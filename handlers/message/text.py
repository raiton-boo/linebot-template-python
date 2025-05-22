from linebot.v3.webhooks import MessageEvent, MessageContent
from linebot.v3.messaging import ReplyMessageRequest, TextMessage, Sender
from .base import BaseMessageHandler

from utils.fetcher.user import UserProfileManager

class TextMessageHandler(BaseMessageHandler):
    async def handle(self, event: MessageEvent):
        try:
            if not isinstance(event.message, MessageContent):
                return
            user_id = event.source.user_id
            user_profile = await UserProfileManager.fetch(
                self.line_bot_api, user_id=user_id
            )
            display_name = user_profile.get_display_name() if user_profile else "友だち追加してね！！"
            icon_url = user_profile.get_picture_url() if user_profile else "https://placehold.jp/150x150.png"

            await self.line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[
                        TextMessage(
                            # これ、有料絵文字送るとその絵文字のメッセージが返ってくる。テキストメッセージ扱いなのおもしろい
                            text=event.message.text,
                            sender=Sender(
                                name=display_name,
                                icon_url=icon_url,
                            ),
                            quoteToken=event.message.quote_token,
                        )
                    ],
                )
            )
        except Exception as e:
            await self.logger.error(
                f"TextMessageContentの処理中にエラーが発生しました:\n{e}"
            )
            raise