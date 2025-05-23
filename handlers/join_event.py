from linebot.v3.webhooks import JoinEvent
from utils.log.log import LogManager


class JoinEventHandler:
    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api
        self.logger = LogManager()

    async def handle(self, event: JoinEvent):
        print(event)
        try:
            group_id = event.source.group_id
            await self.logger.info(
                f"BOTがグループに参加しました:\n"
                f" - グループID: {group_id}"
            )

        except Exception as e:
            await self.logger.error(f"JoinEventの処理中にエラーが発生しました:\n{e}")
