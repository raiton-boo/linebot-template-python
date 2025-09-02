import logging
from linebot.v3.messaging import AsyncMessagingApi
from linebot.v3.webhooks import MessageEvent

from .messages import (
    TextHandler,
    ImageHandler,
    StickerHandler,
    LocationHandler,
    AudioHandler,
    VideoHandler,
    FileHandler,
)

logger = logging.getLogger(__name__)


class MessageEventHandler:
    def __init__(self, api: AsyncMessagingApi):
        self.api = api

        from linebot.v3.webhooks import (
            TextMessageContent,
            ImageMessageContent,
            StickerMessageContent,
            LocationMessageContent,
            AudioMessageContent,
            VideoMessageContent,
            FileMessageContent,
        )

        # メッセージタイプごとのハンドラーを登録
        self.handlers = {
            TextMessageContent: TextHandler(api),
            ImageMessageContent: ImageHandler(api),
            StickerMessageContent: StickerHandler(api),
            LocationMessageContent: LocationHandler(api),
            AudioMessageContent: AudioHandler(api),
            VideoMessageContent: VideoHandler(api),
            FileMessageContent: FileHandler(api),
        }

    async def handle(self, event: MessageEvent) -> None:
        message_type = type(event.message)

        if message_type in self.handlers:
            handler = self.handlers[message_type]
            await handler.handle(event)
        else:
            logger.warning(f"Unsupported message type: {message_type}")


def get_handlers(api: AsyncMessagingApi):
    message_handler = MessageEventHandler(api)
    return {MessageEvent: message_handler.handle}
