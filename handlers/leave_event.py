from linebot.v3.webhooks import LeaveEvent
from utils.log.log import LogManager


class LeaveEventHandler:
    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api
        self.logger = LogManager()

    async def handle(self, event: LeaveEvent):
        try:
            group_id = event.source.group_id
            await self.logger.info(
                f"BOTがグループを退出しました:\n"
                f" - グループID: {group_id}"
            )
        except Exception as e:
            await self.logger.error(f"LeaveEventの処理中にエラーが発生しました:\n{e}")
