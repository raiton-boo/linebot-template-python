import logging
from typing import Dict, Any
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
from linebot.v3.webhooks import MessageEvent

logger = logging.getLogger(__name__)


class StickerHandler:

    def __init__(self, api: AsyncMessagingApi):
        self.api = api

    async def handle(self, event: MessageEvent) -> None:
        try:
            user_id = event.source.user_id
            logger.info(f"Received sticker from user: {user_id}")

            # ステッカー情報を取得
            sticker_info = self._get_sticker_info(event)

            if not sticker_info:
                # 基本応答（Flexではない）
                response_text = "スタンプを受信しましたが、情報が取得できませんでした。"
                await self.api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text=response_text)],
                    )
                )
                return

            # Flexメッセージで応答
            flex_message = self._create_sticker_flex_message(sticker_info)

            await self.api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[flex_message],
                )
            )

        except Exception as e:
            logger.error(f"StickerHandler error: {e}")

    def _create_sticker_flex_message(self, sticker_info: Dict[str, Any]) -> FlexMessage:

        package_id = sticker_info.get("package_id", "不明")
        sticker_id = sticker_info.get("sticker_id", "不明")
        resource_type = sticker_info.get("sticker_resource_type", "static")
        keywords = sticker_info.get("keywords", [])
        text = sticker_info.get("text")

        # リソースタイプに応じた色テーマ
        theme = self._get_sticker_theme(resource_type)

        # ヘッダーボックス
        header_box = FlexBox(
            layout="vertical",
            contents=[
                FlexText(
                    text="ステッカー受信",
                    weight="bold",
                    size="xl",
                    color="#ffffff"
                ),
                FlexText(
                    text=f"{resource_type.upper()} ステッカー",
                    size="md",
                    color="#ffffff",
                    wrap=True
                ),
            ],
            background_color=theme["primary"],
            padding_all="20px",
            spacing="md"
        )

        # 基本情報セクション
        basic_info_contents = [
            FlexText(
                text="ステッカー情報",
                weight="bold",
                size="md",
                color=theme["primary"]
            ),
            FlexSeparator(margin="sm"),
            self._create_sticker_info_row("パッケージID", package_id),
            self._create_sticker_info_row("ステッカーID", sticker_id),
            self._create_sticker_info_row("タイプ", resource_type.upper()),
        ]

        basic_info_box = FlexBox(
            layout="vertical",
            contents=basic_info_contents,
            margin="lg"
        )

        # メインボディ
        body_contents = [basic_info_box]

        # テキスト情報がある場合
        if text:
            text_info_box = FlexBox(
                layout="vertical",
                contents=[
                    FlexText(
                        text="テキスト情報",
                        weight="bold",
                        size="md",
                        color=theme["primary"]
                    ),
                    FlexSeparator(margin="sm"),
                    FlexText(
                        text=text,
                        size="sm",
                        wrap=True,
                        margin="md",
                        background_color=theme["secondary"],
                        padding_all="12px",
                        corner_radius="8px"
                    )
                ],
                margin="xl"
            )
            body_contents.append(text_info_box)

        # キーワード情報がある場合
        if keywords:
            keyword_text = ", ".join(keywords[:5])  # 最大5個まで
            if len(keywords) > 5:
                keyword_text += f" (他{len(keywords)-5}個)"

            keyword_info_box = FlexBox(
                layout="vertical",
                contents=[
                    FlexText(
                        text="キーワード",
                        weight="bold",
                        size="md",
                        color=theme["primary"]
                    ),
                    FlexSeparator(margin="sm"),
                    FlexText(
                        text=keyword_text,
                        size="sm",
                        wrap=True,
                        margin="md",
                        background_color="#F8F9FA",
                        padding_all="12px",
                        corner_radius="8px"
                    )
                ],
                margin="xl"
            )
            body_contents.append(keyword_info_box)

        # 動的ステッカーの場合は特別表示
        if resource_type in ["ANIMATION", "SOUND", "ANIMATION_SOUND", "POPUP", "POPUP_SOUND"]:
            special_feature_box = FlexBox(
                layout="vertical",
                contents=[
                    FlexText(
                        text="特別機能",
                        weight="bold",
                        size="md",
                        color=theme["primary"]
                    ),
                    FlexText(
                        text=self._get_special_feature_description(resource_type),
                        size="sm",
                        wrap=True,
                        color="#666666",
                        margin="sm"
                    )
                ],
                margin="xl",
                background_color=theme["accent"],
                padding_all="12px",
                corner_radius="8px"
            )
            body_contents.append(special_feature_box)

        body_box = FlexBox(
            layout="vertical",
            contents=body_contents,
            spacing="sm",
            padding_all="20px"
        )

        # フッターボックス
        footer_box = FlexBox(
            layout="vertical",
            contents=[
                FlexText(
                    text="素敵なステッカーをありがとうございます",
                    size="sm",
                    color=theme["primary"],
                    align="center",
                    weight="bold",
                    wrap=True
                )
            ],
            padding_all="16px"
        )

        # バブル作成
        bubble = FlexBubble(
            hero=header_box,
            body=body_box,
            footer=footer_box
        )

        return FlexMessage(
            alt_text=f"ステッカー受信: {resource_type}",
            contents=bubble
        )

    def _create_sticker_info_row(self, label: str, value: str) -> FlexBox:
        return FlexBox(
            layout="baseline",
            contents=[
                FlexText(
                    text=label,
                    size="sm",
                    color="#666666",
                    flex=2
                ),
                FlexText(
                    text=value,
                    size="sm",
                    wrap=True,
                    flex=3,
                    max_lines=2
                ),
            ],
            margin="md"
        )

    def _get_sticker_theme(self, resource_type: str) -> Dict[str, str]:

        themes = {
            "static": {
                "primary": "#74B9FF",
                "secondary": "#EBF4FF",
                "accent": "#DDD6FE"
            },
            "ANIMATION": {
                "primary": "#E74C3C",
                "secondary": "#FADBD8",
                "accent": "#F8D7DA"
            },
            "SOUND": {
                "primary": "#27AE60",
                "secondary": "#D5F4E6",
                "accent": "#D4EDDA"
            },
            "ANIMATION_SOUND": {
                "primary": "#8E44AD",
                "secondary": "#EBD8F2",
                "accent": "#E2D3F4"
            },
            "POPUP": {
                "primary": "#F39C12",
                "secondary": "#FEF9E7",
                "accent": "#FFF3CD"
            },
            "POPUP_SOUND": {
                "primary": "#E91E63",
                "secondary": "#FCE4EC",
                "accent": "#F8D7DA"
            }
        }

        return themes.get(resource_type, themes["static"])

    def _get_special_feature_description(self, resource_type: str) -> str:

        descriptions = {
            "ANIMATION": "アニメーション効果付きの動的ステッカーです",
            "SOUND": "音声効果付きのステッカーです",
            "ANIMATION_SOUND": "アニメーションと音声の両方が楽しめる特別なステッカーです",
            "POPUP": "ポップアップ効果付きのステッカーです",
            "POPUP_SOUND": "ポップアップ効果と音声が付いた豪華なステッカーです"
        }

        return descriptions.get(resource_type, "特別な機能付きステッカーです")

    def _get_sticker_info(self, event: MessageEvent) -> Dict[str, Any]:
        message = event.message

        sticker_info = {
            "package_id": getattr(message, "package_id", "unknown"),
            "sticker_id": getattr(message, "sticker_id", "unknown"),
            "sticker_resource_type": getattr(message, "sticker_resource_type", "static"),
            "keywords": getattr(message, "keywords", []),
            "text": getattr(message, "text", None),
        }

        logger.info(f"Sticker info: {sticker_info['package_id']}/{sticker_info['sticker_id']} ({sticker_info['sticker_resource_type']})")

        return sticker_info

    def _get_sticker_info(self, event: MessageEvent) -> Dict[str, Any]:
        message = event.message

        # 基本情報は必須
        if not hasattr(message, "package_id") or not hasattr(message, "sticker_id"):
            logger.warning("Sticker message missing basic info")
            return {}

        sticker_info = {
            "package_id": getattr(message, "package_id", "unknown"),
            "sticker_id": getattr(message, "sticker_id", "unknown"),
            "sticker_resource_type": getattr(
                message, "sticker_resource_type", "static"
            ),
            "keywords": getattr(message, "keywords", []),
            "text": getattr(message, "text", None),
        }

        logger.info(
            f"Sticker info: {sticker_info['package_id']}/{sticker_info['sticker_id']} ({sticker_info['sticker_resource_type']})"
        )

        return sticker_info

    def _format_sticker_info(self, sticker_info: Dict[str, Any]) -> str:
        if not sticker_info:
            return "ステッカー情報を取得できませんでした。"

        package_id = sticker_info.get("package_id", "不明")
        sticker_id = sticker_info.get("sticker_id", "不明")
        resource_type = sticker_info.get("sticker_resource_type", "static")
        keywords = sticker_info.get("keywords", [])
        text = sticker_info.get("text")

        # 絵文字でわかりやすく表示
        response_parts = [
            "ステッカー情報:",
            f"パッケージID: {package_id}",
            f"ステッカーID: {sticker_id}",
            f"タイプ: {resource_type}",
        ]

        # キーワードがある場合
        if keywords:
            keyword_text = ", ".join(keywords[:5])  # 最大5個まで表示
            if len(keywords) > 5:
                keyword_text += f" (他{len(keywords)-5}個)"
            response_parts.append(f"キーワード: {keyword_text}")

        # テキスト情報がある場合
        if text:
            response_parts.append(f"テキスト: {text}")

        # 動的ステッカーの場合は特別表示
        if resource_type in [
            "ANIMATION",
            "SOUND",
            "ANIMATION_SOUND",
            "POPUP",
            "POPUP_SOUND",
        ]:
            response_parts.append("動的ステッカーです！")

        return "\n".join(response_parts)
