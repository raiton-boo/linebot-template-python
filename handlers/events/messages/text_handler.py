import asyncio
import logging
import time

from linebot.v3.messaging import (
    AsyncMessagingApi,
    ReplyMessageRequest,
    TextMessage,
    MentionSubstitutionObject,
    AllMentionTarget,
    UserMentionTarget,
    TextMessageV2,
    ShowLoadingAnimationRequest,
)
from linebot.v3.webhooks import MessageEvent, UserSource, GroupSource, RoomSource

logger = logging.getLogger(__name__)


class TextHandler:
    """テキストメッセージを処理するハンドラー"""

    def __init__(self, api: AsyncMessagingApi):
        self.api = api

    async def handle(self, event: MessageEvent) -> None:
        """テキストメッセージの処理"""
        try:
            message_text = event.message.text
            logger.debug(f"Received text: {message_text}")

            # コマンド（/で始まる）か通常のテキストかを判別
            if message_text.startswith("/"):
                await self._handle_command(event, message_text)
            else:
                await self._handle_regular_text(event, message_text)

        except Exception as e:
            logger.error(f"TextHandler error: {e}")

    async def _handle_command(self, event: MessageEvent, command: str) -> None:
        """スラッシュコマンドを処理"""
        start_time = time.time()

        if command == "/help":
            response_text = (
                "利用可能なコマンド:\n"
                "/help - ヘルプ表示\n"
                "/status - ステータス確認\n"
                "/ping - 疎通確認\n"
                "/loading - ローディングアニメーション表示（個チャのみ）\n"
                "/mention - メンション機能テスト（グループチャットのみ）\n"
                "/allmention - 全員メンション機能テスト (グループチャットのみ・極力使わないように)"
            )
        elif command == "/status":
            response_text = "Bot is running normally"
        elif command == "/ping":
            # 応答時間を測定してレスポンス
            await self.api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[
                        TextMessage(
                            text="Pong!", quote_token=event.message.quote_token
                        ),
                        TextMessage(text=f"応答時間: {time.time() - start_time:.3f}秒"),
                    ],
                )
            )
            return
        elif command == "/loading":
            await self._handle_loading_animation(event)
            return
        elif command == "/mention":
            await self._handle_mention_test(event)
            return
        elif command == "/allmention":
            await self._handle_all_mention_test(event)
            return
        else:
            response_text = (
                f"未知のコマンド: {command}\n/help でコマンド一覧を確認してください。"
            )

        await self._reply_text(event, response_text)

    async def _handle_loading_animation(self, event: MessageEvent) -> None:
        """ローディングアニメーションを表示"""
        try:
            # 個人チャット以外では利用不可
            if not isinstance(event.source, UserSource):
                response_text = (
                    "ローディングアニメーションは個人チャットでのみ利用できます。"
                )
                await self._reply_text(event, response_text)
                return

            user_id = event.source.user_id
            logger.info(f"Starting loading animation for user: {user_id}")

            # 5秒間のローディングアニメーションを開始
            await self.api.show_loading_animation(
                ShowLoadingAnimationRequest(chat_id=user_id, loading_seconds=5)
            )

            # アニメーション完了を待ってから完了メッセージ送信
            await asyncio.sleep(5.5)  # 少し余裕をもって待機
            await self._reply_text(event, "ローディング完了！")

        except Exception as e:
            logger.error(f"Loading animation error: {e}")
            await self._reply_text(
                event, "ローディングアニメーションの表示中にエラーが発生しました。"
            )

    async def _handle_mention_test(self, event: MessageEvent) -> None:
        """特定ユーザーのメンション機能をテスト"""
        try:
            if isinstance(event.source, UserSource):
                # 個人チャットではメンション機能は無効
                response_text = "個人チャットではメンション機能は利用できません。"
                await self._reply_text(event, response_text)
                return

            # グループチャット・ルームでのメンション処理
            if isinstance(event.source, (GroupSource, RoomSource)):
                user_id = event.source.user_id

                # メンション付きメッセージを送信
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
                return

            # その他の場合（通常は発生しない）
            await self._reply_text(event, "メンション機能を利用できません。")

        except Exception as e:
            logger.error(f"Mention test error: {e}")
            await self._reply_text(
                event, "メンション機能のテスト中にエラーが発生しました。"
            )

    async def _handle_all_mention_test(self, event: MessageEvent) -> None:
        """全員メンション機能をテスト（使用注意）"""
        try:
            if isinstance(event.source, UserSource):
                # 個人チャットでは全員メンション不可
                response_text = "個人チャットでは全員メンション機能は利用できません。"
                await self._reply_text(event, response_text)
                return

            # グループチャット・ルームでの全員メンション
            if isinstance(event.source, (GroupSource, RoomSource)):
                user_id = event.source.user_id

                # 全員メンション付きメッセージを送信
                # 注意：全員に通知が行くため、テスト以外では使用を控える
                await self.api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[
                            TextMessageV2(
                                text="{1} 全員メンションテストです。",
                                substitution={
                                    1: MentionSubstitutionObject(
                                        mentionee=AllMentionTarget()
                                    )
                                },
                                quote_token=event.message.quote_token,
                            )
                        ],
                    )
                )
                return

            # その他の場合
            await self._reply_text(event, "全員メンション機能を利用できません。")

        except Exception as e:
            logger.error(f"All mention test error: {e}")
            await self._reply_text(
                event, "全員メンション機能のテスト中にエラーが発生しました。"
            )

    async def _handle_regular_text(self, event: MessageEvent, text: str) -> None:
        """通常のテキストメッセージ処理（エコー機能）"""
        await self._reply_text(event, text)

    async def _reply_text(self, event: MessageEvent, text: str) -> None:
        """シンプルなテキストメッセージで返信"""
        await self.api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token, messages=[TextMessage(text=text)]
            )
        )
