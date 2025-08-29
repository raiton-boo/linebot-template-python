from typing import Any, Optional, Dict
from linebot.v3.webhooks import MessageEvent
from linebot.v3.messaging import ReplyMessageRequest, TextMessage

from .base_message_handler import BaseMessageHandler


class VideoMessageHandler(BaseMessageHandler):
    """動画メッセージハンドラ"""

    async def handle(self, event: MessageEvent) -> None:
        """動画メッセージの処理"""
        user_id = getattr(event.source, "user_id", "unknown")
        self.logger.info(f"Get Message event type for {event.message.type}")

        response = "動画を受信しました！素敵な動画をありがとうございます。"

        await self.line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token, messages=[TextMessage(text=response)]
            )
        )
