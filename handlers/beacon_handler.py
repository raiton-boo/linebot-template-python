from typing import Any, Dict, Optional

from linebot.v3.webhooks import BeaconEvent
from linebot.v3.messaging import AsyncMessagingApi, TextMessage, ReplyMessageRequest

from .base_handler import BaseEventHandler


class BeaconEventHandler(BaseEventHandler):
    """
    BeaconEvent handler

    ユーザーがビーコンに近づいた、または離れた際のイベントを処理します。
    """

    async def handle(self, event: BeaconEvent) -> None:
        """
        Process beacon event

        Args:
            event (BeaconEvent): Beacon event

        Raises:
            Exception: Error occurred during event processing
        """
        try:
            beacon_hwid = event.beacon.hwid if event.beacon else None
            beacon_type = event.beacon.type if event.beacon else None
            device_message = (
                event.beacon.dm
                if event.beacon and hasattr(event.beacon, "dm")
                else None
            )

            self.logger.info(f"Beacon event: type={beacon_type}, hwid={beacon_hwid}")

            # Beacon type に基づいてレスポンスメッセージを生成
            if beacon_type == "enter":
                response_message = f"Beacon エリアに入りました。（ID: {beacon_hwid}）"
            elif beacon_type == "leave":
                response_message = f"Beacon エリアから離れました。（ID: {beacon_hwid}）"
            else:
                response_message = f"Beacon を検出しました。（Type: {beacon_type}）"

            # Reply message を送信
            if event.reply_token:
                messages = [TextMessage(text=response_message)]
                reply_request = ReplyMessageRequest(
                    reply_token=event.reply_token, messages=messages
                )
                await self.line_bot_api.reply_message(reply_request)

        except Exception as error:
            await self._safe_error_handle(error, event)
            raise

    async def _error_handle(
        self,
        error: Exception,
        event: BeaconEvent,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Handle error

        Args:
            error (Exception): Occurred error
            event (BeaconEvent): Event where error occurred
            context (Optional[Dict[str, Any]]): Context information when error occurred
        """
        try:
            self.logger.error(
                f"Error handling beacon event: {type(error).__name__} - {str(error)}",
                exc_info=True,
            )
        except Exception:
            # 絶対に例外を投げてはいけません
            pass
