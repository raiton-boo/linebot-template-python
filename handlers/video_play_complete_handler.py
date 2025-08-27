# handlers/video_play_complete_handler.py
from typing import Any, Dict, Optional

from linebot.v3.webhooks import VideoPlayCompleteEvent
from linebot.v3.messaging import AsyncMessagingApi, TextMessage, ReplyMessageRequest

from .base_handler import BaseEventHandler


class VideoPlayCompleteEventHandler(BaseEventHandler):
    """
    VideoPlayCompleteEvent handler

    ユーザーが動画の再生を完了した際のイベントを処理します。
    """

    async def handle(self, event: VideoPlayCompleteEvent) -> None:
        """
        Process video play complete event

        Args:
            event (VideoPlayCompleteEvent): Video play complete event

        Raises:
            Exception: Error occurred during event processing
        """
        try:
            tracking_id = (
                event.video_play_complete.tracking_id
                if event.video_play_complete
                else None
            )

            self.logger.info(
                f"Video play complete event: tracking_id={tracking_id}",
                extra={
                    "event_type": "video_play_complete",
                    "tracking_id": tracking_id,
                    "source_type": event.source.type if event.source else "unknown",
                },
            )

            # 動画再生完了時の処理を実装
            response_message = "動画の視聴ありがとうございました！"

            # Reply message を送信
            messages = [TextMessage(text=response_message)]
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
        event: VideoPlayCompleteEvent,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Handle error

        Args:
            error (Exception): Occurred error
            event (VideoPlayCompleteEvent): Event where error occurred
            context (Optional[Dict[str, Any]]): Context information when error occurred
        """
        try:
            self.logger.error(
                f"Error handling video play complete event: {type(error).__name__} - {str(error)}",
                exc_info=True,
            )
        except Exception:
            # 絶対に例外を投げてはいけません
            pass
