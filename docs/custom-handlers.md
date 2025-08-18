# カスタムハンドラの作成

このドキュメントでは、新しいイベントハンドラの作成方法と既存ハンドラのカスタマイズ方法を説明します。

## 🏗 ハンドラアーキテクチャ

### ベースハンドラクラス

すべてのイベントハンドラは `BaseEventHandler` を継承します：

```python
# handlers/base_handler.py
from abc import ABC, abstractmethod
import logging
from linebot.v3.messaging import AsyncMessagingApi

class BaseEventHandler(ABC):
    def __init__(self, line_bot_api: AsyncMessagingApi):
        self.line_bot_api = line_bot_api
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    async def handle(self, event) -> None:
        """イベント処理の抽象メソッド"""
        pass
```

## 📝 新しいハンドラの作成

### 1. カスタムメッセージハンドラの例

```python
# handlers/custom_message_handler.py
from typing import Any
from linebot.v3.messaging import TextMessage, ReplyMessageRequest
from linebot.v3.webhooks import MessageEvent
from .base_handler import BaseEventHandler

class CustomMessageHandler(BaseEventHandler):
    """カスタムメッセージハンドラの例"""

    async def handle(self, event: MessageEvent) -> None:
        """メッセージイベントをカスタム処理"""
        try:
            if not hasattr(event.message, "text"):
                return

            message_text = event.message.text.strip().lower()

            # コマンドパターンで処理を分岐
            if message_text.startswith("/weather"):
                await self._handle_weather_command(event, message_text)
            elif message_text.startswith("/help"):
                await self._handle_help_command(event)
            elif message_text == "今何時？":
                await self._handle_time_command(event)
            else:
                await self._handle_default_message(event)

        except Exception as e:
            self.logger.error(f"カスタムメッセージ処理エラー: {e}")
            await self._send_error_message(event)

    async def _handle_weather_command(self, event: MessageEvent, message_text: str) -> None:
        """天気コマンド処理"""
        # 天気APIを呼び出す処理
        location = message_text.replace("/weather", "").strip()
        if not location:
            location = "東京"

        # 実際の天気API呼び出しはここに実装
        weather_info = f"{location}の天気は晴れです☀️"

        await self._send_reply(event.reply_token, weather_info)

    async def _handle_help_command(self, event: MessageEvent) -> None:
        """ヘルプコマンド処理"""
        help_text = """
🤖 利用可能なコマンド:

/weather [場所] - 指定場所の天気を表示
/help - このヘルプを表示
今何時？ - 現在時刻を表示
profile - プロフィール情報を表示

その他のメッセージは鸚鵡返しします。
        """
        await self._send_reply(event.reply_token, help_text.strip())

    async def _handle_time_command(self, event: MessageEvent) -> None:
        """時刻コマンド処理"""
        from datetime import datetime
        current_time = datetime.now().strftime("%Y年%m月%d日 %H時%M分")
        await self._send_reply(event.reply_token, f"現在時刻: {current_time}")

    async def _handle_default_message(self, event: MessageEvent) -> None:
        """デフォルトメッセージ処理（鸚鵡返し）"""
        reply_text = f"「{event.message.text}」と言いましたね！"
        await self._send_reply(event.reply_token, reply_text)

    async def _send_reply(self, reply_token: str, text: str) -> None:
        """返信送信のヘルパーメソッド"""
        messages = [TextMessage(text=text)]
        await self.line_bot_api.reply_message(
            ReplyMessageRequest(reply_token=reply_token, messages=messages)
        )

    async def _send_error_message(self, event: MessageEvent) -> None:
        """エラーメッセージ送信"""
        error_text = "申し訳ございませんが、処理中にエラーが発生しました。"
        await self._send_reply(event.reply_token, error_text)
```

### 2. カスタム Postback ハンドラの例

```python
# handlers/postback_handler.py
from linebot.v3.messaging import TextMessage, ReplyMessageRequest
from linebot.v3.webhooks import PostbackEvent
from .base_handler import BaseEventHandler

class PostbackEventHandler(BaseEventHandler):
    """ポストバックイベントハンドラ"""

    async def handle(self, event: PostbackEvent) -> None:
        """ポストバックイベント処理"""
        try:
            data = event.postback.data

            if data == "action=menu":
                await self._show_menu(event)
            elif data.startswith("action=select_"):
                await self._handle_selection(event, data)
            else:
                await self._handle_unknown_postback(event)

        except Exception as e:
            self.logger.error(f"ポストバック処理エラー: {e}")

    async def _show_menu(self, event: PostbackEvent) -> None:
        """メニュー表示"""
        menu_text = "メニューが表示されました！"
        await self._send_reply(event.reply_token, menu_text)

    async def _handle_selection(self, event: PostbackEvent, data: str) -> None:
        """選択項目処理"""
        selection = data.replace("action=select_", "")
        response_text = f"「{selection}」を選択しました！"
        await self._send_reply(event.reply_token, response_text)

    async def _handle_unknown_postback(self, event: PostbackEvent) -> None:
        """不明なポストバック処理"""
        self.logger.warning(f"不明なポストバック: {event.postback.data}")

    async def _send_reply(self, reply_token: str, text: str) -> None:
        """返信送信"""
        messages = [TextMessage(text=text)]
        await self.line_bot_api.reply_message(
            ReplyMessageRequest(reply_token=reply_token, messages=messages)
        )
```

## 🔌 ハンドラの登録

### 1. ハンドラマッピングの追加

```python
# app.py でハンドラを登録
from handlers import (
    MessageEventHandler,
    FollowEventHandler,
    CustomMessageHandler,  # 新しいハンドラ
    PostbackEventHandler   # 新しいハンドラ
)

# ハンドラマッピング
EVENT_HANDLERS: Dict[Type[Any], Type[BaseEventHandler]] = {
    MessageEvent: CustomMessageHandler,  # デフォルトの代わりにカスタムハンドラを使用
    FollowEvent: FollowEventHandler,
    UnfollowEvent: UnfollowEventHandler,
    PostbackEvent: PostbackEventHandler,  # ポストバックイベント追加
    # 他のイベント...
}
```

### 2. 新しいイベントタイプの追加

```python
# 新しいイベントタイプをインポート
from linebot.v3.webhooks import PostbackEvent, QuickReplyEvent

# イベントハンドラマッピングに追加
EVENT_HANDLERS: Dict[Type[Any], Type[BaseEventHandler]] = {
    # 既存のハンドラ...
    PostbackEvent: PostbackEventHandler,
    # QuickReplyEvent: QuickReplyEventHandler,  # 必要に応じて
}
```

## 🛠 高度なカスタマイズ

### 1. データベース連携ハンドラ

```python
# handlers/database_handler.py
import asyncpg
from .base_handler import BaseEventHandler

class DatabaseMessageHandler(BaseEventHandler):
    """データベース連携メッセージハンドラ"""

    def __init__(self, line_bot_api, db_pool):
        super().__init__(line_bot_api)
        self.db_pool = db_pool

    async def handle(self, event: MessageEvent) -> None:
        """メッセージをデータベースに記録して処理"""
        try:
            # メッセージをデータベースに保存
            await self._save_message_to_db(event)

            # 通常のメッセージ処理
            await self._process_message(event)

        except Exception as e:
            self.logger.error(f"データベース処理エラー: {e}")

    async def _save_message_to_db(self, event: MessageEvent) -> None:
        """メッセージをデータベースに保存"""
        async with self.db_pool.acquire() as connection:
            await connection.execute(
                "INSERT INTO messages (user_id, text, timestamp) VALUES ($1, $2, $3)",
                event.source.user_id,
                event.message.text,
                event.timestamp
            )

    async def _process_message(self, event: MessageEvent) -> None:
        """メッセージ処理ロジック"""
        # カスタム処理を実装
        pass
```

### 2. 外部 API 連携ハンドラ

```python
# handlers/api_handler.py
import aiohttp
from .base_handler import BaseEventHandler

class APIMessageHandler(BaseEventHandler):
    """外部API連携ハンドラ"""

    async def handle(self, event: MessageEvent) -> None:
        """外部APIを呼び出してレスポンス"""
        try:
            if event.message.text.startswith("/translate"):
                await self._handle_translate(event)
            # 他のAPI処理...

        except Exception as e:
            self.logger.error(f"API処理エラー: {e}")

    async def _handle_translate(self, event: MessageEvent) -> None:
        """翻訳API呼び出し"""
        text = event.message.text.replace("/translate", "").strip()

        async with aiohttp.ClientSession() as session:
            # 翻訳APIを呼び出し（例：Google Translate API）
            translated_text = await self._call_translate_api(session, text)
            await self._send_reply(event.reply_token, translated_text)

    async def _call_translate_api(self, session: aiohttp.ClientSession, text: str) -> str:
        """実際の翻訳API呼び出し"""
        # API実装の詳細
        return f"翻訳結果: {text}"  # プレースホルダー
```

## 📋 ベストプラクティス

### 1. エラーハンドリング

- すべてのハンドラでトップレベルの try-catch を実装
- 詳細なログ出力（デバッグ時）
- ユーザーフレンドリーなエラーメッセージ

### 2. パフォーマンス

- 長時間の処理は非同期で実行
- データベースコネクションプールを使用
- 必要に応じてキャッシュを実装

### 3. テスト可能性

- ハンドラロジックをテストしやすく設計
- 外部依存関係をモック可能にする
- 単体テストを作成

### 4. 設定管理

```python
# config.py
class Config:
    WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
    DATABASE_URL = os.getenv("DATABASE_URL")
    TRANSLATE_API_KEY = os.getenv("TRANSLATE_API_KEY")

# ハンドラで使用
from config import Config

class WeatherHandler(BaseEventHandler):
    def __init__(self, line_bot_api):
        super().__init__(line_bot_api)
        self.api_key = Config.WEATHER_API_KEY
```

## 🧪 テスト例

```python
# tests/test_custom_handler.py
import pytest
from unittest.mock import AsyncMock, Mock
from handlers.custom_message_handler import CustomMessageHandler

@pytest.mark.asyncio
async def test_weather_command():
    """天気コマンドのテスト"""
    # モック作成
    mock_api = AsyncMock()
    handler = CustomMessageHandler(mock_api)

    # テストイベント作成
    event = Mock()
    event.message.text = "/weather 東京"
    event.reply_token = "test_token"

    # ハンドラ実行
    await handler.handle(event)

    # アサーション
    mock_api.reply_message.assert_called_once()
```

このようにハンドラを作成・カスタマイズすることで、LINE Bot の機能を柔軟に拡張できます。
