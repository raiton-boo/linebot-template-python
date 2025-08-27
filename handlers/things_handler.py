from typing import Any, Dict, Optional
from linebot.v3.webhooks import ThingsEvent
from linebot.v3.messaging import AsyncMessagingApi, TextMessage, ReplyMessageRequest
from .base_handler import BaseEventHandler


class ThingsEventHandler(BaseEventHandler):
    """
    ThingsEvent handler

    LINE Things デバイスからのイベントを処理します。
    IoTデバイスとの連携や各種センサーデータの受信時に発生します。
    """

    async def handle(self, event: ThingsEvent) -> None:
        """
        Process things event

        Args:
            event (ThingsEvent): Things event
        """
        try:
            device_id = event.things.device_id if event.things else "unknown"
            thing_type = event.things.type if event.things else "unknown"

            self.logger.info(
                f"Things event received: device_id={device_id}, type={thing_type}"
            )

            # デバイスタイプに応じた処理
            response_message = await self._process_things_event(event.things)

            # Reply message を送信（reply_tokenがある場合のみ）
            if hasattr(event, "reply_token") and event.reply_token:
                messages = [TextMessage(text=response_message)]
                reply_request = ReplyMessageRequest(
                    reply_token=event.reply_token, messages=messages
                )
                await self.line_bot_api.reply_message(reply_request)

        except Exception as error:
            await self._safe_error_handle(error, event)
            raise

    async def _process_things_event(self, things) -> str:
        """
        Process specific things event based on device type

        Args:
            things: Things event data

        Returns:
            str: Response message for the user
        """
        device_id = things.device_id if things else "unknown"
        thing_type = things.type if things else "unknown"

        if thing_type == "link":
            return f"🔗 IoTデバイス（{device_id}）が正常に接続されました。"
        elif thing_type == "unlink":
            return f"🔌 IoTデバイス（{device_id}）の接続が解除されました。"
        elif thing_type == "scenarioResult":
            return f"⚡ IoTデバイス（{device_id}）からシナリオ実行結果を受信しました。"
        else:
            return f"📱 IoTデバイス（{device_id}）からイベントを受信しました。\nタイプ: {thing_type}"

    async def _error_handle(
        self,
        error: Exception,
        event: ThingsEvent,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Handle error during things event processing"""
        try:
            self.logger.error(
                f"Things handler error: {type(error).__name__} - {str(error)}",
                exc_info=True,
            )
        except Exception:
            pass
