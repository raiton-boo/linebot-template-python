from typing import Any, Optional, Dict
from linebot.v3.webhooks import MessageEvent
from linebot.v3.messaging import StickerMessage, ReplyMessageRequest, TextMessage

from .base_message_handler import BaseMessageHandler


class StickerMessageHandler(BaseMessageHandler):
    """ステッカーメッセージハンドラ"""

    async def handle(self, event: MessageEvent) -> None:
        """ステッカーメッセージの処理"""
        user_id = self.get_user_id(event)
        self.logger.info(f"Get Message event type for {event.message.type}")

        # ステッカー情報を取得
        sticker_info = self._get_sticker_info(event)

        # ステッカー情報が取得できない場合は基本応答
        if not sticker_info:
            response = "ステッカーありがとうございます！"
        else:
            response = self._format_sticker_info(sticker_info)

        await self.line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token, messages=[TextMessage(text=response)]
            )
        )

    def _get_sticker_info(self, event: MessageEvent) -> Dict[str, Any]:
        """ステッカー情報を取得"""
        message = event.message
        if not hasattr(message, "package_id") or not hasattr(message, "sticker_id"):
            return {}

        return {
            "package_id": getattr(message, "package_id", "unknown"),
            "sticker_id": getattr(message, "sticker_id", "unknown"),
            "sticker_resource_type": getattr(
                message, "sticker_resource_type", "static"
            ),
            "keywords": getattr(message, "keywords", []),
            "text": getattr(message, "text", None),
        }

    def _format_sticker_info(self, sticker_info: Dict[str, Any]) -> str:
        """ステッカー情報をフォーマット"""
        if not sticker_info:
            return "ステッカー情報を取得できませんでした。"

        package_id = sticker_info.get("package_id", "不明")
        sticker_id = sticker_info.get("sticker_id", "不明")
        resource_type = sticker_info.get("sticker_resource_type", "static")
        keywords = sticker_info.get("keywords", [])
        text = sticker_info.get("text")

        response_parts = [
            f"ステッカー情報:",
            f"パッケージID: {package_id}",
            f"ステッカーID: {sticker_id}",
            f"タイプ: {resource_type}",
        ]

        if keywords:
            response_parts.append(f"キーワード: {', '.join(keywords[:3])}...")

        if text:
            response_parts.append(f"テキスト: {text}")

        return "\n".join(response_parts)

    async def _custom_message_error_handling(
        self,
        error: Exception,
        event: MessageEvent,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """ステッカーメッセージ特有のエラーハンドリング"""
        if isinstance(error, ValueError):
            self.logger.info(f"Sticker validation error: {error}")
        elif "sticker" in str(error).lower():
            self.logger.warning(f"Sticker processing error: {error}")
