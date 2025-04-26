from linebot.v3.messaging import AsyncMessagingApi, ReplyMessageRequest, TextMessage
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from commands.command_manager import CommandManager

from commands.command import (
    ping,
    echo
)

async def handle_message_event(event: MessageEvent, line_bot_api: AsyncMessagingApi):
    """メッセージイベントを処理"""
    if isinstance(event.message, TextMessageContent):
        text = event.message.text.strip()

        # コマンド名と引数の初期化
        command_name = None
        args = ""

        # 英数字のコマンドは / または ! で始まる場合のみ反応
        if text.startswith(("/", "!")):
            # プレフィックスのみの場合は無視
            if len(text) == 1:
                return
            # プレフィックスを除去し、コマンド名と引数を分離
            parts = text[1:].split(" ", 1)
            command_name = parts[0]
            args = parts[1] if len(parts) > 1 else ""
        else:
            # 日本語の場合はそのままコマンド名として扱う
            command_name = text

        # コマンドの存在チェックと実行
        if command_name in CommandManager._commands:
            command = CommandManager._commands[command_name]
            if "args" in command["func"].__code__.co_varnames:  # 引数を取るか確認
                await CommandManager.execute_command(command_name, event, line_bot_api, args)
            else:
                await CommandManager.execute_command(command_name, event, line_bot_api)
        elif text.startswith(("/", "!")):
            # 英数字コマンドで存在しない場合のみエラーメッセージを送信
            await line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text="そのコマンドはありません")]
                )
            )