import logging
from linebot.v3.messaging import AsyncMessagingApi, ReplyMessageRequest, TextMessage
from linebot.v3.webhooks import MemberJoinedEvent

logger = logging.getLogger(__name__)


class MemberJoinedEventHandler:

    def __init__(self, api: AsyncMessagingApi):
        self.api = api

    async def handle(self, event: MemberJoinedEvent) -> None:
        try:
            joined_members = event.joined.members
            member_count = len(joined_members)
            logger.info(f"{member_count} member(s) joined")

            if member_count == 1:
                welcome_message = (
                    "新しいメンバーが参加しました！\nよろしくお願いします。"
                )
            else:
                welcome_message = f"{member_count}名の新しいメンバーが参加しました！\nよろしくお願いします。"

            await self.api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=welcome_message)],
                )
            )

        except Exception as e:
            logger.error(f"MemberJoinedEventHandler error: {e}")


def get_handlers(api: AsyncMessagingApi):
    member_joined_handler = MemberJoinedEventHandler(api)
    return {MemberJoinedEvent: member_joined_handler.handle}
