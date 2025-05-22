from linebot.v3.webhooks import UnfollowEvent
from utils.log.log import LogManager


class UnFollowEventHandler:
    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api
        self.logger = LogManager()

    async def handle(self, event: UnfollowEvent):
        try:
            user_id = event.source.user_id
            await self.logger.info(
                f"友だち解除されました:\n"
                f" - ユーザーID: {user_id}"
            )
        except Exception as e:
            await self.logger.error(
                f"UnfollowEventの処理中にエラーが発生しました:\n{e}"
            )
