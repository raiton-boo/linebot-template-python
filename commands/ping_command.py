import time
from .base_command import BaseCommand
from linebot.v3.messaging import ReplyMessageRequest, TextMessage
from linebot.v3.webhooks import MessageEvent


class PingCommand(BaseCommand):
    """Pingコマンド"""
    
    async def execute(self, event: MessageEvent, command: str) -> None:
        """応答時間を測定して返信"""
        try:
            start_time = time.time()
            processing_time = time.time() - start_time
            
            await self.api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[
                        TextMessage(
                            text="ok!", 
                            quote_token=event.message.quote_token
                        ),
                        TextMessage(
                            text=f"time: {processing_time:.5f}秒"
                        ),
                    ],
                )
            )
        except Exception as e:
            await self._reply_error(event, f"応答時間の測定に失敗しました: {e}")