from typing import Any, Dict, Optional

from linebot.v3.webhooks import FollowEvent
from linebot.v3.messaging import AsyncMessagingApi, TextMessage, ReplyMessageRequest

from .base_handler import BaseEventHandler


class FollowEventHandler(BaseEventHandler):
    """
    FollowEvent handler

    ユーザーがボットをフォローした際に発生するイベントを処理します。
    """

    async def handle(self, event: FollowEvent) -> None:
        """
        Process follow event

        Args:
            event (FollowEvent): Follow event

        Raises:
            Exception: Error occurred during event processing
        """
        try:
            user_id = (
                event.source.user_id if hasattr(event.source, "user_id") else "unknown"
            )

            self.logger.info(f"User followed: {user_id}")

            # 歓迎メッセージを送信
            welcome_message = (
                "フォローありがとうございます！\n"
                "何かメッセージを送ってみてください。"
            )
            messages = [TextMessage(text=welcome_message)]
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
        event: FollowEvent,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Handle error

        Args:
            error (Exception): Occurred error
            event (FollowEvent): Event where error occurred
            context (Optional[Dict[str, Any]]): Context information when error occurred
        """
        try:
            self.logger.error(
                f"Follow handler error: {type(error).__name__} - {str(error)}",
                exc_info=True,
            )
        except Exception:
            # 絶対に例外を投げてはいけません
            pass
