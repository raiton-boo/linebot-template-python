"""
グループ参加イベントハンドラ
ボットがグループに招待された際の処理を担当
"""

from linebot.v3.messaging import TextMessage, ReplyMessageRequest
from linebot.v3.webhooks import JoinEvent

from .base_handler import BaseEventHandler


class JoinEventHandler(BaseEventHandler):
    """
    グループ参加イベントを処理するハンドラ

    ボットがグループに招待された際に挨拶メッセージを送信します。
    """

    async def handle(self, event: JoinEvent) -> None:
        """
        グループ参加イベントを処理

        Args:
            event (JoinEvent): グループ参加イベント
        """
        try:
            group_id = getattr(event.source, "group_id", "unknown")
            self.logger.info(f"グループに参加しました: {group_id}")

            # グループ参加時の挨拶メッセージ
            greeting_message = (
                "グループに招待していただき、ありがとうございます！\n"
                "何かメッセージを送ってみてください。"
            )
            messages = [TextMessage(text=greeting_message)]

            await self.line_bot_api.reply_message(
                ReplyMessageRequest(reply_token=event.reply_token, messages=messages)
            )

            self.logger.info(f"グループ参加挨拶を送信しました: {group_id}")

        except Exception as e:
            await self.handle_error(e, event)
