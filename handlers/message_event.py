from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    StickerMessageContent,
    ImageMessageContent,
    AudioMessageContent,
    VideoMessageContent,
    LocationMessageContent,
)
from handlers.message import (
    BaseMessageHandler,
    StickerMessageHandler,
    TextMessageHandler,
    ImageMessageHandler,
    AudioMessageHandler,
    VideoMessageHandler,
    LocationMessageHandler,
)
from utils.log.log import LogManager


class MessageEventHandler(BaseMessageHandler):
    def __init__(self, line_bot_api):
        super().__init__(line_bot_api)
        self.logger = LogManager()
        # メッセージタイプごとのハンドラをマッピング
        self.handler_map = {
            TextMessageContent: TextMessageHandler(line_bot_api),
            StickerMessageContent: StickerMessageHandler(line_bot_api),
            ImageMessageContent: ImageMessageHandler(line_bot_api),
            AudioMessageContent: AudioMessageHandler(line_bot_api),
            VideoMessageContent: VideoMessageHandler(line_bot_api),
            LocationMessageContent: LocationMessageHandler(line_bot_api),
        }

    async def handle(self, event: MessageEvent):
        try:
            for message_type, handler in self.handler_map.items():
                if isinstance(event.message, message_type):
                    await handler.handle(event)
                    return
            await self.logger.info(
                f"未対応のメッセージタイプを受信したため無視しました\n"
                f"{event}"
            )
        except Exception as e:
            await self.logger.error(f"MessageEventの処理中にエラーが発生しました:\n{e}")
