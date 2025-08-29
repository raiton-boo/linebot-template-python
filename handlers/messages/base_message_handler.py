import logging
from abc import ABC, abstractmethod
from typing import Any, Optional, Dict

from linebot.v3.webhooks import MessageEvent
from linebot.v3.messaging import AsyncMessagingApi, ReplyMessageRequest, TextMessage

logger = logging.getLogger(__name__)


class BaseMessageHandler(ABC):
    """メッセージハンドラの基底クラス"""

    def __init__(self, line_bot_api: AsyncMessagingApi) -> None:
        self.line_bot_api = line_bot_api
        self.logger = logger.getChild(self.__class__.__name__)

    @abstractmethod
    async def handle(self, event: MessageEvent) -> None:
        """メッセージ処理（継承先で実装）"""
        pass

    async def safe_handle(self, event: MessageEvent) -> None:
        """安全なメッセージ処理（エラーハンドリング付き）"""
        try:
            await self.handle(event)
        except Exception as error:
            await self._handle_message_error(error, event)

    async def _handle_message_error(
        self,
        error: Exception,
        event: MessageEvent,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """メッセージ処理エラーのハンドリング"""
        try:
            error_info = self._extract_message_error_info(error, event, context)

            if self._is_api_error(error):
                self._log_api_error(error_info)
                await self._handle_api_error(error, event)
            elif self._is_user_input_error(error):
                self._log_user_input_error(error_info)
                await self._send_user_error_message(event)
            else:
                self._log_processing_error(error_info)
                await self._send_system_error_message(event)

            await self._custom_message_error_handling(error, event, context)

        except Exception as error_handling_error:
            self.logger.critical(
                f"Message error handler failed in {self.__class__.__name__}: {str(error_handling_error)}",
                exc_info=True,
            )

    def _extract_message_error_info(
        self,
        error: Exception,
        event: MessageEvent,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """メッセージエラー情報の構造化"""
        return {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "message_type": getattr(event.message, "type", "unknown"),
            "message_id": getattr(event.message, "id", "unknown"),
            "handler_class": self.__class__.__name__,
            "user_id": getattr(getattr(event, "source", None), "user_id", "unknown"),
            "reply_token": getattr(event, "reply_token", None),
            "context": context or {},
        }

    def _is_api_error(self, error: Exception) -> bool:
        """LINE API関連エラーかどうかの判定"""
        api_error_indicators = {
            "api",
            "authentication",
            "rate limit",
            "quota",
            "invalid token",
        }
        error_message = str(error).lower()
        return any(indicator in error_message for indicator in api_error_indicators)

    def _is_user_input_error(self, error: Exception) -> bool:
        """ユーザー入力関連エラーかどうかの判定"""
        user_error_indicators = {"invalid", "format", "length", "unsupported"}
        error_message = str(error).lower()
        return any(indicator in error_message for indicator in user_error_indicators)

    def _log_api_error(self, error_info: Dict[str, Any]) -> None:
        """API関連エラーのログ出力"""
        self.logger.error(
            f"API Error {error_info['handler_class']}: ",
            f"{error_info['error_type']} - {error_info['error_message']} ",
            f"(Message: {error_info['message_type']}, User: {error_info['user_id']})",
            extra=error_info,
            exc_info=True,
        )

    def _log_user_input_error(self, error_info: Dict[str, Any]) -> None:
        """ユーザー入力関連エラーのログ出力"""
        self.logger.info(
            f"User Input Error {error_info['handler_class']}: "
            f"{error_info['error_type']} - {error_info['error_message'][:50]}... "
            f"(User: {error_info['user_id']})",
            extra=error_info,
        )

    def _log_processing_error(self, error_info: Dict[str, Any]) -> None:
        """一般的な処理エラーのログ出力"""
        self.logger.warning(
            f"Processing Error {error_info['handler_class']}: "
            f"{error_info['error_type']} - {error_info['error_message'][:100]}... "
            f"(Message: {error_info['message_type']}, User: {error_info['user_id']})",
            extra=error_info,
        )

    async def _handle_api_error(self, error: Exception, event: MessageEvent) -> None:
        """API関連エラーの処理"""
        pass

    async def _send_user_error_message(self, event: MessageEvent) -> None:
        """ユーザー向けエラーメッセージの送信"""
        try:
            await self.line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[
                        TextMessage(
                            text="申し訳ありません。入力内容に問題があるようです。もう一度お試しください。"
                        )
                    ],
                )
            )
        except Exception as reply_error:
            self.logger.error(f"Failed to send user error message: {reply_error}")

    async def _send_system_error_message(self, event: MessageEvent) -> None:
        """システムエラーメッセージの送信"""
        try:
            await self.line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[
                        TextMessage(
                            text="申し訳ありません。システムエラーが発生しました。しばらく経ってからもう一度お試しください。"
                        )
                    ],
                )
            )
        except Exception as reply_error:
            self.logger.error(f"Failed to send system error message: {reply_error}")

    async def _custom_message_error_handling(
        self,
        error: Exception,
        event: MessageEvent,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """サブクラスでオーバーライドして独自のメッセージエラー処理を追加"""
        pass

    def get_user_id(self, event: MessageEvent) -> str:
        """ユーザーIDを安全に取得"""
        return getattr(getattr(event, "source", None), "user_id", "unknown")

    def get_message_text(self, event: MessageEvent) -> Optional[str]:
        """メッセージテキストを安全に取得"""
        return getattr(getattr(event, "message", None), "text", None)
