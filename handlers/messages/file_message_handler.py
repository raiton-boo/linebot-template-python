"""
File message handler
"""

from typing import Any, Optional, Dict
from linebot.v3.webhooks import MessageEvent
from linebot.v3.messaging import ReplyMessageRequest, TextMessage

from .base_message_handler import BaseMessageHandler


class FileMessageHandler(BaseMessageHandler):
    """
    ファイルメッセージハンドラー
    """

    async def handle(self, event: MessageEvent) -> None:
        """
        ファイルメッセージを処理
        """
        try:
            user_id = getattr(event.source, "user_id", "unknown")
            self.logger.info(f"file message received from {user_id}")

            response = "ファイルを受信しました！"

            await self.line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token, messages=[TextMessage(text=response)]
                )
            )
        except Exception as error:
            await self._safe_error_handle(error, event)
            raise

    async def _error_handle(
        self,
        error: Exception,
        event: MessageEvent,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        エラーハンドリング
        """
        try:
            user_id = getattr(event.source, "user_id", "unknown")
            self.logger.error(
                f"File message handler error from {user_id}: "
                f"{type(error).__name__} - {str(error)}",
                exc_info=True,
            )

            if context:
                self.logger.error(f"Error context: {context}")

        except Exception:
            pass
