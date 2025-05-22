from linebot.v3.webhooks import MemberLeftEvent
from utils.log.log import LogManager
from utils.fetcher.user import UserProfileManager

class MemberLeftEventHandler:
    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api
        self.logger = LogManager()

    async def handle(self, event: MemberLeftEvent):
        try:
            group_id = event.source.group_id
            user_ids = [user.user_id for user in event.left.members]
            names = []
            for user_id in user_ids:
                user_profile = await UserProfileManager.fetch(self.line_bot_api, user_id)
                names.append(user_profile.get_display_name() if user_profile else "不明")
            await self.logger.info(
                f"ユーザーがグループから退出しました:\n"
                f" - グループID: {group_id}\n"
                f" - ユーザーID: {', '.join(user_ids)}\n"
                f" - ユーザー名: {', '.join(names)}"
            )
        except Exception as e:
            await self.logger.error(
                f"MemberLeftEventの処理中にエラーが発生しました:\n{e}"
            )