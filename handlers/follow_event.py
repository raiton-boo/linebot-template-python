from linebot.v3.webhooks import FollowEvent
from linebot.v3.messaging import ReplyMessageRequest, TextMessage
from utils.log.log import LogManager
from utils.fetcher.user import UserProfileManager

class FollowEventHandler:
    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api
        self.logger = LogManager()

    async def handle(self, event: FollowEvent):
        try:
            user_id = event.source.user_id
            user_profile = await UserProfileManager.fetch(self.line_bot_api, user_id)
            name = user_profile.get_display_name() if user_profile else "不明"
            #不明だったらすぐブロックしてんだろうなぁ
            await self.logger.info(
                f"友だち追加されました:\n"
                f" - ユーザーID: {user_id}\n"
                f" - ユーザー名: {name}"
            )
            await self.line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text="フォローありがとうございます！")],
                )
            )
        except Exception as e:
            await self.logger.error(f"FollowEventの処理中にエラーが発生しました:\n{e}")