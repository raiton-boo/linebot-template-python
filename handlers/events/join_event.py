import logging
from linebot.v3.messaging import AsyncMessagingApi, ReplyMessageRequest, TextMessage
from linebot.v3.webhooks import JoinEvent

logger = logging.getLogger(__name__)


class JoinEventHandler:
    def __init__(self, api: AsyncMessagingApi):
        self.api = api

    async def handle(self, event: JoinEvent) -> None:
        try:
            source = event.source
            logger.info(
                f"Joined to {source.type}: {source.group_id if hasattr(source, 'group_id') else source.room_id}"
            )

            greeting_message = (
                "こんにちは！",
                "招待していただきありがとうございます！",
            )

            await self.api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=greeting_message)],
                )
            )
        except Exception as e:
            logger.error(f"JoinEventHandler error: {e}")


def get_handlers(api: AsyncMessagingApi):
    join_handler = JoinEventHandler(api)
    return {JoinEvent: join_handler.handle}
