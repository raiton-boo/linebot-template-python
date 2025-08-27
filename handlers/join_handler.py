from typing import Any, Dict, Optional

from linebot.v3.webhooks import JoinEvent
from linebot.v3.messaging import AsyncMessagingApi, TextMessage, ReplyMessageRequest

from .base_handler import BaseEventHandler


class JoinEventHandler(BaseEventHandler):
    """
    JoinEvent handler

    ボットがグループやルームに招待された際に発生するイベントを処理します。
    """

    async def handle(self, event: JoinEvent) -> None:
        """
        Process join event

        Args:
            event (JoinEvent): Join event

        Raises:
            Exception: Error occurred during event processing
        """
        try:
            source_type = event.source.type if event.source else "unknown"
            source_id = getattr(event.source, f"{source_type}_id", "unknown")

            self.logger.info(f"Bot joined {source_type}: {source_id}")

            # グループ参加時の挨拶メッセージ
            greeting_message = (
                "グループに招待していただき、ありがとうございます！\n"
                "何かメッセージを送ってみてください。"
            )
            messages = [TextMessage(text=greeting_message)]
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
        event: JoinEvent,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Handle error

        Args:
            error (Exception): Occurred error
            event (JoinEvent): Event where error occurred
            context (Optional[Dict[str, Any]]): Context information when error occurred
        """
        try:
            self.logger.error(
                f"Join handler error: {type(error).__name__} - {str(error)}",
                exc_info=True,
            )
        except Exception:
            # 絶対に例外を投げてはいけません
            pass
