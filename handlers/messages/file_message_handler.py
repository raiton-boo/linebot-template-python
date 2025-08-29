from typing import Any, Optional, Dict
from linebot.v3.webhooks import MessageEvent, FileMessageContent
from linebot.v3.messaging import ReplyMessageRequest, TextMessage

from .base_message_handler import BaseMessageHandler


class FileMessageHandler(BaseMessageHandler):
    """ファイルメッセージハンドラ"""

    async def handle(self, event: MessageEvent) -> None:
        """ファイルメッセージの処理"""
        user_id = self.get_user_id(event)
        self.logger.info(f"Get Message event type for {event.message.type}")

        file_info = self._get_file_info(event)
        response = self._format_file_response(file_info)

        await self.line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token, messages=[TextMessage(text=response)]
            )
        )

    def _get_file_info(self, event: MessageEvent) -> Dict[str, Any]:
        """ファイル情報を取得"""
        message = event.message
        if not isinstance(message, FileMessageContent):
            return {}

        return {
            "message_id": message.id,
            "file_name": getattr(message, "file_name", "unknown"),
            "file_size": getattr(message, "file_size", 0),
        }

    def _format_file_response(self, file_info: Dict[str, Any]) -> str:
        """ファイル情報をフォーマット"""
        file_name = file_info.get("file_name", "不明なファイル")
        file_size = file_info.get("file_size", 0)

        if file_size > 1024 * 1024:
            size_text = f"{file_size / (1024 * 1024):.1f} MB"
        elif file_size > 1024:
            size_text = f"{file_size / 1024:.1f} KB"
        else:
            size_text = f"{file_size} bytes"

        return f"ファイルを受信しました！\nファイル名: {file_name}\nサイズ: {size_text}\n\nファイルをお送りいただきありがとうございます！"
