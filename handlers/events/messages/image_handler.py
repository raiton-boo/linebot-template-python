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


class ImageHandler:
    """画像メッセージを処理するハンドラー"""

    def __init__(self, api: AsyncMessagingApi):
        self.api = api

    async def handle(self, event: MessageEvent) -> None:
        """画像メッセージの処理"""
        try:
            image_id = event.message.id
            logger.info(f"Received image: {image_id}")

            # Flexメッセージで視覚的に応答
            flex_message = self._create_image_flex_message(image_id)

            await self.api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[flex_message],
                )
            )

        except Exception as e:
            logger.error(f"ImageHandler error: {e}")

    def _create_image_flex_message(self, image_id: str) -> FlexMessage:
        """画像受信用のFlexメッセージを作成"""
        # ヘッダー部分（紫色のテーマ）
        header_box = FlexBox(
            layout="vertical",
            contents=[
                FlexText(text="画像受信", weight="bold", size="xl", color="#ffffff"),
                FlexText(
                    text="素敵な画像をありがとうございます",
                    size="md",
                    color="#ffffff",
                    wrap=True,
                ),
            ],
            background_color="#9B59B6",
            padding_all="20px",
            spacing="md",
        )

        # 画像情報を表示する部分
        info_box = FlexBox(
            layout="vertical",
            contents=[
                FlexText(text="画像情報", weight="bold", size="md", color="#9B59B6"),
                FlexSeparator(margin="sm"),
                # 画像IDの表示（長いので2行に分割）
                FlexBox(
                    layout="baseline",
                    contents=[
                        FlexText(text="画像ID", size="sm", color="#666666", flex=2),
                        FlexText(
                            text=image_id,
                            size="xs",
                            wrap=True,
                            flex=3,
                            max_lines=2,
                        ),
                    ],
                    margin="md",
                ),
                FlexBox(
                    layout="baseline",
                    contents=[
                        FlexText(text="形式", size="sm", color="#666666", flex=2),
                        FlexText(text="画像ファイル", size="sm", flex=3),
                    ],
                    margin="md",
                ),
                FlexBox(
                    layout="baseline",
                    contents=[
                        FlexText(text="状態", size="sm", color="#666666", flex=2),
                        FlexText(
                            text="受信完了",
                            size="sm",
                            color="#00B894",
                            weight="bold",
                            flex=3,
                        ),
                    ],
                    margin="md",
                ),
            ],
            spacing="sm",
            padding_all="20px",
        )

        # 画像についての説明部分
        description_box = FlexBox(
            layout="vertical",
            contents=[
                FlexText(
                    text="画像について", weight="bold", size="md", color="#9B59B6"
                ),
                FlexText(
                    text="送信いただいた画像は正常に受信されました。LINE内で表示・保存が可能です。",
                    size="sm",
                    wrap=True,
                    color="#666666",
                    margin="sm",
                ),
            ],
            margin="xl",
            background_color="#F8F9FA",
            padding_all="12px",
            corner_radius="8px",
        )

        # フッター部分
        footer_box = FlexBox(
            layout="vertical",
            contents=[
                FlexText(
                    text="画像をお送りいただきありがとうございます",
                    size="sm",
                    color="#9B59B6",
                    align="center",
                    weight="bold",
                    wrap=True,
                )
            ],
            padding_all="16px",
        )

        # 全体のボディ構成
        body_contents = [info_box, description_box]
        body_box = FlexBox(layout="vertical", contents=body_contents, spacing="sm")

        # Flexバブルを組み立て
        bubble = FlexBubble(hero=header_box, body=body_box, footer=footer_box)

        return FlexMessage(alt_text=f"画像受信: ID {image_id[:10]}...", contents=bubble)
