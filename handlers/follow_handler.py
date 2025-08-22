"""
フォローイベントハンドラ
ユーザーがボットをフォローした際の処理
"""

from linebot.v3.messaging import TextMessage, ReplyMessageRequest
from linebot.v3.webhooks import FollowEvent

from linebot_error_analyzer import AsyncLineErrorAnalyzer

from .base_handler import BaseEventHandler


class FollowEventHandler(BaseEventHandler):
    """
    FollowEventを処理するハンドラ
    """

    async def handle(self, event: FollowEvent) -> None:
        """
        フォローイベントを処理

        Args:
            event (FollowEvent): フォローイベント
        """
        try:
            # 歓迎メッセージを送信
            welcome_message = (
                "フォローありがとうございます！\n何かメッセージを送ってみてください。"
            )
            messages = [TextMessage(text=welcome_message)]

            await self.line_bot_api.reply_message(
                ReplyMessageRequest(reply_token=event.reply_token, messages=messages)
            )

        except Exception as e:
            # 独自エラー処理
            self.logger.exception(f"フォロー処理エラー: {type(e).__name__}: {e}")