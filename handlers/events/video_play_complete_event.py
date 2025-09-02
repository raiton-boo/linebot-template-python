import logging
from linebot.v3.messaging import AsyncMessagingApi, ReplyMessageRequest, TextMessage
from linebot.v3.webhooks import VideoPlayCompleteEvent

logger = logging.getLogger(__name__)


class VideoPlayCompleteEventHandler:

    def __init__(self, api: AsyncMessagingApi):
        self.api = api

    async def handle(self, event: VideoPlayCompleteEvent) -> None:
        try:
            video_play_complete = event.video_play_complete
            tracking_id = video_play_complete.tracking_id

            logger.info(f"Video play completed - Tracking ID: {tracking_id}")

            response_text = (
                "動画の再生が完了しました！\n",
                "ご視聴ありがとうございました。",
            )

            await self.api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=response_text)],
                )
            )

        except Exception as e:
            logger.error(f"VideoPlayCompleteEventHandler error: {e}")


def get_handlers(api: AsyncMessagingApi):
    video_play_complete_handler = VideoPlayCompleteEventHandler(api)
    return {VideoPlayCompleteEvent: video_play_complete_handler.handle}
