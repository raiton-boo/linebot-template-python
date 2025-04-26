from linebot.v3.messaging import AsyncMessagingApi, ReplyMessageRequest, TextMessage
from linebot.v3.webhooks import FollowEvent


async def handle_follow_event(event: FollowEvent, line_bot_api: AsyncMessagingApi):
    """フォローイベントを処理"""
    await line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage(text="友達追加ありがとう！")],
        )
    )