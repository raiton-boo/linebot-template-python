from typing import Any, Dict, Optional

from linebot.v3.webhooks import LeaveEvent
from linebot.v3.messaging import AsyncMessagingApi

from .base_handler import BaseEventHandler


class LeaveEventHandler(BaseEventHandler):
    """グループ退出イベントハンドラ"""

    async def handle(self, event: LeaveEvent) -> None:
        """グループ退出イベントの処理"""
        source_type = event.source.type if event.source else "unknown"
        source_id = getattr(event.source, f"{source_type}_id", "unknown")

        self.logger.info(f"Get Leave event")

        # LeaveEventでは返信不可
