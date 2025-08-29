from typing import Dict, Any, Optional

from linebot.v3.webhooks import MessageEvent, Event
from linebot.v3.messaging import AsyncMessagingApi, ReplyMessageRequest, TextMessage

from .base_handler import BaseEventHandler
from .messages import (
    TextMessageHandler,
    ImageMessageHandler,
    AudioMessageHandler,
    VideoMessageHandler,
    StickerMessageHandler,
    LocationMessageHandler,
    FileMessageHandler,
    BaseMessageHandler,
)


class MessageEventHandler(BaseEventHandler):
    """
    MessageEvent handler

    各メッセージタイプを専用ハンドラーに委譲し、
    公式SDKのパターンに従った統一された処理を提供
    """

    def __init__(self, line_bot_api: AsyncMessagingApi):
        """
        Initialize MessageEventHandler

        Args:
            line_bot_api (AsyncMessagingApi): LINE Bot API client
        """
        super().__init__(line_bot_api)

        # メッセージタイプ別ハンドラーマップ
        self.message_handlers: Dict[str, BaseMessageHandler] = {
            "text": TextMessageHandler(line_bot_api),
            "image": ImageMessageHandler(line_bot_api),
            "audio": AudioMessageHandler(line_bot_api),
            "video": VideoMessageHandler(line_bot_api),
            "sticker": StickerMessageHandler(line_bot_api),
            "location": LocationMessageHandler(line_bot_api),
            "file": FileMessageHandler(line_bot_api),
        }

    async def handle(self, event: Event) -> None:
        """
        Process message event

        Args:
            event (Event): イベント

        Raises:
            Exception: Error occurred during event processing
        """
        if not isinstance(event, MessageEvent):
            raise ValueError("Event is not a MessageEvent")

        # メッセージタイプを取得
        message_type = getattr(event.message, "type", "unknown")

        # 対応するハンドラーを取得
        handler = self.message_handlers.get(message_type)

        if handler:
            # 専用ハンドラーで処理
            await handler.handle(event)
        else:
            # 未対応のメッセージタイプ
            await self._handle_unsupported_message_type(event, message_type)

    async def _handle_unsupported_message_type(
        self, event: MessageEvent, message_type: str
    ) -> None:
        """
        未対応のメッセージタイプを処理

        Args:
            event (MessageEvent): メッセージイベント
            message_type (str): メッセージタイプ
        """
        self.logger.warning(f"Unsupported message type: {message_type}")

        try:
            response = f"申し訳ございません。{message_type}タイプのメッセージには、まだ対応しておりません。"

            await self.line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token, messages=[TextMessage(text=response)]
                )
            )
        except Exception as reply_error:
            self.logger.error(
                f"Failed to reply for unsupported message type: {reply_error}"
            )

    async def _error_handle(
        self, error: Exception, event: Event, context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        エラーハンドリング

        Args:
            error (Exception): エラー
            event (Event): イベント
            context (Optional[Dict[str, Any]]): コンテキスト情報
        """
        try:
            if isinstance(event, MessageEvent):
                message_type = getattr(event.message, "type", "unknown")
                user_id = getattr(event.source, "user_id", "unknown")

                self.logger.error(
                    f"Message handler error ({message_type}) from {user_id}: "
                    f"{type(error).__name__} - {str(error)}",
                    exc_info=True,
                )

            if context:
                self.logger.error(f"Error context: {context}")

        except Exception:
            # 絶対に例外を投げてはいけません
            pass
