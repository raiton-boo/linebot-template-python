"""
メッセージイベントハンドラ
メッセージを受信した際の処理
"""

from typing import Any

from linebot.v3.messaging import TextMessage, ReplyMessageRequest
from linebot.v3.webhooks import MessageEvent, MessageContent
from linebot_error_analyzer import AsyncLineErrorAnalyzer, ApiPattern, ErrorCategory

from .base_handler import BaseEventHandler
from commands import GetProfileCommand


class MessageEventHandler(BaseEventHandler):
    """
    MessageEventを処理するハンドラ
    """

    def __init__(self, *args, **kwargs):
        """
        初期化
        """
        super().__init__(*args, **kwargs)
        self.get_profile_command = GetProfileCommand(self.line_bot_api, self.logger)

    async def handle(self, event: MessageEvent) -> None:
        """
        メッセージイベントの処理

        Args:
            event (MessageEvent): メッセージイベント
        """
        try:
            # テキストメッセージ以外は無視
            if not hasattr(event.message, "text") or not event.message.text:
                return

            message_text = event.message.text.strip().lower()

            # プロフィール情報取得コマンド
            if message_text == "profile":
                await self.get_profile_command.execute(event)
                return

            # 通常の鸚鵡返し処理
            reply_text = event.message.text
            messages = [TextMessage(text=reply_text)]

            await self.line_bot_api.reply_message(
                ReplyMessageRequest(reply_token=event.reply_token, messages=messages)
            )

        except Exception as e:
            # エラー処理
            self.logger.error(f"メッセージ処理失敗: {type(e).__name__}")
            await self._handle_message_error(e, event)

    async def _handle_message_error(
        self, error: Exception, event: MessageEvent
    ) -> None:
        """
        メッセージ処理の専用エラーハンドリング

        Args:
            error (Exception): 発生したエラー
            event (MessageEvent): メッセージイベント
        """
        user_id = getattr(event.source, "user_id", "unknown")

        try:
            # エラー解析
            analyzer = AsyncLineErrorAnalyzer()
            analysis_result = await analyzer.analyze(error, ApiPattern.MESSAGE_REPLY)

            # 重要エラーのみ詳細ログ
            if analysis_result.category == ErrorCategory.RATE_LIMIT:
                retry_time = getattr(analysis_result, "retry_after", None) or 60
                self.logger.warning(f"レート制限[{user_id}]: {retry_time}秒待機")
            elif analysis_result.category == ErrorCategory.SERVER_ERROR:
                self.logger.error(f"サーバーエラー[{user_id}]")
            elif analysis_result.category == ErrorCategory.INVALID_REPLY_TOKEN:
                self.logger.warning(f"無効ReplyToken[{user_id}]")
            else:
                self.logger.error(
                    f"メッセージエラー[{user_id}]: {analysis_result.category}"
                )

        except Exception:
            # analyzer失敗時のフォールバック
            self.logger.error(f"メッセージ処理失敗[{user_id}]: {type(error).__name__}")
