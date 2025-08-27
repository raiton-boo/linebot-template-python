from typing import Any, Dict, Optional

from linebot.v3.webhooks import LeaveEvent
from linebot.v3.messaging import AsyncMessagingApi

from .base_handler import BaseEventHandler


class LeaveEventHandler(BaseEventHandler):
    """
    LeaveEvent handler

    ボットがグループやルームから退出させられた際に発生するイベントを処理します。
    """

    async def handle(self, event: LeaveEvent) -> None:
        """
        Process leave event

        Args:
            event (LeaveEvent): Leave event

        Raises:
            Exception: Error occurred during event processing
        """
        try:
            source_type = event.source.type if event.source else "unknown"
            source_id = getattr(event.source, f"{source_type}_id", "unknown")

            self.logger.info(f"Bot left {source_type}: {source_id}")

            # 退出イベントでは返信できないため、ログ記録のみ
            # 必要に応じて内部処理（統計更新、データベース処理など）を実装

        except Exception as error:
            await self._safe_error_handle(error, event)
            raise

    async def _error_handle(
        self,
        error: Exception,
        event: LeaveEvent,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Handle error

        Args:
            error (Exception): Occurred error
            event (LeaveEvent): Event where error occurred
            context (Optional[Dict[str, Any]]): Context information when error occurred
        """
        try:
            self.logger.error(
                f"Leave handler error: {type(error).__name__} - {str(error)}",
                exc_info=True,
            )
        except Exception:
            # 絶対に例外を投げてはいけません
            pass
