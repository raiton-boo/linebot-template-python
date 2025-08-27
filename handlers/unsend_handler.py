from typing import Any, Dict, Optional

from linebot.v3.webhooks import UnsendEvent
from linebot.v3.messaging import AsyncMessagingApi

from .base_handler import BaseEventHandler


class UnsendEventHandler(BaseEventHandler):
    """
    UnsendEvent handler

    ユーザーがメッセージの送信取り消しした際に発生するイベントを処理します。
    """

    async def handle(self, event: UnsendEvent) -> None:
        """
        Process message unsend event

        Args:
            event (UnsendEvent): Message unsend event

        Raises:
            Exception: Error occurred during event processing
        """
        try:
            unsend_message_id = event.unsend.message_id if event.unsend else None

            self.logger.info(f"Message unsent: message_id={unsend_message_id}")

            # 必要に応じて取消通知やデータベース更新などの処理を実装

        except Exception as error:
            await self._safe_error_handle(error, event)

    async def _error_handle(
        self,
        error: Exception,
        event: UnsendEvent,
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
                f"Unsend handler error: {type(error).__name__} - {str(error)}",
                exc_info=True,
            )
        except Exception:
            # 絶対に例外を投げてはいけません
            pass
