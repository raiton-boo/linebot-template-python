import logging
from linebot.v3.messaging import AsyncMessagingApi, ReplyMessageRequest, TextMessage
from linebot.v3.webhooks import FollowEvent

logger = logging.getLogger(__name__)


class FollowEventHandler:
    def __init__(self, api: AsyncMessagingApi):
        self.api = api

    async def handle(self, event: FollowEvent) -> None:
        try:
            user_id = event.source.user_id
            logger.info(f"Following user: {user_id}")

            welcome_message = (
                "フォローありがとうございます！"
            )

            await self.api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=welcome_message)],
                )
            )
        except Exception as e:
            logger.error(f"FollowEventHandler error: {e}")


def get_handlers(api: AsyncMessagingApi):
    follow_handler = FollowEventHandler(api)
    return {FollowEvent: follow_handler.handle}
