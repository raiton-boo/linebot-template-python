import json
import logging
from urllib.parse import parse_qs

from linebot.v3.messaging import (
    AsyncMessagingApi,
    ReplyMessageRequest,
    TextMessage,
    FlexMessage,
    FlexBubble,
    FlexBox,
    FlexText,
    FlexSeparator,
)
from linebot.v3.webhooks import PostbackEvent

logger = logging.getLogger(__name__)


class PostbackEventHandler:
    """Postbackイベントを処理するハンドラー"""

    def __init__(self, api: AsyncMessagingApi):
        self.api = api

    async def handle(self, event: PostbackEvent) -> None:
        """Postbackイベントの処理"""
        try:
            postback_data = event.postback.data
            logger.info(f"Postback received: {postback_data}")

            # Postbackデータの種類を判別して処理を分岐
            if postback_data.startswith("{"):
                # JSONデータの場合
                await self._handle_json_postback(event, postback_data)
            else:
                # URLエンコード形式の場合
                await self._handle_query_postback(event, postback_data)

        except Exception as e:
            logger.error(f"PostbackEventHandler error: {e}")
            await self._reply_error_message(event)

    async def _handle_json_postback(self, event: PostbackEvent, json_data: str) -> None:
        """JSON形式のPostbackデータを処理"""
        try:
            data = json.loads(json_data)
            action = data.get("action", "unknown")

            if action == "json_test":
                # JSON形式のテストデータを処理
                test_data = data.get("data", {})
                user_id = test_data.get("id", "不明")
                user_name = test_data.get("name", "不明")
                timestamp = test_data.get("timestamp", "不明")

                response_text = (
                    f"JSON データテスト結果:\n"
                    f"ID: {user_id}\n"
                    f"名前: {user_name}\n"
                    f"タイムスタンプ: {timestamp}\n"
                    f"データ形式: JSON"
                )

                await self._reply_postback_result(event, response_text, "JSON")
            else:
                await self._reply_unknown_action(event, action)

        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}")
            await self._reply_error_message(event, "JSONデータの解析に失敗しました")

    async def _handle_query_postback(
        self, event: PostbackEvent, query_data: str
    ) -> None:
        """URLエンコード形式のPostbackデータを処理"""
        try:
            # クエリパラメータをパース
            params = parse_qs(query_data)
            # parse_qsは値をリストで返すので、最初の値を取得
            action = params.get("action", ["unknown"])[0]

            if action == "basic_test":
                # 基本テストの処理
                test_type = params.get("type", ["unknown"])[0]
                response_text = (
                    f"基本テスト実行完了\n"
                    f"テストタイプ: {test_type}\n"
                    f"データ形式: URL Query"
                )
                await self._reply_postback_result(event, response_text, "基本")

            elif action == "param_test":
                # パラメータテストの処理
                user = params.get("user", ["不明"])[0]
                value = params.get("value", ["不明"])[0]
                response_text = (
                    f"パラメータテスト結果:\n"
                    f"ユーザー: {user}\n"
                    f"値: {value}\n"
                    f"データ形式: URL Query"
                )
                await self._reply_postback_result(event, response_text, "パラメータ")

            elif action == "silent_test":
                # サイレントテスト（チャットに表示されない）
                notification = params.get("notification", ["true"])[0]
                response_text = (
                    f"サイレントテスト実行完了\n"
                    f"通知設定: {notification}\n"
                    f"※このボタンはサイレント送信のため、"
                    f"押した時にチャット欄に表示されません"
                )
                await self._reply_postback_result(event, response_text, "サイレント")

            else:
                await self._reply_unknown_action(event, action)

        except Exception as e:
            logger.error(f"Query parse error: {e}")
            await self._reply_error_message(event, "クエリデータの解析に失敗しました")

    async def _reply_postback_result(
        self, event: PostbackEvent, result_text: str, test_type: str
    ) -> None:
        """Postback処理結果をFlexメッセージで返信"""
        # テストタイプに応じた色テーマを設定
        color_themes = {
            "基本": "#28A745",  # 緑
            "パラメータ": "#6C757D",  # グレー
            "JSON": "#FFC107",  # 黄色
            "サイレント": "#6F42C1",  # 紫
        }

        color = color_themes.get(test_type, "#007BFF")

        # ヘッダー部分
        header_box = FlexBox(
            layout="vertical",
            contents=[
                FlexText(
                    text=f"✅ {test_type}テスト完了",
                    weight="bold",
                    size="lg",
                    color="#ffffff",
                ),
                FlexText(
                    text="Postbackイベント処理結果",
                    size="sm",
                    color="#ffffff",
                ),
            ],
            background_color=color,
            padding_all="16px",
            spacing="sm",
        )

        # 結果内容部分
        content_box = FlexBox(
            layout="vertical",
            contents=[
                FlexText(
                    text="処理結果:", weight="bold", size="md", color=color, margin="md"
                ),
                FlexSeparator(margin="sm"),
                FlexText(
                    text=result_text,
                    size="sm",
                    wrap=True,
                    margin="md",
                ),
            ],
            padding_all="20px",
        )

        # 追加情報部分
        info_box = FlexBox(
            layout="vertical",
            contents=[
                FlexText(
                    text="📝 補足情報",
                    weight="bold",
                    size="sm",
                    color=color,
                ),
                FlexText(
                    text="このメッセージはPostbackイベントの処理結果として生成されました。",
                    size="xs",
                    wrap=True,
                    color="#666666",
                    margin="sm",
                ),
            ],
            margin="xl",
            background_color="#F8F9FA",
            padding_all="12px",
            corner_radius="8px",
        )

        # バブルを組み立て
        bubble = FlexBubble(
            hero=header_box,
            body=FlexBox(
                layout="vertical",
                contents=[content_box, info_box],
                spacing="none",
            ),
        )

        flex_message = FlexMessage(
            alt_text=f"{test_type}テスト完了 - Postback処理結果", contents=bubble
        )

        await self.api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[flex_message],
            )
        )

    async def _reply_unknown_action(self, event: PostbackEvent, action: str) -> None:
        """未知のアクションに対する応答"""
        response_text = f"未知のアクション: {action}\nサポートされていない操作です。"

        await self.api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=response_text)],
            )
        )

    async def _reply_error_message(
        self, event: PostbackEvent, error_detail: str = None
    ) -> None:
        """エラーメッセージで返信"""
        base_message = "Postbackイベントの処理中にエラーが発生しました。"

        if error_detail:
            response_text = f"{base_message}\n詳細: {error_detail}"
        else:
            response_text = base_message

        await self.api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=response_text)],
            )
        )


def get_handlers(api: AsyncMessagingApi):
    """Postbackハンドラーを登録"""
    postback_handler = PostbackEventHandler(api)
    return {PostbackEvent: postback_handler.handle}
