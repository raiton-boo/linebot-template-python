"""
プロフィール取得コマンド
ユーザーのプロフィール情報を取得する処理を担当
"""

from typing import Optional
from linebot.v3.messaging import MessagingApi, TextMessage, ReplyMessageRequest
from linebot.v3.webhooks import MessageEvent
from linebot_error_analyzer import AsyncLineErrorAnalyzer, ApiPattern, ErrorCategory
import logging


class GetProfileCommand:
    """
    プロフィール取得コマンドクラス
    """

    def __init__(self, line_bot_api: MessagingApi, logger: logging.Logger):
        """
        初期化

        Args:
            line_bot_api (MessagingApi): LINE Bot API
            logger (logging.Logger): ログ出力用
        """
        self.line_bot_api = line_bot_api
        self.logger = logger

    async def execute(self, event: MessageEvent) -> None:
        """
        プロフィール取得処理を実行

        Args:
            event (MessageEvent): メッセージイベント
        """
        await self._handle_profile_request(event)

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
                return "無効なユーザーIDが指定されています。"
            elif status_code == 404:
                # Not Found - ユーザーがbotをブロックしているか友だち追加していない
                return "友だち追加してね！"
            else:
                # その他のエラー（想定外）
                return "プロフィール情報の取得中にエラーが発生しました。"

        except Exception:
            # analyzer失敗時のフォールバック（高速）
            return "❌ プロフィール情報を取得できませんでした。友だち追加をお試しください。"

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
