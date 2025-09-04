import logging
from linebot.v3.messaging import (
    AsyncMessagingApi,
    ReplyMessageRequest,
    TextMessage,
)
from linebot.v3.webhooks import MessageEvent
from commands import AVAILABLE_COMMANDS

logger = logging.getLogger(__name__)


class TextHandler:
    """テキストメッセージを処理するハンドラー"""

    def __init__(self, api: AsyncMessagingApi):
        self.api = api
        # コマンドインスタンスを初期化
        self.commands = {
            cmd: command_class(api) for cmd, command_class in AVAILABLE_COMMANDS.items()
        }

    async def handle(self, event: MessageEvent) -> None:
        """テキストメッセージの処理"""
        try:
            message_text = event.message.text
            logger.debug(f"Received text: {message_text}")

            # コマンド（/で始まる）か通常のテキストかを判別
            if message_text.startswith("/"):
                await self._handle_command(event, message_text)
            else:
                return
                # await self._handle_regular_text(event, message_text)

        except Exception as e:
            logger.error(f"TextHandler error: {e}")

    async def _handle_command(self, event: MessageEvent, command: str) -> None:
        """スラッシュコマンドを処理"""
        try:
            if command in self.commands:
                # 登録されたコマンドを実行
                await self.commands[command].execute(event, command)
            else:
                # 未知のコマンド
                await self._reply_text(
                    event,
                    f"未知のコマンド: {command}\n/help でコマンド一覧を確認してください。"
                )
        except Exception as e:
            logger.error(f"Command execution error: {e}")
            await self._reply_text(event, "コマンドの実行中にエラーが発生しました。")

    async def _handle_regular_text(self, event: MessageEvent, text: str) -> None:
        """通常のテキストメッセージ処理（エコー機能）"""
        await self._reply_text(event, text)

    async def _reply_text(self, event: MessageEvent, text: str) -> None:
        """シンプルなテキストメッセージで返信"""
        await self.api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token, 
                messages=[TextMessage(text=text)]
            )
        )