from typing import Any, Dict, Optional

from linebot.v3.webhooks import PostbackEvent
from linebot.v3.messaging import AsyncMessagingApi, TextMessage, ReplyMessageRequest

from .base_handler import BaseEventHandler


class PostbackEventHandler(BaseEventHandler):
    """
    PostbackEvent handler

    ユーザーがポストバックアクションを実行した際のイベントを処理します。
    """

    async def handle(self, event: PostbackEvent) -> None:
        """
        Process postback event

        Args:
            event (PostbackEvent): Postback event

        Raises:
            Exception: Error occurred during event processing
        """
        try:
            postback_data = event.postback.data if event.postback else None
            postback_params = (
                event.postback.params
                if event.postback and hasattr(event.postback, "params")
                else {}
            )

            self.logger.info(f"Postback event received: data={postback_data}")

            # Postback data を処理
            response_message = await self._process_postback_data(
                postback_data, postback_params
            )

            # Reply message を送信
            if event.reply_token and response_message:
                messages = [TextMessage(text=response_message)]
                reply_request = ReplyMessageRequest(
                    reply_token=event.reply_token, messages=messages
                )
                await self.line_bot_api.reply_message(reply_request)

        except Exception as error:
            await self._safe_error_handle(error, event)
            raise

    async def _process_postback_data(
        self, data: Optional[str], params: Dict[str, Any]
    ) -> Optional[str]:
        """
        Process postback data and return response message

        Args:
            data (Optional[str]): Postback data
            params (Dict[str, Any]): Postback parameters

        Returns:
            Optional[str]: Response message
        """
        if not data:
            return "Postback data を受信しました。"

        # Postback data を解析して適切なレスポンスを生成
        if "action=buy" in data:
            return "購入処理を開始します。"
        elif "action=info" in data:
            return "詳細情報を表示します。"
        else:
            return f"Postback を受信しました: {data}"

    async def _error_handle(
        self,
        error: Exception,
        event: PostbackEvent,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Handle error

        Args:
            error (Exception): Occurred error
            event (PostbackEvent): Event where error occurred
            context (Optional[Dict[str, Any]]): Context information when error occurred
        """
        try:
            self.logger.error(
                f"Error handling postback event: {type(error).__name__} - {str(error)}",
                exc_info=True,
            )
        except Exception:
            # 絶対に例外を投げてはいけません
            pass
