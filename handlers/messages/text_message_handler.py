from typing import Any, Optional, Dict
from linebot.v3.webhooks import MessageEvent, UserSource
from linebot.v3.messaging import (
    ReplyMessageRequest,
    TextMessage,
    ShowLoadingAnimationRequest,
)

from .base_message_handler import BaseMessageHandler


class TextMessageHandler(BaseMessageHandler):
    """テキストメッセージハンドラ"""

    async def handle(self, event: MessageEvent) -> None:
        """テキストメッセージの処理"""
        user_id = self.get_user_id(event)
        text = self.get_message_text(event)

        self.logger.info(f"Get Message event type for {event.message.type}")

        # ローディングアニメーション処理
        if text.lower() in ["ローディング", "loading"]:
            await self._handle_loading_animation(event)
            return

        response = self._generate_response(text.strip())

        if response:  # レスポンスがある場合のみ送信
            await self.line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token, messages=[TextMessage(text=response)]
                )
            )

    async def _handle_loading_animation(self, event: MessageEvent) -> None:
        """ローディングアニメーション処理"""
        if isinstance(event.source, UserSource):
            await self.line_bot_api.show_loading_animation(
                ShowLoadingAnimationRequest(
                    chatId=event.source.user_id, loadingSeconds=5
                )
            )
        else:
            await self.line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[
                        TextMessage(
                            text="ローディングアニメーションはユーザーチャットでのみ利用可能です。"
                        )
                    ],
                )
            )

    def _generate_response(self, text: str) -> Optional[str]:
        """テキストに基づいた応答を生成"""
        text_lower = text.lower()

        if any(
            greeting in text_lower
            for greeting in ["こんにちは", "おはよう", "こんばんは", "hello", "hi"]
        ):
            return "こんにちは！お元気ですか？"
        elif any(help_word in text_lower for help_word in ["ヘルプ", "help", "使い方"]):
            return "使用可能なコマンド:\n- こんにちは: 挨拶\n- ローディング: ローディングアニメーション\n- ヘルプ: このメッセージ"
        elif any(thanks in text_lower for thanks in ["ありがとう", "thank", "thanks"]):
            return "どういたしまして！何かお手伝いできることがあればお知らせください。"
        elif "?" in text or "？" in text:
            return "申し訳ございませんが、まだその質問にはお答えできません。"
        elif len(text) > 100:
            return (
                "長いメッセージをありがとうございます！内容を確認させていただきました。"
            )
        else:
            # 特定のパターンにマッチしない場合は応答しない
            return None

    async def _custom_message_error_handling(
        self,
        error: Exception,
        event: MessageEvent,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """テキストメッセージ特有のエラーハンドリング"""
        if isinstance(error, ValueError):
            self.logger.info(f"Text validation error: {error}")
        elif "loading" in str(error).lower():
            self.logger.warning(f"Loading animation error: {error}")
            try:
                await self.line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[
                            TextMessage(
                                text="ローディングアニメーションの実行に失敗しました。"
                            )
                        ],
                    )
                )
            except Exception as reply_error:
                self.logger.error(
                    f"Loading error message sending failed: {reply_error}"
                )
