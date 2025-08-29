from typing import Any, Optional, Dict
from linebot.v3.webhooks import MessageEvent
from linebot.v3.messaging import ReplyMessageRequest, TextMessage

from .base_message_handler import BaseMessageHandler


class AudioMessageHandler(BaseMessageHandler):
    """音声メッセージハンドラ"""

    async def handle(self, event: MessageEvent) -> None:
        """音声メッセージの処理"""
        user_id = getattr(event.source, "user_id", "unknown")
        self.logger.info(f"Get Message event type for {event.message.type}")

        response = "音声を受信しました！音声の内容を解析中です..."

        await self.line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token, messages=[TextMessage(text=response)]
            )
        )
