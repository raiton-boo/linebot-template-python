from linebot.v3.webhooks import MessageEvent, ImageMessageContent
from .base import BaseMessageHandler


class ImageMessageHandler(BaseMessageHandler):
    async def handle(self, event: MessageEvent):
        try:
            if not isinstance(event.message, ImageMessageContent):
                return
        except Exception as e:
            await self.logger.error(
                f"ImageMessageContentの処理中にエラーが発生しました:\n{e}"
            )
            raise