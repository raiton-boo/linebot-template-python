from .base_command import BaseCommand
from linebot.v3.webhooks import MessageEvent


class HelpCommand(BaseCommand):
    """ヘルプコマンド"""
    
    async def execute(self, event: MessageEvent, command: str) -> None:
        """ヘルプメッセージを表示"""
        from . import COMMAND_HELP_TEXT
        await self._reply_text(event, COMMAND_HELP_TEXT)