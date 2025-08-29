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
    AccountLinkEventHandler,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

REQUIRED_ENV_VARS = ["CHANNEL_SECRET", "CHANNEL_ACCESS_TOKEN"]
CRITICAL_ERROR_KEYWORDS = {"rate", "limit", "timeout", "server", "quota"}
LARGE_EVENT_THRESHOLD = 5
SLOW_PROCESSING_THRESHOLD = 1.0


def validate_environment() -> Tuple[str, str]:
    """環境変数の検証"""
    env_values = {var: os.getenv(var) for var in REQUIRED_ENV_VARS}
    missing_vars = [var for var, val in env_values.items() if not val]

    if missing_vars:
        logger.error(f"Missing environment variables: {', '.join(missing_vars)}")
        sys.exit(1)

    return env_values["CHANNEL_SECRET"], env_values["CHANNEL_ACCESS_TOKEN"]


channel_secret, channel_access_token = validate_environment()

configuration = Configuration(access_token=channel_access_token)
async_api_client = AsyncApiClient(configuration)
line_bot_api = AsyncMessagingApi(async_api_client)
parser = WebhookParser(channel_secret)

app = FastAPI(
    title="LINE Bot Template",
    description="高性能非同期処理対応のLINE Botテンプレート",
    version="2.0.0",
    docs_url=None,
    redoc_url=None,
)


def create_event_handler_map(
    api: AsyncMessagingApi,
) -> Dict[Type[Any], BaseEventHandler]:
    """イベントハンドラマッピングを生成"""
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
        AccountLinkEvent: AccountLinkEventHandler(api),
    }

    logger.info(f"Handler mapping created: {len(active_handlers)} event types supported")
    return active_handlers


event_handler_map = create_event_handler_map(line_bot_api)


@app.on_event("startup")
async def startup_event():
    logger.info("LINE Bot server started")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("LINE Bot server stopped")


@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """ヘルスチェック"""
    return {"status": "healthy", "handlers": len(event_handler_map), "message": "OK"}


@app.post("/callback")
async def webhook_callback(request: Request):
    """
    LINE Webhookコールバック処理

    署名検証後、即座にレスポンスを返しバックグラウンドでイベント処理を実行
    """
    signature = request.headers.get("X-Line-Signature")
    body = (await request.body()).decode()

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

    if events:
        # バックグラウンドでイベント処理を開始（レスポンス速度優先）
        asyncio.create_task(_process_events_background(events))

    return {"message": "ok"}


async def _process_events_background(events: List[Any]) -> None:
    """
    イベントのバックグラウンド並行処理

    複数イベントを同時処理し、パフォーマンス監視も行う
    """
    start_time = time.time()
    event_count = len(events)

    if event_count > LARGE_EVENT_THRESHOLD:
        logger.info(f"大量イベント処理開始: {event_count}件")

    # 全イベントを並行処理
    tasks = [_handle_single_event(event) for event in events]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # 処理結果の集計
    error_count = sum(1 for result in results if isinstance(result, Exception))
    success_count = event_count - error_count

    if error_count > 0:
        logger.info(f"処理完了 - 成功: {success_count} / エラー: {error_count}")

    # パフォーマンス監視
    processing_time = time.time() - start_time
    if processing_time > SLOW_PROCESSING_THRESHOLD:
        logger.warning(f"処理時間超過: {processing_time:.2f}秒")


async def _handle_single_event(event: Any) -> None:
    """単一イベント処理"""
    event_type = type(event)
    handler = event_handler_map.get(event_type)

    if not handler:
        logger.warning(f"Unsupported event type: {event_type.__name__}")
        return

    try:
        await handler.safe_handle(event)
    except Exception as error:
        await _handle_processing_error(error, event_type)


async def _handle_processing_error(error: Exception, event_type: Type) -> None:
    """
    エラーハンドリング

    重要度に応じて適切なログレベルで出力する
    """
    error_message_words = set(str(error).lower().split())
    error_type_name = type(error).__name__

    # レート制限やタイムアウトなどの重要エラーかチェック
    is_critical_error = bool(CRITICAL_ERROR_KEYWORDS & error_message_words)

    if is_critical_error:
        await _analyze_critical_error(error, event_type, error_type_name)
    else:
        logger.error(f"{event_type.__name__} processing error: {error_type_name}")


async def _analyze_critical_error(
    error: Exception, event_type: Type, error_type_name: str
) -> None:
    """重要エラーの詳細解析とログ出力"""
    try:
        analyzer = AsyncLineErrorAnalyzer()
        analysis_result = await analyzer.analyze(error)
        logger.warning(
            f"{event_type.__name__} critical error: {analysis_result.category} "
            f"How to deal: {analysis_result.recommended_action[:50]}..."
        )
    except Exception:
        # エラー解析が失敗した場合のフォールバック
        logger.error(f"{event_type.__name__} critical error: {error_type_name}")


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
