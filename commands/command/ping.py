import time
from linebot.v3.messaging import AsyncMessagingApi, ReplyMessageRequest, TextMessage
from linebot.v3.webhooks import MessageEvent
from commands.command_manager import CommandManager

@CommandManager.register_command(name="ping", aliases=["pong", "ぴんぐ"], description="Pingコマンド")
async def ping(event: MessageEvent, line_bot_api: AsyncMessagingApi):
    """Pingコマンドの処理"""
    start_time = time.time()  # 実行開始時間を記録

    # 実行時間を計測するための処理
    end_time = time.time()
    execution_time = end_time - start_time

    # メッセージをまとめて返信
    await line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[
                TextMessage(text="Pong!"),
                TextMessage(text=f"実行時間: {execution_time:.3f}秒") # 本当はPushmessage使いたいけど、使いすぎると制限に引っかかるので、ここはReplymessageで我慢
            ]
        )
    )