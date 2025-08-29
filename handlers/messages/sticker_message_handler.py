"""
Sticker message handler
"""

from typing import Any, Optional, Dict
from linebot.v3.webhooks import MessageEvent
from linebot.v3.messaging import StickerMessage, ReplyMessageRequest, TextMessage

from .base_message_handler import BaseMessageHandler


class StickerMessageHandler(BaseMessageHandler):
    """
    ステッカーメッセージハンドラー

    ステッカー情報を返すシンプルなハンドラー
    """

    async def handle(self, event: MessageEvent) -> None:
        """
        ステッカーメッセージを処理

        Args:
            event (MessageEvent): メッセージイベント

        Raises:
            Exception: Error occurred during sticker message processing
        """
        try:
            user_id = getattr(event.source, "user_id", "unknown")
            self.logger.info(f"sticker message received from {user_id}")

            # ステッカー情報を取得
            sticker_info = self._get_sticker_info(event)

            # ステッカー情報を文字列で返信
            response = self._format_sticker_info(sticker_info)

            await self.line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token, messages=[TextMessage(text=response)]
                )
            )
        except Exception as error:
            await self._safe_error_handle(error, event)
            raise

    def _get_sticker_info(self, event: MessageEvent) -> dict:
        """
        ステッカー情報を取得

        Args:
            event (MessageEvent): メッセージイベント

        Returns:
            dict: ステッカー情報
        """
        message = event.message
        if not isinstance(message, StickerMessage):
            return {}

        return {
            "package_id": message.package_id,
            "sticker_id": message.sticker_id,
        }

    def _format_sticker_info(self, sticker_info: dict) -> str:
        """
        ステッカー情報をフォーマット

        Args:
            sticker_info (dict): ステッカー情報

        Returns:
            str: フォーマットされたステッカー情報
        """
        if not sticker_info:
            return "ステッカー情報を取得できませんでした。"

        package_id = sticker_info.get("package_id", "不明")
        sticker_id = sticker_info.get("sticker_id", "不明")

        return (
            f"ステッカー情報:\nパッケージID: {package_id}\nステッカーID: {sticker_id}"
        )

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
                f"Sticker message handler error from {user_id}: "
                f"{type(error).__name__} - {str(error)}",
                exc_info=True,
            )

            if context:
                self.logger.error(f"Error context: {context}")

        except Exception:
            # 絶対に例外を投げてはいけません
            pass
