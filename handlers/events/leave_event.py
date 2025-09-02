import logging
from linebot.v3.messaging import AsyncMessagingApi
from linebot.v3.webhooks import LeaveEvent

logger = logging.getLogger(__name__)


class LeaveEventHandler:
    def __init__(self, api: AsyncMessagingApi):
        self.api = api

    async def handle(self, event: LeaveEvent) -> None:
        try:
            source = event.source
            logger.info(
                f"Left from {source.type}: {source.group_id if hasattr(source, 'group_id') else source.room_id}"
            )
        except Exception as e:
            logger.error(f"LeaveEventHandler error: {e}")


def get_handlers(api: AsyncMessagingApi):
    leave_handler = LeaveEventHandler(api)
    return {LeaveEvent: leave_handler.handle}
