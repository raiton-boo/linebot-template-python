import os
import sys
import logging
import asyncio
import time
from typing import Optional, Dict, Type, Any, List, Tuple

import uvicorn
from fastapi import Request, FastAPI, HTTPException, status
from linebot.v3.webhook import WebhookParser
from linebot.v3.messaging import (
    AsyncApiClient,
    AsyncMessagingApi,
    Configuration,
)
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.webhooks import (
    MessageEvent,
    UnsendEvent,
    FollowEvent,
    UnfollowEvent,
    JoinEvent,
    LeaveEvent,
    MemberJoinedEvent,
    MemberLeftEvent,
    PostbackEvent,
    BeaconEvent,
    VideoPlayCompleteEvent,
    ThingsEvent,
    AccountLinkEvent,
)

from linebot_error_analyzer import AsyncLineErrorAnalyzer
from handlers.base_handler import BaseEventHandler
from handlers import (
    BeaconEventHandler,
    FollowEventHandler,
    JoinEventHandler,
    LeaveEventHandler,
    MemberJoinedEventHandler,
    MemberLeftEventHandler,
    MessageEventHandler,
    PostbackEventHandler,
    UnfollowEventHandler,
    UnsendEventHandler,
    VideoPlayCompleteEventHandler,
    ThingsEventHandler,
    AccountLinkEventHandler,
)

# ==== ログ設定 ====
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==== 定数定義 ====
REQUIRED_ENV_VARS = ["CHANNEL_SECRET", "CHANNEL_ACCESS_TOKEN"]
CRITICAL_ERROR_KEYWORDS = {"rate", "limit", "timeout", "server", "quota"}
LARGE_EVENT_THRESHOLD = 5
SLOW_PROCESSING_THRESHOLD = 1.0


# ==== 環境変数の取得 ====
def validate_environment() -> Tuple[str, str]:
    """
    必須環境変数の検証と取得

    Returns:
        Tuple[str, str]: (channel_secret, channel_access_token)

    Raises:
        SystemExit: 必須環境変数が不足している場合
    """
    env_values = {var: os.getenv(var) for var in REQUIRED_ENV_VARS}
    missing_vars = [var for var, val in env_values.items() if not val]

    if missing_vars:
        logger.error(f"環境変数が不足: {', '.join(missing_vars)}")
        sys.exit(1)

    return env_values["CHANNEL_SECRET"], env_values["CHANNEL_ACCESS_TOKEN"]


# 環境変数取得
channel_secret, channel_access_token = validate_environment()

# ==== LINE API 設定 ====
configuration = Configuration(access_token=channel_access_token)
async_api_client = AsyncApiClient(configuration)
line_bot_api = AsyncMessagingApi(async_api_client)
parser = WebhookParser(channel_secret)

# ==== アプリケーション初期化 ====
app = FastAPI(
    title="LINE Bot Template",
    description="高性能非同期処理対応のLINE Botテンプレート",
    version="2.0.0",
    docs_url=None,  # 本番環境では無効化
    redoc_url=None,  # 本番環境では無効化
)


# ==== ハンドラ初期化とマッピング ====
def create_event_handler_map(
    api: AsyncMessagingApi,
) -> Dict[Type[Any], BaseEventHandler]:
    """
    イベントハンドラマッピングを生成

    O(1)の高速ルーティングを実現するため、辞書構造を使用

    Args:
        api (AsyncMessagingApi): LINE Bot API クライアント

    Returns:
        Dict[Type[Any], BaseEventHandler]: イベントタイプ -> ハンドラのマッピング
    """
    # アクティブなハンドラのみマッピング（メモリ効率化）
    active_handlers = {
        MessageEvent: MessageEventHandler(api),
        UnsendEvent: UnsendEventHandler(api),
        FollowEvent: FollowEventHandler(api),
        UnfollowEvent: UnfollowEventHandler(api),
        JoinEvent: JoinEventHandler(api),
        LeaveEvent: LeaveEventHandler(api),
        MemberJoinedEvent: MemberJoinedEventHandler(api),
        MemberLeftEvent: MemberLeftEventHandler(api),
        PostbackEvent: PostbackEventHandler(api),
        BeaconEvent: BeaconEventHandler(api),
        VideoPlayCompleteEvent: VideoPlayCompleteEventHandler(api),
        ThingsEvent: ThingsEventHandler(api),
        AccountLinkEvent: AccountLinkEventHandler(api),
    }

    logger.info(f"ハンドラマッピング作成完了: {len(active_handlers)}種類のイベント対応")
    return active_handlers


# グローバルハンドラマッピング（起動時に一度だけ作成）
event_handler_map = create_event_handler_map(line_bot_api)


# ==== アプリケーションライフサイクル ====
@app.on_event("startup")
async def startup_event():
    logger.info("LINE Bot サーバー起動完了")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("LINE Bot サーバー終了")


# ==== エンドポイント ====
@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """
    ヘルスチェックエンドポイント

    Returns:
        dict: サーバー状態
    """
    return {"status": "healthy", "handlers": len(event_handler_map), "message": "OK"}


@app.post("/callback")
async def webhook_callback(request: Request):
    """
    LINE Webhook コールバック処理

    署名検証後、即座に200レスポンスを返却し、
    バックグラウンドでイベント処理を実行する高速処理方式を採用

    Args:
        request (Request): FastAPIリクエストオブジェクト

    Returns:
        dict: 処理状態

    Raises:
        HTTPException: 署名エラー(400) または内部エラー(500)
    """
    # リクエスト解析
    signature = request.headers.get("X-Line-Signature")
    body = (await request.body()).decode()

    # 署名検証
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        logger.warning("署名検証失敗: Channel Secretを確認してください")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signature"
        )
    except Exception as e:
        logger.error(f"Webhook解析エラー: {type(e).__name__}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
    # バックグラウンド処理開始（レスポンス速度最優先）
    if events:
        # デバッグ: 受信イベントタイプをログ出力
        event_types = [type(event).__name__ for event in events]
        logger.info(f"受信イベント: {event_types}")
        asyncio.create_task(_process_events_background(events))

    return {"message": "ok"}


# ==== バックグラウンド処理 ====
async def _process_events_background(events: List[Any]) -> None:
    """
    イベントバックグラウンド処理

    並行処理（asyncio.gather）により高速処理を実現

    Args:
        events (List[Any]): 処理対象イベントリスト
    """
    start_time = time.time()
    event_count = len(events)

    # 大量イベント検知（パフォーマンス監視）
    if event_count > LARGE_EVENT_THRESHOLD:
        logger.info(f"大量イベント処理開始: {event_count}件")

    # 並行処理実行
    tasks = [_handle_single_event(event) for event in events]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # 結果統計（ワンパス集計）
    error_count = sum(1 for result in results if isinstance(result, Exception))
    success_count = event_count - error_count

    # 結果ログ出力（エラー時のみ）
    if error_count > 0:
        logger.info(f"処理完了 - 成功: {success_count} / エラー: {error_count}")

    # パフォーマンス監視
    processing_time = time.time() - start_time
    if processing_time > SLOW_PROCESSING_THRESHOLD:
        logger.warning(f"処理時間超過: {processing_time:.2f}秒")


async def _handle_single_event(event: Any) -> None:
    """
    単一イベント処理

    Args:
        event (Any): 処理対象イベント
    """
    event_type = type(event)
    handler = event_handler_map.get(event_type)  # 辞書検索

    if not handler:
        logger.warning(
            f"未対応イベントタイプ: {event_type.__name__} - 利用可能なハンドラ: {list(event_handler_map.keys())}"
        )
        return

    try:
        await handler.handle(event)
    except Exception as error:
        await _handle_processing_error(error, event_type)


async def _handle_processing_error(error: Exception, event_type: Type) -> None:
    """
    イベント処理エラーハンドリング

    アルゴリズム最適化：set intersection による高速キーワード検索

    Args:
        error (Exception): 発生したエラー
        event_type (Type): イベントタイプ
    """
    error_message_words = set(str(error).lower().split())  # set化で高速検索
    error_type_name = type(error).__name__

    # 重要エラー判定（アルゴリズム最適化：set intersection - O(min(m,n))）
    is_critical_error = bool(CRITICAL_ERROR_KEYWORDS & error_message_words)

    if is_critical_error:
        # 重要エラーは詳細解析
        await _analyze_critical_error(error, event_type, error_type_name)
    else:
        # 通常エラーは簡潔ログ
        logger.error(f"{event_type.__name__}処理エラー: {error_type_name}")


async def _analyze_critical_error(
    error: Exception, event_type: Type, error_type_name: str
) -> None:
    """
    重要エラーの詳細解析

    Args:
        error (Exception): エラーオブジェクト
        event_type (Type): イベントタイプ
        error_type_name (str): エラータイプ名
    """
    try:
        analyzer = AsyncLineErrorAnalyzer()
        analysis_result = await analyzer.analyze(error)
        logger.warning(
            f"{event_type.__name__}重要エラー: {analysis_result.category} "
            f"対処法: {analysis_result.recommended_action[:50]}..."
        )
    except Exception:
        # Analyzer失敗時はフォールバック
        logger.error(f"{event_type.__name__}重要エラー: {error_type_name}")


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
