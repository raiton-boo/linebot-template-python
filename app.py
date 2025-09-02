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

from handlers.events import AVAILABLE_HANDLERS

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# システム設定の定数
REQUIRED_ENV_VARS = ["CHANNEL_SECRET", "CHANNEL_ACCESS_TOKEN"]
CRITICAL_ERROR_KEYWORDS = {"rate", "limit", "timeout", "server", "quota"}
LARGE_EVENT_THRESHOLD = 5  # 大量イベント判定の閾値
SLOW_PROCESSING_THRESHOLD = 1.0  # 処理遅延警告の閾値（秒）


def validate_environment() -> Tuple[str, str]:
    """起動時に必要な環境変数をチェック"""
    env_values = {var: os.getenv(var) for var in REQUIRED_ENV_VARS}
    missing_vars = [var for var, val in env_values.items() if not val]

    if missing_vars:
        logger.error(f"Missing environment variables: {', '.join(missing_vars)}")
        sys.exit(1)

    return env_values["CHANNEL_SECRET"], env_values["CHANNEL_ACCESS_TOKEN"]


# 起動時の環境変数チェック
channel_secret, channel_access_token = validate_environment()

# LINE Bot API の初期化
configuration = Configuration(access_token=channel_access_token)
async_api_client = AsyncApiClient(configuration)
line_bot_api = AsyncMessagingApi(async_api_client)
parser = WebhookParser(channel_secret)

# FastAPI アプリケーションの初期化
app = FastAPI(
    title="LINE Bot Template",
    description="LINE Bot Template with Async Event Handlers",
    docs_url=None,  # Swagger UIを無効化
    redoc_url=None,  # ReDocを無効化
)

# イベントハンドラーの格納辞書
event_handlers = {}


def register_all_event_handlers():
    """各モジュールからイベントハンドラーを収集して登録"""
    for handler_module in AVAILABLE_HANDLERS:
        module_name = handler_module.__name__
        logger.debug(f"Checking module: {module_name}")

        if hasattr(handler_module, "get_handlers"):
            try:
                handlers = handler_module.get_handlers(line_bot_api)
                event_handlers.update(handlers)

            except Exception as e:
                logger.error(
                    f"Error registering {module_name}: {type(e).__name__}: {e}"
                )
        else:
            logger.warning(f"{module_name}: No get_handlers function")

    logger.info(f"Total registered event types: {len(event_handlers)}")

    # ハンドラーが登録されていない場合の警告
    if not event_handlers:
        logger.warning("No event handlers registered!")


# 起動時にハンドラーを登録
register_all_event_handlers()

# アプリケーションの統計情報を保持
event_stats = {
    "total_requests": 0,
    "successful_requests": 0,
    "failed_requests": 0,
    "total_events": 0,
    "processed_events": 0,
    "failed_events": 0,
    "processing_times": [],
    "event_type_counts": {},
    "last_event_time": None,
}


@app.on_event("startup")
async def startup_event():
    """アプリケーション起動時の初期化処理"""
    handler_count = len(AVAILABLE_HANDLERS)
    registered_events = len(event_handlers)
    handler_names = [module.__name__.split(".")[-1] for module in AVAILABLE_HANDLERS]

    # 起動ログの出力
    logger.info("=" * 60)
    logger.info("🚀 LINE Bot Template - Server Starting")
    logger.info("=" * 60)
    logger.info(f"Handler Modules: {handler_count}")
    logger.info(f"Registered Event Types: {registered_events}")
    logger.info(f"Parser: {parser.__class__.__name__}")
    logger.info(f"API: {line_bot_api.__class__.__name__}")
    logger.info("=" * 60)

    # デバッグモードで詳細情報を出力
    for event_type in event_handlers.keys():
        logger.debug(f"{event_type.__name__} handler registered")


@app.on_event("shutdown")
async def shutdown_event():
    """アプリケーション終了時のクリーンアップ処理"""
    try:
        # APIクライアントを適切に閉じる
        await async_api_client.close()

        # 統計情報の計算
        total_requests = event_stats["total_requests"]
        total_events = event_stats["total_events"]
        success_rate = (
            (event_stats["processed_events"] / total_events * 100)
            if total_events > 0
            else 0
        )

        # 終了ログと統計情報の出力
        logger.info("=" * 60)
        logger.info("LINE Bot Template - Server Shutting Down")
        logger.info("=" * 60)
        logger.info(f"Total Requests: {total_requests:,}")
        logger.info(f"Total Events: {total_events:,}")
        logger.info(f"Success Rate: {success_rate:.1f}%")

        # イベントタイプ別の統計を出力
        if event_stats["event_type_counts"]:
            logger.info("📋Event Type Statistics:")
            for event_type, count in event_stats["event_type_counts"].items():
                logger.info(f"   • {event_type}: {count:,}")

        logger.info("=" * 60)
        logger.info("Server stopped successfully")

    except Exception as e:
        logger.error(f"Shutdown error: {e}")


@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """基本的なヘルスチェック"""
    handler_names = [module.__name__.split(".")[-1] for module in AVAILABLE_HANDLERS]

    # 平均処理時間を計算
    avg_processing_time = (
        sum(event_stats["processing_times"]) / len(event_stats["processing_times"])
        if event_stats["processing_times"]
        else 0
    )

    # 成功率を計算
    success_rate = (
        (event_stats["processed_events"] / event_stats["total_events"] * 100)
        if event_stats["total_events"] > 0
        else 100
    )

    return {
        "status": "healthy",
        "architecture": "async_event_handlers",
        "registered_modules": len(AVAILABLE_HANDLERS),
        "registered_event_types": len(event_handlers),
        "handler_modules": handler_names,
        "stats": {
            "total_requests": event_stats["total_requests"],
            "successful_requests": event_stats["successful_requests"],
            "failed_requests": event_stats["failed_requests"],
            "total_events": event_stats["total_events"],
            "processed_events": event_stats["processed_events"],
            "failed_events": event_stats["failed_events"],
            "success_rate_percent": round(success_rate, 2),
            "avg_processing_time_ms": round(avg_processing_time * 1000, 2),
        },
        "uptime": {
            "last_event_time": event_stats["last_event_time"],
        },
        "message": "OK",
    }


@app.get("/health/detail")
async def health_check_detail():
    """詳細なシステム情報を含むヘルスチェック"""
    # ハンドラーモジュールの詳細情報を収集
    handler_details = []
    for module in AVAILABLE_HANDLERS:
        module_name = module.__name__.split(".")[-1]
        has_get_handlers = hasattr(module, "get_handlers")
        handler_details.append(
            {
                "module": module_name,
                "has_get_handlers_function": has_get_handlers,
                "full_module_name": module.__name__,
            }
        )

    # 登録済みイベントの詳細情報を収集
    registered_events = {}
    for event_type, handler_func in event_handlers.items():
        registered_events[event_type.__name__] = {
            "handler_function": handler_func.__name__,
            "event_count": event_stats["event_type_counts"].get(event_type.__name__, 0),
        }

    return {
        "status": "healthy",
        "architecture": "async_event_handlers",
        "system_info": {
            "total_handler_modules": len(AVAILABLE_HANDLERS),
            "registered_event_types": len(event_handlers),
            "parser_class": parser.__class__.__name__,
            "api_class": line_bot_api.__class__.__name__,
            "channel_secret_configured": bool(channel_secret),
            "channel_access_token_configured": bool(channel_access_token),
        },
        "handler_details": handler_details,
        "registered_events": registered_events,
        "detailed_stats": {
            **event_stats,
            "processing_times_sample": event_stats["processing_times"][
                -10:
            ],  # 最新10件
        },
        "message": "Detailed health check completed",
    }


@app.get("/health/events")
async def health_check_events():
    """イベント処理に関する統計情報"""
    return {
        "event_statistics": event_stats["event_type_counts"],
        "total_events": event_stats["total_events"],
        "registered_event_types": [
            event_type.__name__ for event_type in event_handlers.keys()
        ],
        "last_event_time": event_stats["last_event_time"],
    }


@app.post("/callback")
async def webhook_callback(request: Request):
    """LINE からの Webhook を受信・処理するエンドポイント"""
    signature = request.headers.get("X-Line-Signature")
    body = await request.body()
    body_str = body.decode("utf-8")

    # リクエスト統計を更新
    event_stats["total_requests"] += 1
    start_time = time.time()

    try:
        # Webhook の署名を検証してイベントをパース
        events = parser.parse(body_str, signature)

        if events:
            # イベントがある場合はバックグラウンドで処理
            asyncio.create_task(_handle_events_background(events, start_time))
            event_stats["last_event_time"] = time.strftime("%Y-%m-%d %H:%M:%S")
        else:
            # イベントがない場合も成功とカウント
            event_stats["successful_requests"] += 1

        # LINEへの即座のレスポンス
        return {"message": "ok"}

    except InvalidSignatureError:
        # 署名検証エラー（設定ミスの可能性が高い）
        event_stats["failed_requests"] += 1
        logger.warning("Signature verification failed: Check CHANNEL_SECRET")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signature"
        )
    except Exception as e:
        # その他の予期しないエラー
        event_stats["failed_requests"] += 1
        logger.error(f"Webhook parsing error: {type(e).__name__}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


async def _handle_events_background(events: List[Any], start_time: float) -> None:
    """受信したイベントをバックグラウンドで並列処理"""
    event_count = len(events)
    event_stats["total_events"] += event_count

    # イベントタイプ別の統計を更新
    for event in events:
        event_type_name = type(event).__name__
        event_stats["event_type_counts"][event_type_name] = (
            event_stats["event_type_counts"].get(event_type_name, 0) + 1
        )

    # 大量イベントの場合はログ出力
    if event_count > LARGE_EVENT_THRESHOLD:
        logger.info(f"Processing large event batch: {event_count} events")

    try:
        # 全イベントを並列で処理
        tasks = [_handle_single_event(event) for event in events]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 結果を集計
        error_count = sum(1 for result in results if isinstance(result, Exception))
        success_count = event_count - error_count

        # 統計を更新
        event_stats["processed_events"] += success_count
        event_stats["failed_events"] += error_count
        event_stats["successful_requests"] += 1

        # エラーがあった場合の詳細ログ
        if error_count > 0:
            logger.warning(
                f"Processing completed - Success: {success_count}, Errors: {error_count}"
            )
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    event_type = type(events[i]).__name__
                    logger.error(
                        f"   • {event_type} error: {type(result).__name__}: {result}"
                    )
        elif event_count > 1:
            # 複数イベントが全て成功した場合
            logger.info(f"All events processed successfully: {success_count}")

        # 処理時間の記録と分析
        processing_time = time.time() - start_time
        event_stats["processing_times"].append(processing_time)

        # 処理時間履歴を100件に制限
        if len(event_stats["processing_times"]) > 100:
            event_stats["processing_times"] = event_stats["processing_times"][-100:]

        # パフォーマンス監視
        if processing_time > SLOW_PROCESSING_THRESHOLD:
            logger.warning(
                f"Slow processing detected: {processing_time:.2f}s ({event_count} events)"
            )
        elif event_count > 3:
            logger.info(f"⚡ Events processed: {event_count} in {processing_time:.3f}s")

    except Exception as e:
        # バックグラウンド処理全体でエラーが発生
        event_stats["failed_requests"] += 1
        event_stats["failed_events"] += event_count
        logger.error(f"Background processing error: {type(e).__name__}: {e}")


async def _handle_single_event(event: Any) -> None:
    """個々のイベントを適切なハンドラーで処理"""
    try:
        event_type = type(event)
        event_type_name = event_type.__name__

        # 対応するハンドラーが存在するかチェック
        if event_type in event_handlers:
            handler_func = event_handlers[event_type]
            await handler_func(event)
            logger.debug(f"{event_type_name} processed successfully")
        else:
            # 未対応のイベントタイプの場合
            logger.warning(f"No handler for {event_type_name}")
            logger.info(f"Consider adding handler for {event_type_name}")

    except Exception as e:
        # イベント処理でエラーが発生
        await _handle_processing_error(e, type(event))
        raise e  # エラーを上位に伝播


async def _handle_processing_error(error: Exception, event_type: Type) -> None:
    """イベント処理エラーを分析してログ出力"""
    error_message_words = set(str(error).lower().split())
    error_type_name = type(error).__name__
    event_type_name = event_type.__name__

    # 重要度の高いエラーキーワードをチェック
    is_critical_error = bool(CRITICAL_ERROR_KEYWORDS & error_message_words)

    if is_critical_error:
        # API制限やサーバーエラーなどの重要なエラー
        logger.error(f"{event_type_name} CRITICAL ERROR: {error_type_name} - {error}")
    else:
        # 通常のエラー（詳細はデバッグレベルで出力）
        logger.warning(f"{event_type_name} processing error: {error_type_name}")
        logger.debug(f"Error details: {error}")


# デバッグモードの設定
if os.getenv("DEBUG", "false").lower() == "true":
    logging.getLogger().setLevel(logging.DEBUG)
    logger.info("Debug mode enabled")


# 直接実行時のサーバー起動
if __name__ == "__main__":
    logger.info(f"Python version: {sys.version}")
    logger.info(f"FastAPI starting on http://0.0.0.0:8000")
    logger.info(f"Health check: http://0.0.0.0:8000/health")

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
