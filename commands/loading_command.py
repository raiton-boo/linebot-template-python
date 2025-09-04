import asyncio
import logging
from .base_command import BaseCommand
from linebot.v3.messaging import ShowLoadingAnimationRequest
from linebot.v3.webhooks import MessageEvent, UserSource

logger = logging.getLogger(__name__)


class LoadingCommand(BaseCommand):
    """ローディングアニメーションコマンド"""

    async def execute(self, event: MessageEvent, command: str) -> None:
        """ローディングアニメーションを表示"""
        try:
            # 個人チャット以外では利用不可
            if not isinstance(event.source, UserSource):
                await self._reply_text(
                    event,
                    "ローディングアニメーションは個人チャットでのみ利用できます。",
                )
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
            await self._reply_error(
                event, "ローディングアニメーションの表示に失敗しました"
            )
