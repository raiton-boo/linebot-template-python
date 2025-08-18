import os
import sys
import logging
import asyncio
import time
from typing import Optional, Dict, Type, Any, List

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
    FollowEvent,
    UnfollowEvent,
    JoinEvent,
    LeaveEvent,
    MemberJoinedEvent,
)
from linebot_error_analyzer import AsyncLineErrorAnalyzer, ErrorCategory

# ハンドラのインポート
from handlers import (
    MessageEventHandler,
    FollowEventHandler,
    UnfollowEventHandler,
    JoinEventHandler,
    LeaveEventHandler,
    MemberJoinedEventHandler,
    BaseEventHandler,
)

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- 環境変数の取得 ---
channel_secret: Optional[str] = os.getenv("LINE_CHANNEL_SECRET")
channel_access_token: Optional[str] = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

# 必須環境変数のチェック（早期終了）
if not channel_secret:
    logger.error("環境変数 LINE_CHANNEL_SECRET が設定されていません")
    sys.exit(1)

if not channel_access_token:
    logger.error("環境変数 LINE_CHANNEL_ACCESS_TOKEN が設定されていません")
    sys.exit(1)

# LINE API 設定
configuration = Configuration(access_token=channel_access_token)

# --- アプリケーション初期化 ---
app = FastAPI(
    title="LINE Bot Template",
    description="非同期処理対応のLINE Botテンプレート",
    version="1.0.0",
    docs_url=None,  # 本番環境でのSwagger UI無効化（セキュリティ向上）
    redoc_url=None,  # ReDoc UI無効化
)

async_api_client = AsyncApiClient(configuration)
line_bot_api = AsyncMessagingApi(async_api_client)
parser = WebhookParser(channel_secret)


# --- ハンドラ初期化とマッピング ---
def create_event_handler_map(
    api: AsyncMessagingApi,
) -> Dict[Type[Any], BaseEventHandler]:
    """
    イベントタイプとハンドラのマッピングを作成
    高速なイベントルーティングを実現します

    Args:
        api (AsyncMessagingApi): LINE Bot API クライアント

    Returns:
        Dict[Type[Any], BaseEventHandler]: イベントタイプ -> ハンドラのマッピング
    """
    return {
        MessageEvent: MessageEventHandler(api),
        FollowEvent: FollowEventHandler(api),
        UnfollowEvent: UnfollowEventHandler(api),
        JoinEvent: JoinEventHandler(api),
        LeaveEvent: LeaveEventHandler(api),
        MemberJoinedEvent: MemberJoinedEventHandler(api),
    }


# イベントハンドラマッピングを作成
event_handler_map = create_event_handler_map(line_bot_api)


@app.on_event("startup")
async def startup_event():
    logger.info("LINE Bot サーバー起動完了")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("LINE Bot サーバー終了")


@app.get("/")
async def root():
    """
    ルートエンドポイント。疎通確認用。

    Returns:
        dict: ウェルカムメッセージ
    """
    return {"message": "Hello, World!"}


@app.get("/health", status_code=status.HTTP_200_OK)
async def health():
    """
    ヘルスチェックエンドポイント。
    サーバーの稼働状況を確認するために使用します。

    Returns:
        dict: ステータスメッセージ
    """
    return {"message": "ok"}


@app.post("/callback")
async def handle_callback(request: Request):
    """
    LINEプラットフォームからのWebhookコールバックを処理するエンドポイント。
    署名検証を行い、ハンドラマッピングを使用して各種イベントを高速処理します。

    Args:
        request (Request): FastAPIのリクエストオブジェクト

    Returns:
        dict: 処理結果

    Raises:
        HTTPException: 署名が無効な場合（400）または内部エラー（500）
    """
    start_time = time.time()  # パフォーマンス測定開始

    signature = request.headers.get("X-Line-Signature")
    body = (await request.body()).decode()

    # 署名検証
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError as sig_error:
        # analyzerで署名エラーの詳細診断（セキュリティ向上）
        try:
            analyzer = AsyncLineErrorAnalyzer()
            analysis_result = await analyzer.analyze(sig_error)
            # 簡潔で有用な情報のみログ出力
            logger.warning(f"署名検証失敗: {analysis_result.recommended_action}")
        except Exception:
            # analyzerが失敗してもフォールバック
            logger.warning("署名検証失敗: チャネルシークレットを確認してください")

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signature"
        )
    except Exception as e:
        logger.error(f"Webhook解析エラー: {type(e).__name__}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )

    # 高速イベント処理（並行処理）
    async def process_single_event(event):
        """単一イベントを処理"""
        event_type = type(event)
        handler = event_handler_map.get(event_type)

        if handler:
            try:
                await handler.handle(event)
            except Exception as e:
                # 重要なエラーのみanalyzerで詳細解析（レスポンス速度を保つ）
                error_type_name = type(e).__name__

                # 特定の重要なエラータイプのみ詳細解析
                if any(
                    keyword in str(e).lower()
                    for keyword in ["rate", "limit", "timeout", "server"]
                ):
                    try:
                        analyzer = AsyncLineErrorAnalyzer()
                        analysis_result = await analyzer.analyze(e)
                        logger.warning(
                            f"{event_type.__name__}重要エラー: {analysis_result.category} "
                            f"| 対処: {analysis_result.recommended_action[:50]}..."
                        )
                    except Exception:
                        logger.error(
                            f"{event_type.__name__}処理失敗: {error_type_name}"
                        )
                else:
                    # 通常エラーは最小限のログ
                    logger.error(f"{event_type.__name__}処理失敗: {error_type_name}")
        else:
            # 未知のイベントタイプ（開発時に有用）
            logger.debug(f"未対応イベント: {event_type.__name__}")

    # 並行処理でイベントを処理（高速化）
    if events:
        event_count = len(events)
        # パフォーマンス監視用の軽量ログ
        if event_count > 5:  # 大量イベント時のみログ
            logger.info(f"大量イベント処理開始: {event_count}件")

        tasks = [process_single_event(event) for event in events]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # エラー統計（邪魔にならない程度）
        error_count = sum(1 for result in results if isinstance(result, Exception))
        if error_count > 0:
            logger.info(
                f"イベント処理完了: 成功{event_count-error_count}件 / エラー{error_count}件"
            )

    # パフォーマンス監視（遅い場合のみログ）
    processing_time = time.time() - start_time
    if processing_time > 1.0:  # 1秒以上かかった場合のみ
        logger.warning(f"Webhook処理時間: {processing_time:.2f}秒 (要最適化)")

    return {"message": "ok"}


if __name__ == "__main__":
    # サーバー起動用（開発・テスト用）
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
