import logging
from linebot.v3.messaging import AsyncMessagingApi
from linebot.v3.webhooks import UnsendEvent

logger = logging.getLogger(__name__)


class UnsendEventHandler:
    def __init__(self, api: AsyncMessagingApi):
        self.api = api

    async def handle(self, event: UnsendEvent) -> None:
        try:
            unsend = event.unsend
            message_id = unsend.message_id
            logger.info(f"Message unsent: {message_id}")
        except Exception as e:
            logger.error(f"UnsendEventHandler error: {e}")


def get_handlers(api: AsyncMessagingApi):
    unsend_handler = UnsendEventHandler(api)
    return {UnsendEvent: unsend_handler.handle}
