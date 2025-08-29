from typing import Any, Optional, Dict
from linebot.v3.webhooks import MessageEvent
from linebot.v3.messaging import ReplyMessageRequest, TextMessage, ImageMessage

from .base_message_handler import BaseMessageHandler


class ImageMessageHandler(BaseMessageHandler):
    """画像メッセージハンドラ"""

    async def handle(self, event: MessageEvent) -> None:
        """画像メッセージの処理"""
        user_id = self.get_user_id(event)
        self.logger.info(f"Get Message event type for {event.message.type}")

        # 画像情報を取得
        image_info = self._get_image_info(event)

        # 画像情報が取得できない場合は基本応答
        if not image_info:
            response = "画像を受信しました！ありがとうございます。"
        else:
            analysis_result = await self._analyze_image(image_info)
            response = self._format_image_response(image_info, analysis_result)

        await self.line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token, messages=[TextMessage(text=response)]
            )
        )

    def _get_image_info(self, event: MessageEvent) -> Dict[str, Any]:
        """画像情報を取得"""
        message = event.message
        if not hasattr(message, "id"):
            return {}

        return {
            "message_id": getattr(message, "id", "unknown"),
            "content_provider": getattr(message, "content_provider", None),
            "image_set": getattr(message, "image_set", None),
        }

    async def _analyze_image(self, image_info: Dict[str, Any]) -> Dict[str, Any]:
        """画像解析（模擬実装）"""
        return {
            "detected_objects": ["person", "background"],
            "colors": ["blue", "white", "green"],
            "estimated_size": "medium",
            "quality": "good",
        }

    def _format_image_response(
        self, image_info: Dict[str, Any], analysis: Dict[str, Any]
    ) -> str:
        """画像処理結果をフォーマット"""
        message_id = image_info.get("message_id", "不明")

        response_parts = [
            "画像を受信しました！",
            f"メッセージID: {message_id}",
            "",
            "画像解析結果:",
        ]

        if analysis.get("detected_objects"):
            objects = ", ".join(analysis["detected_objects"])
            response_parts.append(f"検出された物体: {objects}")

        if analysis.get("colors"):
            colors = ", ".join(analysis["colors"][:3])
            response_parts.append(f"主要な色: {colors}")

        if analysis.get("quality"):
            response_parts.append(f"画質: {analysis['quality']}")

        response_parts.append("\n画像をありがとうございます！")

        return "\n".join(response_parts)

    async def _custom_message_error_handling(
        self,
        error: Exception,
        event: MessageEvent,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """画像メッセージ特有のエラーハンドリング"""
        if "image" in str(error).lower():
            self.logger.warning(f"Image processing error: {error}")
        elif isinstance(error, ValueError):
            self.logger.info(f"Image validation error: {error}")
