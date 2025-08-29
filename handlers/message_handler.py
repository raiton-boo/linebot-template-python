from typing import Dict, Any, Optional

from linebot.v3.webhooks import (
    MessageEvent,
    Event,
    TextMessageContent,
    ImageMessageContent,
    AudioMessageContent,
    VideoMessageContent,
    StickerMessageContent,
    LocationMessageContent,
    FileMessageContent,
)
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
    """メッセージイベントハンドラ"""

    def __init__(self, line_bot_api: AsyncMessagingApi):
        super().__init__(line_bot_api)

        # メッセージコンテンツタイプ別ハンドラーマップ
        self.message_handlers: Dict[type, BaseMessageHandler] = {
            TextMessageContent: TextMessageHandler(line_bot_api),
            ImageMessageContent: ImageMessageHandler(line_bot_api),
            AudioMessageContent: AudioMessageHandler(line_bot_api),
            VideoMessageContent: VideoMessageHandler(line_bot_api),
            StickerMessageContent: StickerMessageHandler(line_bot_api),
            LocationMessageContent: LocationMessageHandler(line_bot_api),
            FileMessageContent: FileMessageHandler(line_bot_api),
        }

    async def handle(self, event: Event) -> None:
        """メッセージイベントの処理"""
        if not isinstance(event, MessageEvent):
            return

        # メッセージコンテンツのタイプを取得
        message_content_type = type(event.message)

        handler = self.message_handlers.get(message_content_type)

        if handler:
            await handler.safe_handle(event)
        else:
            await self._handle_unsupported_message_type(event, message_content_type)

    async def _handle_unsupported_message_type(
        self, event: MessageEvent, message_content_type: type
    ) -> None:
        """未対応メッセージタイプの処理"""
        content_type_name = (
            message_content_type.__name__ if message_content_type else "unknown"
        )
        self.logger.warning(f"Unsupported message type: {content_type_name}")

        try:
            response = f"申し訳ございません。{content_type_name}タイプのメッセージには、まだ対応しておりません。"

            await self.line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token, messages=[TextMessage(text=response)]
                )
            )
        except Exception as reply_error:
            self.logger.error(
                f"Failed to reply for unsupported message content type: {reply_error}"
            )

    async def _error_handle(
        self, error: Exception, event: Event, context: Optional[Dict[str, Any]] = None
    ) -> None:
        """エラーハンドリング"""
        try:
            if isinstance(event, MessageEvent):
                message_content_type = type(event.message)
                content_type_name = (
                    message_content_type.__name__ if message_content_type else "unknown"
                )
                user_id = getattr(event.source, "user_id", "unknown")

                self.logger.error(
                    f"Message handler error ({content_type_name}): "
                    f"{type(error).__name__} - {str(error)}",
                    exc_info=True,
                )

            if context:
                self.logger.error(f"Error context: {context}")

        except Exception:
            pass
