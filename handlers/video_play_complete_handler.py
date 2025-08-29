# handlers/video_play_complete_handler.py
from typing import Any, Dict, Optional

from linebot.v3.webhooks import VideoPlayCompleteEvent
from linebot.v3.messaging import AsyncMessagingApi, TextMessage, ReplyMessageRequest

from .base_handler import BaseEventHandler


class VideoPlayCompleteEventHandler(BaseEventHandler):
    """動画再生完了イベントハンドラ"""

    async def handle(self, event: VideoPlayCompleteEvent) -> None:
        """動画再生完了イベントの処理"""
        tracking_id = (
            event.video_play_complete.tracking_id if event.video_play_complete else None
        )

        self.logger.info(
            f"Get VideoPlayComplete event",
            extra={
                "event_type": "video_play_complete",
                "tracking_id": tracking_id,
                "source_type": event.source.type if event.source else "unknown",
            },
        )

        response_message = (
            "動画の視聴ありがとうございました。その他のコンテンツもお楽しみください。"
        )

        await self.line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=response_message)],
            )
        )
