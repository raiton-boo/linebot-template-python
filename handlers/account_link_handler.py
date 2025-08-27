from typing import Any, Dict, Optional
from linebot.v3.webhooks import AccountLinkEvent
from linebot.v3.messaging import AsyncMessagingApi, TextMessage, ReplyMessageRequest
from .base_handler import BaseEventHandler


class AccountLinkEventHandler(BaseEventHandler):
    """
    AccountLinkEvent handler

    ユーザーがアカウント連携を完了した際のイベントを処理します。
    外部サービス（Google、Facebook等）との連携完了時に発生します。
    """

    async def handle(self, event: AccountLinkEvent) -> None:
        """
        Process account link event

        Args:
            event (AccountLinkEvent): Account link event
        """
        try:
            link_result = event.link.result if event.link else None
            nonce = event.link.nonce if event.link else None

            self.logger.info(f"Account link event: result={link_result}, nonce={nonce}")

            if link_result == "ok":
                response_message = (
                    "✅ アカウント連携が完了しました！\n"
                    "これで外部サービスと連携した機能をご利用いただけます。"
                )
                self.logger.info(f"Account linked successfully: nonce={nonce}")
            else:
                response_message = (
                    "❌ アカウント連携に失敗しました。\n"
                    "お手数ですが、再度連携をお試しください。"
                )
                self.logger.warning(
                    f"Account linking failed: result={link_result}, nonce={nonce}"
                )

            # Reply message を送信
            messages = [TextMessage(text=response_message)]
            reply_request = ReplyMessageRequest(
                reply_token=event.reply_token, messages=messages
            )
            await self.line_bot_api.reply_message(reply_request)

        except Exception as error:
            await self._safe_error_handle(error, event)
            raise

    async def _error_handle(
        self,
        error: Exception,
        event: AccountLinkEvent,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Handle error during account link processing"""
        try:
            self.logger.error(
                f"Account link handler error: {type(error).__name__} - {str(error)}",
                exc_info=True,
            )
        except Exception:
            pass
