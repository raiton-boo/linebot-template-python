from typing import Any, Optional, Dict
from linebot.v3.webhooks import MessageEvent
from linebot.v3.messaging import ReplyMessageRequest, TextMessage, LocationMessage

from .base_message_handler import BaseMessageHandler


class LocationMessageHandler(BaseMessageHandler):
    """位置情報メッセージハンドラ"""

    async def handle(self, event: MessageEvent) -> None:
        """位置情報メッセージの処理"""
        user_id = self.get_user_id(event)
        self.logger.info(f"Get Message event type for {event.message.type}")

        # 位置情報を取得
        location_info = self._get_location_info(event)

        if not location_info:
            response = "位置情報を受信しましたが、詳細を取得できませんでした。"
            await self.line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token, messages=[TextMessage(text=response)]
                )
            )
            return

        # 位置情報の分析
        analysis = self._analyze_location(location_info)

        # 応答をフォーマット
        response = self._format_location_response(location_info, analysis)

        await self.line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token, messages=[TextMessage(text=response)]
            )
        )

    def _get_location_info(self, event: MessageEvent) -> Dict[str, Any]:
        """位置情報を取得"""
        message = event.message

        # LocationMessageContentの属性を安全に取得
        location_info = {}

        try:
            # 各属性を安全に取得
            title = getattr(message, "title", None)
            address = getattr(message, "address", None)
            latitude = getattr(message, "latitude", None)
            longitude = getattr(message, "longitude", None)

            # 値が存在する場合のみ追加
            if title:
                location_info["title"] = title
            if address:
                location_info["address"] = address
            if latitude is not None:
                location_info["latitude"] = latitude
            if longitude is not None:
                location_info["longitude"] = longitude

        except Exception as e:
            self.logger.warning(f"位置情報属性取得エラー: {e}")

        return location_info

    def _analyze_location(self, location_info: Dict[str, Any]) -> Dict[str, Any]:
        """位置情報を分析"""
        lat = location_info.get("latitude")
        lng = location_info.get("longitude")

        analysis = {"region": "unknown", "timezone": "unknown", "type": "point"}

        if lat and lng:
            # 日本の大まかな地域判定
            if 35.0 <= lat <= 36.0 and 139.0 <= lng <= 140.0:
                analysis["region"] = "東京周辺"
                analysis["timezone"] = "JST"
            elif 34.0 <= lat <= 35.0 and 135.0 <= lng <= 136.0:
                analysis["region"] = "大阪周辺"
                analysis["timezone"] = "JST"
            elif 24.0 <= lat <= 26.5 and 123.0 <= lng <= 131.5:
                analysis["region"] = "沖縄"
                analysis["timezone"] = "JST"
            elif 43.0 <= lat <= 45.5 and 141.0 <= lng <= 146.0:
                analysis["region"] = "北海道"
                analysis["timezone"] = "JST"
            elif 30.0 <= lat <= 46.0 and 129.0 <= lng <= 146.0:
                analysis["region"] = "日本"
                analysis["timezone"] = "JST"

        return analysis

    def _format_location_response(
        self, location_info: Dict[str, Any], analysis: Dict[str, Any]
    ) -> str:
        """位置情報応答をフォーマット"""
        title = location_info.get("title", "位置情報")
        address = location_info.get("address", "住所不明")
        lat = location_info.get("latitude", "不明")
        lng = location_info.get("longitude", "不明")
        region = analysis.get("region", "不明")

        response_parts = [
            "位置情報を受信しました！",
            f"タイトル: {title}",
            f"住所: {address}",
            f"座標: {lat}, {lng}",
        ]

        if region != "unknown":
            response_parts.append(f"地域: {region}")

        response_parts.extend(["", "位置情報をありがとうございます！"])

        return "\n".join(response_parts)

    async def _custom_message_error_handling(
        self,
        error: Exception,
        event: MessageEvent,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """位置情報メッセージ特有のエラーハンドリング"""
        if "location" in str(error).lower():
            self.logger.warning(f"Location processing error: {error}")
        elif isinstance(error, ValueError):
            self.logger.info(f"Location validation error: {error}")
        elif "coordinate" in str(error).lower():
            self.logger.warning(f"Coordinate processing error: {error}")
