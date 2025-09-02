import logging
from linebot.v3.messaging import AsyncMessagingApi, ReplyMessageRequest, TextMessage
from linebot.v3.webhooks import BeaconEvent

logger = logging.getLogger(__name__)


class BeaconEventHandler:

    def __init__(self, api: AsyncMessagingApi):
        self.api = api

    async def handle(self, event: BeaconEvent) -> None:
        try:
            beacon = event.beacon
            beacon_type = beacon.type
            hwid = beacon.hwid

            logger.info(f"Beacon detected - Type: {beacon_type}, HWID: {hwid}")

            if beacon_type == "enter":
                response_text = f"ビーコンエリアに入りました！\n識別ID: {hwid}"
            elif beacon_type == "leave":
                response_text = f"ビーコンエリアから出ました。\n識別ID: {hwid}"
            else:
                response_text = (
                    f"ビーコンを検出しました。\nタイプ: {beacon_type}\n識別ID: {hwid}"
                )

            await self.api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=response_text)],
                )
            )

        except Exception as e:
            logger.error(f"BeaconEventHandler error: {e}")


def get_handlers(api: AsyncMessagingApi):
    beacon_handler = BeaconEventHandler(api)
    return {BeaconEvent: beacon_handler.handle}
