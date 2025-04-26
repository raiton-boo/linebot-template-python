from linebot.v3.messaging import AsyncMessagingApi, ReplyMessageRequest, TextMessage
from linebot.v3.webhooks import MessageEvent
from commands.command_manager import CommandManager

@CommandManager.register_command(name="echo", description="メッセージをそのまま返します")
async def echo(event: MessageEvent, line_bot_api: AsyncMessagingApi, args: str):
    """Echoコマンドの処理"""
    message = args.strip()  # 引数をそのまま返す
    await line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage(text=message)]
        )
    )