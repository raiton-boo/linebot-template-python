# handlers/events/account_link_event.py
import logging
from linebot.v3.messaging import AsyncMessagingApi, ReplyMessageRequest, TextMessage
from linebot.v3.webhooks import AccountLinkEvent

logger = logging.getLogger(__name__)


class AccountLinkEventHandler:

    def __init__(self, api: AsyncMessagingApi):
        self.api = api

    async def handle(self, event: AccountLinkEvent) -> None:
        try:
            link = event.link
            result = link.result
            nonce = link.nonce

            logger.info(f"Account link event - Result: {result}, Nonce: {nonce}")

            if result == "ok":
                response_text = (
                    "アカウントの連携が完了しました！\n"
                    "これで追加機能をご利用いただけます。"
                )
            else:
                response_text = (
                    "アカウント連携に失敗しました。\n" "もう一度お試しください。"
                )

            await self.api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=response_text)],
                )
            )

        except Exception as e:
            logger.error(f"AccountLinkEventHandler error: {e}")


def get_handlers(api: AsyncMessagingApi):
    account_link_handler = AccountLinkEventHandler(api)
    return {AccountLinkEvent: account_link_handler.handle}
