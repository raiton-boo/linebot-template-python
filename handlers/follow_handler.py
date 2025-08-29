from typing import Any, Dict, Optional

from linebot.v3.webhooks import FollowEvent
from linebot.v3.messaging import AsyncMessagingApi, TextMessage, ReplyMessageRequest

from .base_handler import BaseEventHandler


class FollowEventHandler(BaseEventHandler):
    """フォローイベントハンドラ"""

    async def handle(self, event: FollowEvent) -> None:
        """フォローイベントの処理"""
        user_id = (
            event.source.user_id if hasattr(event.source, "user_id") else "unknown"
        )

        self.logger.info(f"Get Follow event")

        welcome_message = (
            "フォローありがとうございます。\n"
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
                messages=[TextMessage(text=welcome_message)],
            )
        )
