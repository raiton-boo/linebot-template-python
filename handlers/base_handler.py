import logging
from abc import ABC, abstractmethod
from typing import Any, Optional, Dict

from linebot.v3.messaging import AsyncMessagingApi
from linebot.v3.webhooks import Event

logger = logging.getLogger(__name__)


class BaseEventHandler(ABC):
    """イベントハンドラの基底クラス"""

    def __init__(self, line_bot_api: AsyncMessagingApi) -> None:
        self.line_bot_api = line_bot_api
        self.logger = logger.getChild(self.__class__.__name__)

    @abstractmethod
    async def handle(self, event: Event) -> None:
        """
        イベント処理（継承先で実装）

        Args:
            event: 処理対象のイベント
        """
        pass

    async def safe_handle(self, event: Event) -> None:
        """
        安全なイベント処理（エラーハンドリング付き）

        Args:
            event: 処理対象のイベント
        """
        try:
            await self.handle(event)
        except Exception as error:
            await self._handle_error(error, event)
            # 必要に応じて再スローするかどうかを決定
            await self._handle_error(error, event)

    async def _handle_error(
        self, error: Exception, event: Event, context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        エラーハンドリングの具象実装

        サブクラスでオーバーライド可能
        """
        try:
            error_info = self._extract_error_info(error, event, context)

            if self._is_critical_error(error):
                self._log_critical_error(error_info)
                await self._handle_critical_error(error, event)
            else:
                self._log_standard_error(error_info)
                await self._handle_standard_error(error, event)

            # カスタムエラーハンドリングのフック
            await self._custom_error_handling(error, event, context)

        except Exception as error_handling_error:
            self.logger.critical(
                f"Error handler failed in {self.__class__.__name__}: {str(error_handling_error)}",
                exc_info=True,
            )

    def _extract_error_info(
        self, error: Exception, event: Event, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """エラー情報の構造化"""
        return {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "event_type": type(event).__name__,
            "handler_class": self.__class__.__name__,
            "user_id": getattr(getattr(event, "source", None), "user_id", "unknown"),
            "context": context or {},
        }

    def _is_critical_error(self, error: Exception) -> bool:
        """重要エラーかどうか判定"""
        critical_keywords = {
            "rate",
            "limit",
            "timeout",
            "server",
            "quota",
            "authentication",
        }
        error_message = str(error).lower()
        return any(keyword in error_message for keyword in critical_keywords)

    def _log_critical_error(self, error_info: Dict[str, Any]) -> None:
        """重要エラーのログ出力"""
        self.logger.error(
            f"CRITICAL ERROR in {error_info['handler_class']}: "
            f"{error_info['error_type']} - {error_info['error_message']} "
            f"(Event: {error_info['event_type']}, User: {error_info['user_id']})",
            extra=error_info,
            exc_info=True,
        )

    def _log_standard_error(self, error_info: Dict[str, Any]) -> None:
        """通常エラーのログ出力"""
        self.logger.warning(
            f"Error in {error_info['handler_class']}: "
            f"{error_info['error_type']} - {error_info['error_message'][:100]}... "
            f"(User: {error_info['user_id']})",
            extra=error_info,
        )

    async def _handle_critical_error(self, error: Exception, event: Event) -> None:
        """重要エラーの処理（オーバーライド可能）"""
        pass

    async def _handle_standard_error(self, error: Exception, event: Event) -> None:
        """通常エラーの処理（オーバーライド可能）"""
        pass

    async def _custom_error_handling(
        self, error: Exception, event: Event, context: Optional[Dict[str, Any]] = None
    ) -> None:
        """カスタムエラーハンドリングのフック（サブクラスで実装）"""
        pass

    def get_user_id(self, event: Event) -> str:
        """イベントからユーザーIDを取得"""
        return getattr(getattr(event, "source", None), "user_id", "unknown")
