from linebot.v3.webhooks import MessageEvent, StickerMessageContent
from linebot.v3.messaging import ReplyMessageRequest, TextMessage
from .base import BaseMessageHandler


class StickerMessageHandler(BaseMessageHandler):
    async def handle(self, event: MessageEvent):
        try:
            if not isinstance(event.message, StickerMessageContent):
                return
            sticker_id = event.message.sticker_id
            package_id = event.message.package_id

            await self.line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[
                        TextMessage(
                            text=f"スタンプを受信しました！\nスタンプID: {sticker_id}\nパッケージID: {package_id}",
                        )
                    ],
                )
            )
        except Exception as e:
            await self.logger.error(
                f"StickerMessageContentの処理中にエラーが発生しました:\n{e}"
            )
            raise
