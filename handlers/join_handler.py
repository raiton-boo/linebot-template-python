from typing import Any, Dict, Optional

from linebot.v3.webhooks import JoinEvent
from linebot.v3.messaging import AsyncMessagingApi, TextMessage, ReplyMessageRequest

from .base_handler import BaseEventHandler


class JoinEventHandler(BaseEventHandler):
    """グループ参加イベントハンドラ"""

    async def handle(self, event: JoinEvent) -> None:
        """グループ参加イベントの処理"""
        source_type = event.source.type if event.source else "unknown"
        source_id = getattr(event.source, f"{source_type}_id", "unknown")

        self.logger.info(f"Get Join event")

        greeting_message = (
            "グループに招待していただき、ありがとうございます。\n"
            "このボットでは様々な機能をお試しいただけます:\n\n"
            "・テキストメッセージ\n"
            "・画像の送信・解析\n"
            "・音声メッセージ\n"
            "・動画メッセージ\n"
            "・位置情報の共有\n"
            "・ステッカー\n"
            "・ファイル送信\n\n"
            "何でもメッセージを送ってみてください。"
        )

        await self.line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=greeting_message)],
            )
        )
