from linebot.v3.webhooks import MessageEvent, LocationMessageContent
from .base import BaseMessageHandler

class LocationMessageHandler(BaseMessageHandler):
    async def handle(self, event: MessageEvent):
        try:
            if not isinstance(event.message, LocationMessageContent):
                return
            await self.logger.info(
                f"位置情報メッセージを受信しました\n{event.message.address}\n{event.message.latitude}\n{event.message.longitude}"
            )
        except Exception as e:
            await self.logger.error(
                f"LocationMessageContentの処理中にエラーが発生しました:\n{e}"
            )
            raise