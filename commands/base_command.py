import logging
from abc import ABC, abstractmethod
from linebot.v3.messaging import (
    AsyncMessagingApi,
    ReplyMessageRequest,
    TextMessage,
)
from linebot.v3.webhooks import MessageEvent

logger = logging.getLogger(__name__)


class BaseCommand(ABC):
    """コマンドの基底クラス"""
    
    def __init__(self, api: AsyncMessagingApi):
        self.api = api

    @abstractmethod
    async def execute(self, event: MessageEvent, command: str) -> None:
        """コマンドを実行する（サブクラスで実装）"""
        pass

    async def _reply_text(self, event: MessageEvent, text: str) -> None:
        """シンプルなテキストメッセージで返信"""
        await self.api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=text)]
            )
        )

    async def _reply_error(self, event: MessageEvent, error_message: str = None) -> None:
        """エラーメッセージで返信"""
        if error_message:
            text = f"コマンドの実行中にエラーが発生しました: {error_message}"
        else:
            text = "コマンドの実行中にエラーが発生しました。"
        
        await self._reply_text(event, text)