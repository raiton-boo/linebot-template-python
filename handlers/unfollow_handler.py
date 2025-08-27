from typing import Any, Dict, Optional

from linebot.v3.webhooks import UnfollowEvent
from linebot.v3.messaging import AsyncMessagingApi

from .base_handler import BaseEventHandler


class UnfollowEventHandler(BaseEventHandler):
    """
    UnfollowEvent handler

    ユーザーがボットをブロック（アンフォロー）した際に発生するイベントを処理します。
    """

    async def handle(self, event: UnfollowEvent) -> None:
        """
        Process unfollow event

        Args:
            event (UnfollowEvent): Unfollow event

        Raises:
            Exception: Error occurred during event processing
        """
        try:
            user_id = (
                event.source.user_id if hasattr(event.source, "user_id") else "unknown"
            )

            self.logger.info(f"User unfollowed: {user_id}")

            # アンフォローイベントでは返信できないため、ログ記録のみ
            # 必要に応じて内部処理（統計更新、データベース処理など）を実装

        except Exception as error:
            await self._safe_error_handle(error, event)
            raise

    async def _error_handle(
        self,
        error: Exception,
        event: UnfollowEvent,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Handle error

        Args:
            error (Exception): Occurred error
            event (UnfollowEvent): Event where error occurred
            context (Optional[Dict[str, Any]]): Context information when error occurred
        """
        try:
            self.logger.error(
                f"Unfollow handler error: {type(error).__name__} - {str(error)}",
                exc_info=True,
            )
        except Exception:
            # 絶対に例外を投げてはいけません
            pass
