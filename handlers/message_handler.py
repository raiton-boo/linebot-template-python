"""
メッセージイベントハンドラ
テキストメッセージを受信した際の処理を担当
"""

from typing import Any

from linebot.v3.messaging import TextMessage, ReplyMessageRequest
from linebot.v3.webhooks import MessageEvent, MessageContent
from linebot_error_analyzer import AsyncLineErrorAnalyzer, ApiPattern, ErrorCategory

from .base_handler import BaseEventHandler


class MessageEventHandler(BaseEventHandler):
    """
    メッセージイベントを処理するハンドラ

    受信したテキストメッセージを鸚鵡返しで返信します。
    """

    async def handle(self, event: MessageEvent) -> None:
        """
        メッセージイベントを処理

        Args:
            event (MessageEvent): メッセージイベント
        """
        try:
            # 早期リターン: テキストメッセージ以外はスキップ
            if not hasattr(event.message, "text"):
                return

            message_text = event.message.text.strip().lower()

            # プロフィール情報取得コマンド
            if message_text == "profile":
                await self._handle_profile_request(event)
                return

            # 通常の鸚鵡返し処理（最小ログ）
            reply_text = event.message.text
            messages = [TextMessage(text=reply_text)]

            await self.line_bot_api.reply_message(
                ReplyMessageRequest(reply_token=event.reply_token, messages=messages)
            )

        except Exception as e:
            # 最小限のエラーログ（詳細なスタックトレースは削除）
            self.logger.error(f"メッセージ処理失敗: {type(e).__name__}")
            await self._handle_message_error(e, event)

    async def _handle_profile_request(self, event: MessageEvent) -> None:
        """
        プロフィール情報取得処理

        Args:
            event (MessageEvent): メッセージイベント
        """
        try:
            # ユーザーIDを取得
            user_id = getattr(event.source, "user_id", None)
            if not user_id:
                error_message = "ユーザーIDが取得できませんでした。"
                await self._send_reply(event.reply_token, error_message)
                return

            # プロフィール情報を取得
            profile = await self.line_bot_api.get_profile(user_id)

            # プロフィール情報をフォーマット
            profile_text = (
                f"プロフィール情報\n"
                f"表示名: {profile.display_name}\n"
                f"ユーザーID: {profile.user_id}\n"
                f"プロフィール画像: {'あり' if profile.picture_url else 'なし'}\n"
                f"ステータス: {profile.status_message if profile.status_message else '未設定'}\n"
                f"画像URL: {profile.picture_url if profile.picture_url else 'なし'}"
            )

            await self._send_reply(event.reply_token, profile_text)

        except Exception as e:
            # 最小限のエラーログ（詳細なスタックトレースは削除）
            user_id = getattr(event.source, "user_id", "unknown")
            self.logger.error(f"プロフィール取得失敗[{user_id}]: {type(e).__name__}")

            # 高速エラー解析とメッセージ決定
            error_msg = await self._analyze_and_get_profile_error_message(e)
            await self._send_reply(event.reply_token, error_msg)

    async def _analyze_and_get_profile_error_message(self, error: Exception) -> str:
        """
        プロフィール取得エラーを解析し、適切なユーザーメッセージを返す（LINE公式ドキュメント準拠）

        Args:
            error (Exception): 発生したエラー

        Returns:
            str: ユーザーに表示するエラーメッセージ
        """
        try:
            analyzer = AsyncLineErrorAnalyzer()
            analysis_result = await analyzer.analyze(error, ApiPattern.USER_PROFILE)

            # LINE公式ドキュメント準拠: 400, 404のみ
            status_code = analysis_result.status_code

            if status_code == 400:
                # Bad Request - 無効なユーザーIDなど
                return "❌ 無効なユーザーIDが指定されています。"
            elif status_code == 404:
                # Not Found - ユーザーがbotをブロックしているか友だち追加していない
                return "友だち追加してね！"
            else:
                # その他のエラー（想定外）
                return "❌ プロフィール情報の取得中にエラーが発生しました。"

        except Exception:
            # analyzer失敗時のフォールバック（高速）
            return "❌ プロフィール情報を取得できませんでした。友だち追加をお試しください。"

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
            # 高速エラー解析（重要なカテゴリーのみ詳細ログ）
            analyzer = AsyncLineErrorAnalyzer()
            analysis_result = await analyzer.analyze(error, ApiPattern.MESSAGE_PUSH)

            # 重要エラーのみ詳細ログ、その他は簡潔に
            if analysis_result.category == ErrorCategory.RATE_LIMIT:
                retry_time = analysis_result.retry_after or 60
                self.logger.warning(f"レート制限[{user_id}]: {retry_time}秒待機")
            elif analysis_result.category == ErrorCategory.SERVER_ERROR:
                self.logger.error(
                    f"サーバーエラー[{user_id}]: リトライ={analysis_result.is_retryable}"
                )
            elif analysis_result.category == ErrorCategory.INVALID_REPLY_TOKEN:
                self.logger.warning(f"無効ReplyToken[{user_id}]: トークン期限切れ")
            else:
                self.logger.error(
                    f"メッセージエラー[{user_id}]: {analysis_result.category}"
                )

        except Exception:
            # analyzer失敗時のフォールバック（最小限）
            self.logger.error(f"メッセージ処理失敗[{user_id}]: {type(error).__name__}")

    async def _send_reply(self, reply_token: str, text: str) -> None:
        """
        返信メッセージを送信

        Args:
            reply_token (str): 返信トークン
            text (str): 送信するテキスト
        """
        try:
            messages = [TextMessage(text=text)]
            await self.line_bot_api.reply_message(
                ReplyMessageRequest(reply_token=reply_token, messages=messages)
            )
        except Exception as e:
            # 簡潔な返信エラーログ
            self.logger.error(f"返信送信失敗: {type(e).__name__}")

            # 重要エラーのみ詳細チェック（高速化）
            try:
                analyzer = AsyncLineErrorAnalyzer()
                analysis_result = await analyzer.analyze(e, ApiPattern.REPLY_MESSAGE)

                # Reply Token関連エラーのみ特別ログ
                if analysis_result.category == ErrorCategory.INVALID_REPLY_TOKEN:
                    self.logger.warning("Reply Token期限切れ: 新しいイベントが必要")
                elif analysis_result.status_code == 429:
                    retry_time = analysis_result.retry_after or 60
                    self.logger.warning(f"返信レート制限: {retry_time}秒待機")

            except Exception:
                # analyzer失敗時は何もしない（高速化のため）
                pass
