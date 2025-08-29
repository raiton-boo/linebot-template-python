"""
Location message handler
"""

from typing import Any, Optional, Dict
from linebot.v3.webhooks import MessageEvent
from linebot.v3.messaging import ReplyMessageRequest, TextMessage, LocationMessage

from .base_message_handler import BaseMessageHandler


class LocationMessageHandler(BaseMessageHandler):
    """
    位置情報メッセージハンドラー
    """

    async def handle(self, event: MessageEvent) -> None:
        """
        位置情報メッセージを処理
        """
        try:
            user_id = getattr(event.source, "user_id", "unknown")
            self.logger.info(f"location message received from {user_id}")

            # 位置情報を取得
            location_info = self._get_location_info(event)
            response = self._format_location_info(location_info)

            await self.line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token, messages=[TextMessage(text=response)]
                )
            )
        except Exception as error:
            await self._safe_error_handle(error, event)
            raise

    def _get_location_info(self, event: MessageEvent) -> dict:
        """位置情報を取得"""
        message = event.message
        if not isinstance(message, LocationMessage):
            return {}

        return {
            "title": message.title,
            "address": message.address,
            "latitude": message.latitude,
            "longitude": message.longitude,
        }

    def _format_location_info(self, location_info: dict) -> str:
        """位置情報をフォーマット"""
        if not location_info:
            return "位置情報を取得できませんでした。"

        title = location_info.get("title", "不明")
        address = location_info.get("address", "不明")
        lat = location_info.get("latitude", "不明")
        lng = location_info.get("longitude", "不明")

        return (
            f"位置情報:\nタイトル: {title}\n住所: {address}\n緯度: {lat}\n経度: {lng}"
        )

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
                f"Location message handler error from {user_id}: "
                f"{type(error).__name__} - {str(error)}",
                exc_info=True,
            )

            if context:
                self.logger.error(f"Error context: {context}")

        except Exception:
            pass
