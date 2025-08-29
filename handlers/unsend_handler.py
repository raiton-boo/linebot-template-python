from typing import Any, Dict, Optional

from linebot.v3.webhooks import UnsendEvent
from linebot.v3.messaging import AsyncMessagingApi

from .base_handler import BaseEventHandler


class UnsendEventHandler(BaseEventHandler):
    """メッセージ送信取消イベントハンドラ"""

    async def handle(self, event: UnsendEvent) -> None:
        """メッセージ送信取消イベントの処理"""
        unsend_message_id = event.unsend.message_id if event.unsend else None

        self.logger.info(f"Get Unsend event")

        # UnsendEventでは返信不可
