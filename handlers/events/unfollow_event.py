import logging
from linebot.v3.messaging import AsyncMessagingApi
from linebot.v3.webhooks import UnfollowEvent

logger = logging.getLogger(__name__)


class UnfollowEventHandler:
    def __init__(self, api: AsyncMessagingApi):
        self.api = api

    async def handle(self, event: UnfollowEvent) -> None:
        try:
            user_id = event.source.user_id
            logger.info(f"Unfollowed user: {user_id}")
        except Exception as e:
            logger.error(f"UnfollowEventHandler error: {e}")


def get_handlers(api: AsyncMessagingApi):
    unfollow_handler = UnfollowEventHandler(api)
    return {UnfollowEvent: unfollow_handler.handle}
