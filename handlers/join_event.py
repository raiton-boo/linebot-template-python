from linebot.v3.messaging import AsyncMessagingApi, ReplyMessageRequest, TextMessage
from linebot.v3.webhooks import JoinEvent


async def handle_join_event(event: JoinEvent, line_bot_api: AsyncMessagingApi):
    """ジョインイベントを処理"""
    await line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage(text="グループに招待してくれてありがとう！")],
        )
    )