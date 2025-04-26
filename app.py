import os
import sys
import dotenv
dotenv.load_dotenv()

import uvicorn # pipreqsで読み込ませるために置いてる
from fastapi import Request, FastAPI, HTTPException
from linebot.v3.webhook import WebhookParser
from linebot.v3.messaging import (
    AsyncApiClient,
    AsyncMessagingApi,
    Configuration,
)
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.webhooks import MessageEvent, FollowEvent, JoinEvent, UnsendEvent

from handlers.message_event import handle_message_event
from handlers.follow_event import handle_follow_event
from handlers.join_event import handle_join_event

from logs.log import LogManager as log
log = log()

# 環境変数からLINEチャンネルのシークレットとアクセストークンを取得
channel_secret = os.getenv("LINE_CHANNEL_SECRET")
channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

if not channel_secret:
    print("Specify LINE_CHANNEL_SECRET as environment variable.")
    sys.exit()

if not channel_access_token:
    print("Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.")
    sys.exit()

# LINE Messaging APIの設定
configuration = Configuration(access_token=channel_access_token)

# FastAPIアプリケーションの初期化
app = FastAPI()
async_api_client = AsyncApiClient(configuration)
line_bot_api = AsyncMessagingApi(async_api_client)
parser = WebhookParser(channel_secret)

@app.on_event("startup")
async def startup_event():
    log.info("アプリケーションが起動しました")

@app.post("/callback")
async def handle_callback(request: Request):
    """LINE Webhookのコールバックを処理"""
    signature = request.headers.get("X-Line-Signature")
    body = (await request.body()).decode()

    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        log.error("InvalidSignatureError 署名が無効です")
        raise HTTPException(status_code=400, detail="Invalid signature")

    for event in events:
        if isinstance(event, MessageEvent):
            await handle_message_event(event, line_bot_api)
        elif isinstance(event, FollowEvent):
            await handle_follow_event(event, line_bot_api)
        elif isinstance(event, JoinEvent):
            await handle_join_event(event, line_bot_api)
        elif isinstance(event, UnsendEvent):
            pass

    return "OK"

@app.on_event("shutdown")
async def shutdown_event():
    log.info("アプリケーションがシャットダウンしました")
    await async_api_client.close()