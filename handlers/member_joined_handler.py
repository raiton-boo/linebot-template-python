from typing import Any, Dict, Optional

from linebot.v3.webhooks import MemberJoinedEvent
from linebot.v3.messaging import AsyncMessagingApi, TextMessage, ReplyMessageRequest

from .base_handler import BaseEventHandler


class MemberJoinedEventHandler(BaseEventHandler):
    """
    MemberJoinedEvent handler

    グループやルームに新しいメンバーが参加した際に発生するイベントを処理します。
    """

    async def handle(self, event: MemberJoinedEvent) -> None:
        """
        Process member joined event

        Args:
            event (MemberJoinedEvent): Member joined event

        Raises:
            Exception: Error occurred during event processing
        """
        try:
            # 参加したメンバーの情報を取得
            joined_members = (
                event.joined.members if event.joined and event.joined.members else []
            )

            if joined_members:
                member_count = len(joined_members)
                message_text = f"{member_count}名のメンバーが参加しました！\nようこそ！"

                self.logger.info(
                    f"Member joined: {member_count} to {event.source.type}"
                )
            else:
                message_text = "新しいメンバーが参加しました！\nようこそ！"
                self.logger.info(f"Member joined to {event.source.type}")

            # 歓迎メッセージを送信
            messages = [TextMessage(text=message_text)]
            reply_request = ReplyMessageRequest(
                reply_token=event.reply_token, messages=messages
            )
            await self.line_bot_api.reply_message(reply_request)

        except Exception as error:
            await self._safe_error_handle(error, event)
            raise

    async def _error_handle(
        self,
        error: Exception,
        event: MemberJoinedEvent,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Handle error

        Args:
            error (Exception): Occurred error
            event (MemberJoinedEvent): Event where error occurred
            context (Optional[Dict[str, Any]]): Context information when error occurred
        """
        try:
            self.logger.error(
                f"Member joined handler error: {type(error).__name__} - {str(error)}",
                exc_info=True,
            )
        except Exception:
            # 絶対に例外を投げてはいけません
            pass
