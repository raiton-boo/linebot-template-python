import logging
from .base_command import BaseCommand
from linebot.v3.messaging import ReplyMessageRequest, LocationMessage, TextMessage
from linebot.v3.webhooks import MessageEvent

logger = logging.getLogger(__name__)


class PoliceCommand(BaseCommand):
    """警察庁位置情報コマンド"""

    async def execute(self, event: MessageEvent, command: str) -> None:
        """警察庁本部の位置情報を送信"""
        try:
            police_hq_info = {
                "title": "警察庁",
                "address": "日本、〒100-8974 東京都千代田区霞が関2丁目1−2",
                "latitude": 35.674710,
                "longitude": 139.752040,
            }

            logger.info(f"Sending police HQ location: {police_hq_info['address']}")

            # 位置情報メッセージを送信
            await self.api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[
                        LocationMessage(
                            title=police_hq_info["title"],
                            address=police_hq_info["address"],
                            latitude=police_hq_info["latitude"],
                            longitude=police_hq_info["longitude"],
                        ),
                        TextMessage(text="つかまれ！！"),
                    ],
                )
            )

        except Exception as e:
            logger.error(f"Police command error: {e}")
            await self._reply_error(event, "警察庁本部の位置情報送信に失敗しました")
