from typing import Any, Dict, Optional

from linebot.v3.webhooks import BeaconEvent
from linebot.v3.messaging import AsyncMessagingApi, TextMessage, ReplyMessageRequest

from .base_handler import BaseEventHandler


class BeaconEventHandler(BaseEventHandler):
    """ビーコンイベントハンドラ"""

    async def handle(self, event: BeaconEvent) -> None:
        """ビーコンイベントの処理"""
        beacon_hwid = event.beacon.hwid if event.beacon else None
        beacon_type = event.beacon.type if event.beacon else None

        self.logger.info(f"Get Beacon event")

        if beacon_type == "enter":
            response_message = f"Beaconエリアに入りました（ID: {beacon_hwid}）"
        elif beacon_type == "leave":
            response_message = f"Beaconエリアから離れました（ID: {beacon_hwid}）"
        else:
            response_message = f"Beaconを検出しました（Type: {beacon_type}）"

        if event.reply_token:
            await self.line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=response_message)],
                )
            )
