from linebot.v3.webhooks import UnsendEvent
from utils.log.log import LogManager


class UnsendEventHandler:
    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api
        self.logger = LogManager()

    async def handle(self, event: UnsendEvent):
        try:
            print(event)
            message_id = event.unsend.message_id
            await self.logger.info(
                f"メッセージが取り消されました:\n"
                f" - ユーザーID: {event.source.user_id}\n"
                f" - メッセージID: {message_id}"
            )
        except Exception as e:
            await self.logger.error(
                f"UnsendEventの処理中にエラーが発生しました:\n{e}"
            )
