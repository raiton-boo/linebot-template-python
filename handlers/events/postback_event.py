import logging
from linebot.v3.messaging import AsyncMessagingApi, ReplyMessageRequest, TextMessage
from linebot.v3.webhooks import PostbackEvent

logger = logging.getLogger(__name__)


class PostbackEventHandler:
    def __init__(self, api: AsyncMessagingApi):
        self.api = api

    async def handle(self, event: PostbackEvent) -> None:
        try:
            postback_data = event.postback.data
            logger.info(f"Postback received: {postback_data}")
        except Exception as e:
            logger.error(f"PostbackEventHandler error: {e}")


def get_handlers(api: AsyncMessagingApi):
    postback_handler = PostbackEventHandler(api)
    return {PostbackEvent: postback_handler.handle}
