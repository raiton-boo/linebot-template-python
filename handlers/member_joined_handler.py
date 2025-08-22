"""
メンバー参加イベントハンドラ
グループに新しいメンバーが参加した際の処理
"""

from linebot.v3.messaging import TextMessage, ReplyMessageRequest
from linebot.v3.webhooks import MemberJoinedEvent

from .base_handler import BaseEventHandler


class MemberJoinedEventHandler(BaseEventHandler):
    """
    MemberJoinedEventを処理するハンドラ
    """

    async def handle(self, event: MemberJoinedEvent) -> None:
        """
        メンバー参加イベントを処理

        Args:
            event (MemberJoinedEvent): メンバー参加イベント
        """
        try:
            # 参加したユーザー数を取得
            joined_members = event.joined.members
            member_count = len(joined_members)

            group_id = getattr(event.source, "group_id", "unknown")
            self.logger.info(
                f"グループに {member_count} 人のメンバーが参加しました: {group_id}"
            )

            # 歓迎メッセージ
            if member_count == 1:
                welcome_message = "新しいメンバーが参加しました！\nようこそ！"
            else:
                welcome_message = (
                    f"新しく {member_count} 人のメンバーが参加しました！\nようこそ！"
                )

            messages = [TextMessage(text=welcome_message)]

            await self.line_bot_api.reply_message(
                ReplyMessageRequest(reply_token=event.reply_token, messages=messages)
            )

            self.logger.info(f"メンバー参加歓迎メッセージを送信しました: {group_id}")

        except Exception as e:
            await self.handle_error(e, event)
