from typing import Any, Dict, Optional

from linebot.v3.webhooks import UnfollowEvent
from linebot.v3.messaging import AsyncMessagingApi

from .base_handler import BaseEventHandler


class UnfollowEventHandler(BaseEventHandler):
    """アンフォローイベントハンドラ"""

    async def handle(self, event: UnfollowEvent) -> None:
        """アンフォローイベントの処理"""
        user_id = (
            event.source.user_id if hasattr(event.source, "user_id") else "unknown"
        )

        self.logger.info(f"Get Unfollow event")

        # UnfollowEventでは返信不可
