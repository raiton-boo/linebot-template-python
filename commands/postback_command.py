import logging
from .base_command import BaseCommand
from linebot.v3.messaging import (
    ReplyMessageRequest,
    FlexMessage,
    FlexBubble,
    FlexBox,
    FlexText,
    FlexButton,
    PostbackAction,
    FlexSeparator,
)
from linebot.v3.webhooks import MessageEvent

logger = logging.getLogger(__name__)


class PostbackCommand(BaseCommand):
    """Postbackテストコマンド"""

    async def execute(self, event: MessageEvent, command: str) -> None:
        """Postback機能のテスト用ボタンメッセージを送信"""
        try:
            flex_message = self._create_postback_flex_message()

            await self.api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[flex_message],
                )
            )

        except Exception as e:
            logger.error(f"Postback command error: {e}")
            await self._reply_error(event, "Postback機能のテストに失敗しました")

    def _create_postback_flex_message(self) -> FlexMessage:
        """Postbackテスト用のFlexメッセージを作成"""
        # ヘッダー部分
        header_box = FlexBox(
            layout="vertical",
            contents=[
                FlexText(
                    text="Postback テスト", weight="bold", size="xl", color="#ffffff"
                ),
                FlexText(
                    text="ボタンを押してPostback機能をテスト",
                    size="md",
                    color="#ffffff",
                    wrap=True,
                ),
            ],
            background_color="#007BFF",
            padding_all="20px",
            spacing="md",
        )

        # 説明部分
        description_box = FlexBox(
            layout="vertical",
            contents=[
                FlexText(
                    text="各ボタンを押すと、それぞれ異なるデータがPostbackとして送信されます:",
                    size="sm",
                    wrap=True,
                    color="#666666",
                    margin="sm",
                ),
            ],
            padding_all="20px",
        )

        # ボタン部分
        buttons_box = FlexBox(
            layout="vertical",
            contents=[
                FlexButton(
                    action=PostbackAction(
                        label="基本テスト",
                        data="action=basic_test&type=simple",
                        display_text="基本テストを実行しました",
                    ),
                    style="primary",
                    color="#28A745",
                ),
                FlexButton(
                    action=PostbackAction(
                        label="パラメータテスト",
                        data="action=param_test&user=sample&value=123",
                        display_text="パラメータテストを実行しました",
                    ),
                    style="secondary",
                    margin="md",
                ),
                FlexButton(
                    action=PostbackAction(
                        label="JSON データテスト",
                        data='{"action":"json_test","data":{"id":999,"name":"test_user","timestamp":"2024-01-01"}}',
                        display_text="JSON データテストを実行しました",
                    ),
                    style="primary",
                    color="#FFC107",
                    margin="md",
                ),
                FlexButton(
                    action=PostbackAction(
                        label="サイレントテスト",
                        data="action=silent_test&notification=false",
                    ),
                    style="secondary",
                    margin="md",
                ),
            ],
            spacing="sm",
            padding_all="20px",
        )

        # 注意事項
        footer_box = FlexBox(
            layout="vertical",
            contents=[
                FlexSeparator(),
                FlexText(
                    text="💡 ボタンを押すとPostbackイベントが発生し、サーバー側で処理されます",
                    size="xs",
                    color="#999999",
                    wrap=True,
                    margin="md",
                ),
            ],
            padding_all="16px",
        )

        # 全体をまとめてバブルを作成
        bubble = FlexBubble(
            hero=header_box,
            body=FlexBox(
                layout="vertical",
                contents=[description_box, buttons_box],
                spacing="none",
            ),
            footer=footer_box,
        )

        return FlexMessage(
            alt_text="Postback機能テスト - ボタンを押してください", contents=bubble
        )
