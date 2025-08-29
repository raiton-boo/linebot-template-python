import logging
from typing import Any, Dict, Optional

from linebot.v3.webhooks import MemberLeftEvent
from linebot.v3.messaging import AsyncMessagingApi, TextMessage, ReplyMessageRequest

from .base_handler import BaseEventHandler


class MemberLeftEventHandler(BaseEventHandler):
    """メンバー退出イベントハンドラ"""

    async def handle(self, event: MemberLeftEvent) -> None:
        """メンバー退出イベントの処理"""
        left_members = event.left.members if event.left and event.left.members else []

        self.logger.info(f"Get Member left event")

        if left_members:
            member_count = len(left_members)
            self.logger.info(f"Member left: {member_count}名 ({event.source.type})")
        else:
            self.logger.info(f"Member left: {event.source.type}")

        # MemberLeftEventでは返信不可
