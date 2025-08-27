import logging
from typing import Any, Dict, Optional

from linebot.v3.webhooks import MemberLeftEvent
from linebot.v3.messaging import AsyncMessagingApi, TextMessage, ReplyMessageRequest

from .base_handler import BaseEventHandler


class MemberLeftEventHandler(BaseEventHandler):
    """
    MemberLeftEvent handler

    グループやルームからメンバーが退出した際に発生するイベントを処理します。
    """

    async def handle(self, event: MemberLeftEvent) -> None:
        """
        Process member left event

        Args:
            event (MemberLeftEvent): Member left event

        Raises:
            Execption: Error occurred during event processing
        """
        try:
            # 退出したメンバーの情報を取得する
            left_members = (
                event.left.members if event.left and event.left.members else []
            )

            if left_members:
                member_count = len(left_members)
                message_text = f"{member_count}名のメンバーが退出しました。"

                self.logger.info(
                    f"Member left: {member_count} from {event.source.type}"
                )
            else:
                message_text = "メンバーが退出しました。"
                self.logger.info(f"Member left from {event.source.type}")

            # MemberLeftEventには reply_token がないため、ログ記録のみ
            # 必要に応じて内部処理（統計更新、データベース処理など）を実装
            self.logger.info(f"Member left event processed: {message_text}")

        except Exception as error:
            await self._safe_error_handle(error, event)
            raise

    async def _error_handle(
        self,
        error: Exception,
        event: MemberLeftEvent,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Handle error

        Args:
            error (Exception): Occurred error
            event (MemberLeftEvent): Event where error occurred
            context (Optional[Dict[str, Any]]): Context information when error occurred
        """
        try:
            self.logger.error(
                f"Member left handler error: {type(error).__name__} - {str(error)}",
                exc_info=True,
            )
        except Exception:
            # 絶対に例外を投げてはいけません
            pass
