from typing import Any, Dict, Optional
from linebot.v3.webhooks import AccountLinkEvent
from linebot.v3.messaging import AsyncMessagingApi, TextMessage, ReplyMessageRequest
from .base_handler import BaseEventHandler


class AccountLinkEventHandler(BaseEventHandler):
    """アカウント連携イベントハンドラ"""

    async def handle(self, event: AccountLinkEvent) -> None:
        """アカウント連携イベントの処理"""
        link_result = event.link.result if event.link else None
        nonce = event.link.nonce if event.link else None

        self.logger.info(f"Get Account link event")

        if link_result == "ok":
            response_message = (
                "アカウント連携が完了しました。\n"
                "外部サービスと連携した機能をご利用いただけます。"
            )
            self.logger.info(f"Account linked successfully: nonce={nonce}")
        else:
            response_message = (
                "アカウント連携に失敗しました。\n" "再度連携をお試しください。"
            )
            self.logger.warning(
                f"Account link failed: result={link_result}, nonce={nonce}"
            )

        await self.line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=response_message)],
            )
        )
