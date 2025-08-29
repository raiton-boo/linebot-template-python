from typing import Any, Dict, Optional

from linebot.v3.webhooks import MemberJoinedEvent
from linebot.v3.messaging import AsyncMessagingApi, TextMessage, ReplyMessageRequest

from .base_handler import BaseEventHandler


class MemberJoinedEventHandler(BaseEventHandler):
    """メンバー参加イベントハンドラ"""

    async def handle(self, event: MemberJoinedEvent) -> None:
        """メンバー参加イベントの処理"""
        joined_members = (
            event.joined.members if event.joined and event.joined.members else []
        )

        self.logger.info(f"Get Member joined event")

        if joined_members:
            member_count = len(joined_members)
            message_text = f"{member_count}名のメンバーが参加しました。ようこそ！"
            self.logger.info(f"Member joined: {member_count} to {event.source.type}")
        else:
            message_text = "新しいメンバーが参加しました。ようこそ！"
            self.logger.info(f"Member joined to {event.source.type}")

        await self.line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token, messages=[TextMessage(text=message_text)]
            )
        )
