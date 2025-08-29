"""
Image message handler
"""

from typing import Any, Optional, Dict
from linebot.v3.webhooks import MessageEvent
from linebot.v3.messaging import ReplyMessageRequest, TextMessage

from .base_message_handler import BaseMessageHandler


class ImageMessageHandler(BaseMessageHandler):
    """
    画像メッセージハンドラー

    シンプルな画像処理
    """

    async def handle(self, event: MessageEvent) -> None:
        """
        画像メッセージを処理

        Args:
            event (MessageEvent): メッセージイベント

        Raises:
            Exception: Error occurred during image message processing
        """
        try:
            user_id = getattr(event.source, "user_id", "unknown")
            self.logger.info(f"image message received from {user_id}")

            response = "画像を受信しました！"

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

        Args:
            error (Exception): エラー
            event (MessageEvent): メッセージイベント
            context (Optional[Dict[str, Any]]): コンテキスト情報
        """
        try:
            user_id = getattr(event.source, "user_id", "unknown")
            self.logger.error(
                f"Image message handler error from {user_id}: "
                f"{type(error).__name__} - {str(error)}",
                exc_info=True,
            )

            if context:
                self.logger.error(f"Error context: {context}")

        except Exception:
            # 絶対に例外を投げてはいけません
            pass
