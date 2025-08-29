"""
Base message handler for specific message types
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Optional, Dict

from linebot.v3.webhooks import MessageEvent
from linebot.v3.messaging import AsyncMessagingApi

logger = logging.getLogger(__name__)


class BaseMessageHandler(ABC):
    """
    Message handler base class

    全てのメッセージハンドラはこのクラスを継承し、handle および _error_handle メソッドを実装する必要があります。
    """

    def __init__(self, line_bot_api: AsyncMessagingApi) -> None:
        """
        Initialize message handler

        Args:
            line_bot_api (AsyncMessagingApi): LINE Bot API client
        """
        self.line_bot_api = line_bot_api
        self.logger = logger.getChild(self.__class__.__name__)

    @abstractmethod
    async def handle(self, event: MessageEvent) -> None:
        """
        Process message event (abstract method)

        Args:
            event (MessageEvent): Target message event to process

        Raises:
            Exception: Error occurred during message processing
        """
        pass

    @abstractmethod
    async def _error_handle(
        self,
        error: Exception,
        event: MessageEvent,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Handle error (abstract method - private access only)

        Note: この実装は例外を投げてはいけません。全ての例外を内部でキャッチして処理してください。

        Args:
            error (Exception): Occurred error
            event (MessageEvent): Message event where error occurred
            context (Optional[Dict[str, Any]]): Context information when error occurred
        """
        pass

    async def _safe_error_handle(
        self,
        error: Exception,
        event: MessageEvent,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Safe error handling wrapper (private method)

        Args:
            error (Exception): Occurred error
            event (MessageEvent): Message event where error occurred
            context (Optional[Dict[str, Any]]): Context information when error occurred
        """
        try:
            await self._error_handle(error, event, context)
        except Exception as error_handling_error:
            # エラーハンドリングが失敗した場合の最低限のログ出力
            self.logger.critical(
                f"Error handler failed in {self.__class__.__name__}: {str(error_handling_error)}",
                exc_info=True,
            )
