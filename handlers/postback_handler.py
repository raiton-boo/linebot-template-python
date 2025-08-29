from typing import Any, Dict, Optional

from linebot.v3.webhooks import PostbackEvent
from linebot.v3.messaging import AsyncMessagingApi, TextMessage, ReplyMessageRequest

from .base_handler import BaseEventHandler


class PostbackEventHandler(BaseEventHandler):
    """ポストバックイベントハンドラ"""

    async def handle(self, event: PostbackEvent) -> None:
        """ポストバックイベントの処理"""
        postback_data = event.postback.data if event.postback else None
        postback_params = (
            event.postback.params
            if event.postback and hasattr(event.postback, "params")
            else {}
        )

        self.logger.info(f"Get Postback event")

        response_message = await self._process_postback_data(
            postback_data, postback_params
        )

        if event.reply_token and response_message:
            await self.line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=response_message)],
                )
            )

    async def _process_postback_data(
        self, data: Optional[str], params: Dict[str, Any]
    ) -> Optional[str]:
        """ポストバックデータの処理"""
        if not data:
            return "ポストバックデータを受信しました。"

        # ポストバックデータの解析処理
        # if "action=buy" in data:
        #     return "購入処理を開始します。"
        # elif "action=info" in data:
        #     return "詳細情報を表示します。"
        # else:
        #     return f"ポストバックを受信しました: {data}"
