import logging
from abc import ABC, abstractmethod
from typing import Any, Optional, Dict

from linebot.v3.messaging import AsyncMessagingApi
from linebot.v3.webhooks import Event

logger = logging.getLogger(__name__)


class BaseEventHandler(ABC):
    """
    Event handler base class

    全てのハンドラはこのクラスを継承し、handle および _error_handle メソッドを実装する必要があります。
    """

    def __init__(self, line_bot_api: AsyncMessagingApi) -> None:
        """
        Initialize handler

        Args:
            line_bot_api (AsyncMessagingApi): LINE Bot API client
        """
        self.line_bot_api = line_bot_api
        self.logger = logger.getChild(self.__class__.__name__)

    @abstractmethod
    async def handle(self, event: Event) -> None:
        """
        Process event (abstract method)

        Args:
            event (Event): Target event to process

        Raises:
            Exception: Error occurred during event processing
        """
        pass

    @abstractmethod
    async def _error_handle(
        self, error: Exception, event: Event, context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Handle error (abstract method - private access only)

        Note: この実装は例外を投げてはいけません。全ての例外を内部でキャッチして処理してください。

        Args:
            error (Exception): Occurred error
            event (Event): Event where error occurred
            context (Optional[Dict[str, Any]]): Context information when error occurred
        """
        pass

    async def _safe_error_handle(
        self, error: Exception, event: Event, context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Safe error handling wrapper (private method)

        Args:
            error (Exception): Occurred error
            event (Event): Event where error occurred
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
