from linebot.v3.webhooks import MessageEvent, VideoMessageContent
from .base import BaseMessageHandler


class VideoMessageHandler(BaseMessageHandler):
    async def handle(self, event: MessageEvent):
        try:
            if not isinstance(event.message, VideoMessageContent):
                return
        except Exception as e:
            await self.logger.error(
                f"VideoMessageContentの処理中にエラーが発生しました:\n{e}"
            )
            raise
