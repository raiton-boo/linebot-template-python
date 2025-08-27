from typing import Any, Dict, Optional

from linebot.v3.webhooks import MessageEvent
from linebot.v3.messaging import AsyncMessagingApi, TextMessage, ReplyMessageRequest

from .base_handler import BaseEventHandler

# プロフィール取得機能をインポート
from commands import GetProfileCommand


class MessageEventHandler(BaseEventHandler):
    """
    MessageEvent handler

    ユーザーからテキスト、画像、音声などのメッセージを受信した際に発生するイベントを処理します。
    """

    def __init__(self, line_bot_api: AsyncMessagingApi):
        """
        Initialize handler with profile command

        Args:
            line_bot_api (AsyncMessagingApi): LINE Bot API client
        """
        super().__init__(line_bot_api)
        # プロフィール取得コマンドを初期化
        self.profile_command = GetProfileCommand(line_bot_api, self.logger)

    async def handle(self, event: MessageEvent) -> None:
        """
        Process message event

        Args:
            event (MessageEvent): Message event

        Raises:
            Exception: Error occurred during event processing
        """
        try:
            # メッセージタイプを取得
            message = event.message
            message_type = message.type if hasattr(message, "type") else "unknown"
            user_id = (
                event.source.user_id if hasattr(event.source, "user_id") else "unknown"
            )

            self.logger.info(f"Message received: {message_type} from {user_id}")

            # メッセージタイプに応じた処理
            response_message = await self._process_message(message, event)

            if response_message:
                messages = [TextMessage(text=response_message)]
                reply_request = ReplyMessageRequest(
                    reply_token=event.reply_token, messages=messages
                )
                await self.line_bot_api.reply_message(reply_request)

        except Exception as error:
            await self._safe_error_handle(error, event)
            raise

    async def _process_message(
        self, message: Any, event: MessageEvent
    ) -> Optional[str]:
        """
        メッセージタイプに応じた処理を実行

        Args:
            message (Any): メッセージオブジェクト
            event (MessageEvent): メッセージイベント

        Returns:
            Optional[str]: 返信メッセージ（Noneの場合は返信なし）
        """
        message_type = getattr(message, "type", "unknown")

        # テキストメッセージの場合（eventも渡す）
        if message_type == "text":
            return await self._handle_text_message(message, event)  # eventを追加

        # 画像メッセージの場合
        elif message_type == "image":
            return "画像を受信しました！素敵な写真ですね。"

        # 音声メッセージの場合
        elif message_type == "audio":
            return "音声メッセージを受信しました！"

        # 動画メッセージの場合
        elif message_type == "video":
            return "動画を受信しました！"

        # ファイルメッセージの場合
        elif message_type == "file":
            file_name = getattr(message, "fileName", "ファイル")
            return f"ファイル「{file_name}」を受信しました！"

        # スタンプメッセージの場合
        elif message_type == "sticker":
            return "可愛いスタンプですね！😊"

        # 位置情報メッセージの場合
        elif message_type == "location":
            title = getattr(message, "title", "場所")
            address = getattr(message, "address", "不明")
            return f"位置情報を受信しました！\n場所: {title}\n住所: {address}"

        # その他(未対応)のメッセージタイプ
        else:
            return f"{message_type}メッセージを受信しました！"

    async def _handle_text_message(
        self, message: Any, event: MessageEvent
    ) -> Optional[str]:
        """
        テキストメッセージの処理

        Args:
            message (Any): テキストメッセージオブジェクト
            event (MessageEvent): メッセージイベント

        Returns:
            Optional[str]: 返信メッセージ（Noneの場合はコマンドが処理済み）
        """
        text = getattr(message, "text", "").lower().strip()

        # 簡単なパターンマッチング
        if not text:
            return "メッセージが受信できませんでした。"

        # プロフィール取得コマンド
        if any(
            profile_cmd in text
            for profile_cmd in ["profile", "プロフィール", "ぷろふぃーる"]
        ):
            # プロフィール取得コマンドを実行（返信はコマンド内で処理）
            await self.profile_command.execute(event)
            return None  # コマンドが返信処理済みのため、Noneを返す

        # 挨拶パターン
        elif any(
            greeting in text
            for greeting in ["こんにちは", "おはよう", "こんばんは", "hello", "hi"]
        ):
            return "こんにちは！お元気ですか？"

        # 感謝パターン
        elif any(
            thanks in text
            for thanks in ["ありがとう", "サンキュー", "thanks", "thank you"]
        ):
            return (
                "どういたしまして！何か他にお手伝いできることがあれば教えてくださいね。"
            )

        # ヘルプパターン
        elif any(
            help_word in text for help_word in ["ヘルプ", "help", "使い方", "機能"]
        ):
            return (
                "【Bot機能一覧】\n"
                "• テキスト、画像、音声などのメッセージに対応\n"
                "• スタンプや位置情報も受信可能\n"
                "• 簡単な会話機能\n"
                "• プロフィール情報の取得（「プロフィール」と送信）\n"
                "何かメッセージを送ってみてください！"
            )

        # 質問パターン
        elif "?" in text or "？" in text:
            return "質問ですね！申し訳ありませんが、まだ詳しい質問にはお答えできません。今後改良していきます！"

        # それ以外のメッセージ
        else:
            return None

    async def _error_handle(
        self,
        error: Exception,
        event: MessageEvent,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Handle error

        Args:
            error (Exception): Occurred error
            event (MessageEvent): Event where error occurred
            context (Optional[Dict[str, Any]]): Context information when error occurred
        """
        try:
            message_type = (
                getattr(event.message, "type", "unknown")
                if hasattr(event, "message")
                else "unknown"
            )
            self.logger.error(
                f"Message handler error ({message_type}): {type(error).__name__} - {str(error)}",
                exc_info=True,
            )
        except Exception:
            # 絶対に例外を投げてはいけません
            pass
