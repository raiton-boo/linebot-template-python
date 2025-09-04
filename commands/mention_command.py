import logging
from .base_command import BaseCommand
from linebot.v3.messaging import (
    ReplyMessageRequest,
    TextMessageV2,
    MentionSubstitutionObject,
    UserMentionTarget,
    AllMentionTarget,
)
from linebot.v3.webhooks import MessageEvent, UserSource, GroupSource, RoomSource

logger = logging.getLogger(__name__)


class MentionCommand(BaseCommand):
    """メンションコマンド"""

    async def execute(self, event: MessageEvent, command: str) -> None:
        """メンション機能をテスト"""
        try:
            if isinstance(event.source, UserSource):
                # 個人チャットではメンション機能は無効
                await self._reply_text(
                    event, "個人チャットではメンション機能は利用できません。"
                )
                return

            # グループチャット・ルームでのメンション処理
            if isinstance(event.source, (GroupSource, RoomSource)):
                user_id = event.source.user_id

                if command == "/allmention":
                    # 全員メンション
                    await self._send_all_mention(event, user_id)
                else:
                    # 個人メンション
                    await self._send_user_mention(event, user_id)
                return

            # その他の場合
            await self._reply_text(event, "メンション機能を利用できません。")

        except Exception as e:
            logger.error(f"Mention command error: {e}")
            await self._reply_error(event, "メンション機能のテストに失敗しました")

    async def _send_user_mention(self, event: MessageEvent, user_id: str) -> None:
        """個人メンションを送信"""
        await self.api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    TextMessageV2(
                        text="{1} こんにちは！メンション機能のテストです。",
                        substitution={
                            1: MentionSubstitutionObject(
                                mentionee=UserMentionTarget(userId=user_id)
                            )
                        },
                        quote_token=event.message.quote_token,
                    )
                ],
            )
        )

    async def _send_all_mention(self, event: MessageEvent, user_id: str) -> None:
        """全員メンションを送信（注意：全員に通知）"""
        await self.api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    TextMessageV2(
                        text="{1} 全員メンションテストです。",
                        substitution={
                            1: MentionSubstitutionObject(mentionee=AllMentionTarget())
                        },
                        quote_token=event.message.quote_token,
                    )
                ],
            )
        )
