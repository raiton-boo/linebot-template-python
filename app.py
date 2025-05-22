import os
import sys

import uvicorn  # pipreqsに読み込ませるため
from fastapi import Request, FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
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
    JoinEvent,
    UnfollowEvent,
    LeaveEvent,
    MemberJoinedEvent,
    MemberLeftEvent,
)
from handlers import (
    MessageEventHandler,
    UnsendEventHandler,
    FollowEventHandler,
    JoinEventHandler,
    UnFollowEventHandler,
    LeaveEventHandler,
    MemberJoinedEventHandler,
    MemberLeftEventHandler,
)
from utils.Logify.log import LogManager

# --- 環境変数の取得 ---
channel_secret = os.getenv("LINE_CHANNEL_SECRET")
channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

if not channel_secret:
    sys.exit("Specify LINE_CHANNEL_SECRET as environment variable.")

if not channel_access_token:
    sys.exit("Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.")

configuration = Configuration(access_token=channel_access_token)

# --- インスタンス生成 ---
app = FastAPI()
logger = LogManager()
async_api_client = AsyncApiClient(configuration)
line_bot_api = AsyncMessagingApi(async_api_client)
parser = WebhookParser(channel_secret)

# --- handlers設定 ---
message_event_handler = MessageEventHandler(line_bot_api)
unsend_event_handler = UnsendEventHandler(line_bot_api)
follow_event_handler = FollowEventHandler(line_bot_api)
unfollow_event_handler = UnFollowEventHandler(line_bot_api)
join_event_handler = JoinEventHandler(line_bot_api)
leave_event_handler = LeaveEventHandler(line_bot_api)
member_joined_event_handler = MemberJoinedEventHandler(line_bot_api)
member_left_event_handler = MemberLeftEventHandler(line_bot_api)

# --- イベントハンドラのマッピング ---
event_handler_map = {
    MessageEvent: message_event_handler,
    UnsendEvent: unsend_event_handler,
    FollowEvent: follow_event_handler,
    UnfollowEvent: unfollow_event_handler,
    JoinEvent: join_event_handler,
    LeaveEvent: leave_event_handler,
    MemberJoinedEvent: member_joined_event_handler,
    MemberLeftEvent: member_left_event_handler,
}


@app.on_event("startup")
async def startup_event():
    await logger.info("アプリケーションが起動しました")


@app.on_event("shutdown")
async def shutdown_event():
    await logger.info("アプリケーションがシャットダウンしました")


@app.get("/")
async def root():
    """
    ルートエンドポイント。疎通確認用。
    Returns:
        dict: メッセージ
    """
    return {"message": "Hello, World!"}


@app.post("/callback")
async def handle_callback(request: Request):
    """
    LINEプラットフォームからのWebhookコールバックを処理するエンドポイント。

    Args:
        request (Request): FastAPIのリクエストオブジェクト

    Returns:
        str: レスポンスメッセージ
    """
    signature = request.headers.get("X-Line-Signature")
    body = (await request.body()).decode()

    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        await logger.warning("InvalidSignatureError: 署名が無効です")
        raise HTTPException(status_code=400, detail="Invalid signature")
    except Exception as e:
        await logger.error(f"Webhookの処理中にエラー: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

    for event in events:
        try:
            handler = event_handler_map.get(type(event))
            if handler:
                await handler.handle(event)
            else:
                await logger.info(f"未対応イベント受信: {type(event)}")
        except Exception as e:
            await logger.error(f"/callback内でイベント処理中にエラー: {e}")

    return "OK"

if __name__ == "__main__":
    # サーバー起動用（開発・テスト用）
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
