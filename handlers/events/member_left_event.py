import logging
from linebot.v3.messaging import AsyncMessagingApi, ReplyMessageRequest, TextMessage
from linebot.v3.webhooks import MemberLeftEvent

logger = logging.getLogger(__name__)


class MemberLeftEventHandler:

    def __init__(self, api: AsyncMessagingApi):
        self.api = api

    async def handle(self, event: MemberLeftEvent) -> None:
        try:
            left_members = event.left.members
            member_count = len(left_members)
            logger.info(f"{member_count} member(s) left")

            # メンバー退出イベントにreply_tokenがないため、メッセージ送信ができない

        except Exception as e:
            logger.error(f"MemberLeftEven　tHandler error: {e}")


def get_handlers(api: AsyncMessagingApi):
    member_left_handler = MemberLeftEventHandler(api)

    return {MemberLeftEvent: member_left_handler.handle}
