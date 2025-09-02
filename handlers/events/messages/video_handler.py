import logging
from linebot.v3.messaging import (
    AsyncMessagingApi,
    ReplyMessageRequest,
    FlexMessage,
    FlexBubble,
    FlexBox,
    FlexText,
    FlexSeparator,
)
from linebot.v3.webhooks import MessageEvent

logger = logging.getLogger(__name__)


class VideoHandler:
    def __init__(self, api: AsyncMessagingApi):
        self.api = api

    async def handle(self, event: MessageEvent) -> None:
        try:
            video = event.message
            video_id = video.id
            duration = video.duration

            logger.info(f"Received video: {video_id} ({duration}ms)")

            # Flexメッセージで応答
            flex_message = self._create_video_flex_message(video_id, duration)

            await self.api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[flex_message],
                )
            )

        except Exception as e:
            logger.error(f"VideoHandler error: {e}")

    def _create_video_flex_message(self, video_id: str, duration: int) -> FlexMessage:

        # 再生時間を読みやすい形式に変換
        duration_formatted = self._format_duration(duration)
        duration_category = self._categorize_duration(duration)

        # ヘッダーボックス
        header_box = FlexBox(
            layout="vertical",
            contents=[
                FlexText(text="動画受信", weight="bold", size="xl", color="#ffffff"),
                FlexText(
                    text="動画を受信しました", size="md", color="#ffffff", wrap=True
                ),
            ],
            background_color="#E74C3C",
            padding_all="20px",
            spacing="md",
        )

        # 動画情報セクション
        video_info_contents = [
            FlexText(text="動画情報", weight="bold", size="md", color="#E74C3C"),
            FlexSeparator(margin="sm"),
            self._create_video_info_row("動画ID", video_id),
            self._create_video_info_row("再生時間", duration_formatted),
            self._create_video_info_row("カテゴリ", duration_category),
        ]

        video_info_box = FlexBox(
            layout="vertical", contents=video_info_contents, margin="lg"
        )

        # 動画説明セクション
        description_box = FlexBox(
            layout="vertical",
            contents=[
                FlexText(
                    text="動画について", weight="bold", size="md", color="#E74C3C"
                ),
                FlexText(
                    text="映像と音声を含む動画ファイルです。LINE内で再生いただけます。",
                    size="sm",
                    wrap=True,
                    color="#666666",
                    margin="sm",
                ),
            ],
            margin="xl",
            background_color="#FDF2F2",
            padding_all="12px",
            corner_radius="8px",
        )

        # メインボディ
        body_contents = [video_info_box, description_box]

        body_box = FlexBox(
            layout="vertical", contents=body_contents, spacing="sm", padding_all="20px"
        )

        # フッターボックス
        footer_box = FlexBox(
            layout="vertical",
            contents=[
                FlexText(
                    text="動画をお送りいただきありがとうございます",
                    size="sm",
                    color="#E74C3C",
                    align="center",
                    weight="bold",
                    wrap=True,
                )
            ],
            padding_all="16px",
        )

        # バブル作成
        bubble = FlexBubble(hero=header_box, body=body_box, footer=footer_box)

        return FlexMessage(
            alt_text=f"動画受信 (再生時間: {duration_formatted})", contents=bubble
        )

    def _create_video_info_row(self, label: str, value: str) -> FlexBox:
        return FlexBox(
            layout="baseline",
            contents=[
                FlexText(text=label, size="sm", color="#666666", flex=2),
                FlexText(text=value, size="sm", wrap=True, flex=3, max_lines=2),
            ],
            margin="md",
        )

    def _format_duration(self, duration_ms: int) -> str:
        seconds = duration_ms / 1000

        if seconds < 60:
            return f"{seconds:.1f}秒"
        elif seconds < 3600:  # 1時間未満
            minutes = int(seconds // 60)
            remaining_seconds = int(seconds % 60)
            return f"{minutes}分{remaining_seconds}秒"
        else:  # 1時間以上
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}時間{minutes}分"

    def _categorize_duration(self, duration_ms: int) -> str:
        """再生時間をカテゴリ分け"""
        seconds = duration_ms / 1000

        if seconds < 15:
            return "ショート動画 (15秒未満)"
        elif seconds < 60:
            return "短編動画 (1分未満)"
        elif seconds < 300:  # 5分
            return "中編動画 (5分未満)"
        elif seconds < 1800:  # 30分
            return "長編動画 (30分未満)"
        else:
            return "長時間動画 (30分以上)"
