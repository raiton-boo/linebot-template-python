from linebot.v3.webhooks import MessageEvent, AudioMessageContent
from .base import BaseMessageHandler


class AudioMessageHandler(BaseMessageHandler):
    async def handle(self, event: MessageEvent):
        try:
            if not isinstance(event.message, AudioMessageContent):
                return
        except Exception as e:
            await self.logger.error(
                f"AudioMessageContentの処理中にエラーが発生しました:\n{e}"
            )
            raise