import logging
from linebot.v3.messaging import (
    AsyncMessagingApi, 
    ReplyMessageRequest, 
    TextMessage,
    FlexMessage,
    FlexBubble,
    FlexBox,
    FlexText,
    FlexSeparator,
)
from linebot.v3.webhooks import MessageEvent

logger = logging.getLogger(__name__)


class AudioHandler:
    """音声メッセージを処理するハンドラー"""
    
    def __init__(self, api: AsyncMessagingApi):
        self.api = api

    async def handle(self, event: MessageEvent) -> None:
        """音声メッセージの処理"""
        try:
            audio = event.message
            audio_id = audio.id
            duration = audio.duration

            logger.info(f"Received audio: {audio_id} ({duration}ms)")

            # 再生時間を読みやすい形式に変換
            formatted_duration = self._format_duration(duration)
            
            # Flexメッセージで応答
            flex_message = self._create_audio_flex_message(audio_id, duration, formatted_duration)

            await self.api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[flex_message],
                )
            )

        except Exception as e:
            logger.error(f"AudioHandler error: {e}")

    def _format_duration(self, duration_ms: int) -> str:
        """再生時間をわかりやすい形式に変換"""
        seconds = duration_ms / 1000
        
        if seconds < 60:
            return f"{seconds:.1f}秒"
        else:
            minutes = int(seconds // 60)
            remaining_seconds = int(seconds % 60)
            return f"{minutes}分{remaining_seconds}秒"

    def _create_audio_flex_message(self, audio_id: str, duration: int, formatted_duration: str) -> FlexMessage:
        """音声受信用のFlexメッセージを作成"""
        # ヘッダー（音声テーマの緑色）
        header_box = FlexBox(
            layout="vertical",
            contents=[
                FlexText(text="音声受信", weight="bold", size="xl", color="#ffffff"),
                FlexText(
                    text="音声メッセージをありがとうございます",
                    size="md",
                    color="#ffffff",
                    wrap=True,
                ),
            ],
            background_color="#27AE60",
            padding_all="20px",
            spacing="md",
        )

        # 音声情報部分
        info_box = FlexBox(
            layout="vertical",
            contents=[
                FlexText(text="音声情報", weight="bold", size="md", color="#27AE60"),
                FlexSeparator(margin="sm"),
                FlexBox(
                    layout="baseline",
                    contents=[
                        FlexText(text="音声ID", size="sm", color="#666666", flex=2),
                        FlexText(
                            text=audio_id[:20] + "...",  # IDが長いので短縮
                            size="xs",
                            wrap=True,
                            flex=3,
                        ),
                    ],
                    margin="md",
                ),
                FlexBox(
                    layout="baseline",
                    contents=[
                        FlexText(text="再生時間", size="sm", color="#666666", flex=2),
                        FlexText(text=formatted_duration, size="sm", flex=3, weight="bold"),
                    ],
                    margin="md",
                ),
                FlexBox(
                    layout="baseline",
                    contents=[
                        FlexText(text="形式", size="sm", color="#666666", flex=2),
                        FlexText(text="音声メッセージ", size="sm", flex=3),
                    ],
                    margin="md",
                ),
            ],
            spacing="sm",
            padding_all="20px",
        )

        # 説明部分
        description_box = FlexBox(
            layout="vertical",
            contents=[
                FlexText(
                    text="音声について", weight="bold", size="md", color="#27AE60"
                ),
                FlexText(
                    text="送信いただいた音声メッセージは正常に受信されました。LINE内で再生いただけます。",
                    size="sm",
                    wrap=True,
                    color="#666666",
                    margin="sm",
                ),
            ],
            margin="xl",
            background_color="#E8F5E8",
            padding_all="12px",
            corner_radius="8px",
        )

        # フッター
        footer_box = FlexBox(
            layout="vertical",
            contents=[
                FlexText(
                    text="音声メッセージをありがとうございます",
                    size="sm",
                    color="#27AE60",
                    align="center",
                    weight="bold",
                    wrap=True,
                )
            ],
            padding_all="16px",
        )

        body_contents = [info_box, description_box]
        body_box = FlexBox(layout="vertical", contents=body_contents, spacing="sm")

        bubble = FlexBubble(hero=header_box, body=body_box, footer=footer_box)

        return FlexMessage(
            alt_text=f"音声受信: {formatted_duration}",
            contents=bubble
        )