import logging
from typing import Dict, Any
from linebot.v3.messaging import (
    AsyncMessagingApi,
    ReplyMessageRequest,
    FlexMessage,
    FlexBubble,
    FlexBox,
    FlexText,
    FlexSeparator,
)
from linebot.v3.webhooks import MessageEvent

logger = logging.getLogger(__name__)


class FileHandler:
    """ファイルメッセージを処理するハンドラー"""

    def __init__(self, api: AsyncMessagingApi):
        self.api = api

    async def handle(self, event: MessageEvent) -> None:
        """ファイルメッセージの処理"""
        try:
            user_id = event.source.user_id
            logger.info(f"Received file from user: {user_id}")

            # ファイル情報を取得・分析
            file_info = self._get_file_info(event)
            analysis = self._analyze_file(file_info)

            # Flexメッセージで応答
            flex_message = self._create_file_flex_message(file_info, analysis)

            await self.api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[flex_message],
                )
            )

        except Exception as e:
            logger.error(f"FileHandler error: {e}")

    def _create_file_flex_message(
        self, file_info: Dict[str, Any], analysis: Dict[str, Any]
    ) -> FlexMessage:
        """ファイル受信用のFlexメッセージを作成"""
        file_name = file_info.get("file_name", "不明なファイル")
        file_type = analysis.get("type", "不明")
        formatted_size = analysis.get("formatted_size", "不明")
        size_category = analysis.get("size_category", "不明")
        extension = analysis.get("extension", "")
        security_level = analysis.get("security_level", "不明")
        is_executable = analysis.get("is_executable", False)

        # セキュリティレベルに応じた色テーマを選択
        color_theme = self._get_security_color_theme(security_level)

        # ヘッダー部分
        header_box = FlexBox(
            layout="vertical",
            contents=[
                FlexText(
                    text="ファイル受信",
                    weight="bold",
                    size="xl",
                    color="#ffffff"
                ),
                FlexText(
                    text=file_name,
                    size="md",
                    color="#ffffff",
                    wrap=True,
                    max_lines=2
                ),
            ],
            background_color=color_theme["primary"],
            padding_all="20px",
            spacing="md"
        )

        # ファイル基本情報
        file_info_contents = [
            FlexText(
                text="ファイル情報",
                weight="bold",
                size="md",
                color=color_theme["primary"]
            ),
            FlexSeparator(margin="sm"),
            self._create_file_info_row("タイプ", file_type),
            self._create_file_info_row("サイズ", f"{formatted_size} ({size_category}サイズ)"),
        ]

        if extension:
            file_info_contents.append(self._create_file_info_row("拡張子", f".{extension}"))

        file_info_box = FlexBox(
            layout="vertical",
            contents=file_info_contents,
            margin="lg"
        )

        # セキュリティ情報
        security_info_contents = [
            FlexText(
                text="セキュリティ情報",
                weight="bold",
                size="md",
                color=color_theme["primary"]
            ),
            FlexSeparator(margin="sm"),
            self._create_security_info_row(security_level, is_executable),
        ]

        security_info_box = FlexBox(
            layout="vertical",
            contents=security_info_contents,
            margin="xl"
        )

        # ファイル説明セクション
        description_box = self._create_file_description_box(file_type)

        # メインボディの構成
        body_contents = [file_info_box, security_info_box]
        if description_box:
            body_contents.append(description_box)

        body_box = FlexBox(
            layout="vertical",
            contents=body_contents,
            spacing="sm",
            padding_all="20px"
        )

        # セキュリティ警告フッター
        footer_box = None
        if security_level in ["危険", "注意"]:
            footer_box = self._create_security_warning_footer(security_level)

        bubble = FlexBubble(
            hero=header_box,
            body=body_box,
            footer=footer_box
        )

        return FlexMessage(
            alt_text=f"ファイル受信: {file_name}",
            contents=bubble
        )

    def _create_file_info_row(self, label: str, value: str) -> FlexBox:
        """ファイル情報の行を作成"""
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

    def _create_security_info_row(self, security_level: str, is_executable: bool) -> FlexBox:
        """セキュリティ情報の行を作成"""
        security_colors = {
            "安全": "#00B894",
            "不明": "#74B9FF",
            "注意": "#FDCB6E",
            "危険": "#E84393"
        }

        color = security_colors.get(security_level, "#74B9FF")
        executable_text = " (実行可能)" if is_executable else ""

        return FlexBox(
            layout="baseline",
            contents=[
                FlexText(
                    text="レベル",
                    size="sm",
                    color="#666666",
                    flex=2
                ),
                FlexText(
                    text=f"{security_level}{executable_text}",
                    size="sm",
                    color=color,
                    weight="bold",
                    flex=3
                ),
            ],
            margin="md"
        )

    def _create_file_description_box(self, file_type: str) -> FlexBox:
        """ファイルタイプの説明ボックスを作成"""
        descriptions = {
            "画像": "写真や図表などの画像データです。",
            "PDF文書": "テキストや表計算などのオフィス文書です。",
            "Word文書": "テキストや表計算などのオフィス文書です。",
            "Excel文書": "テキストや表計算などのオフィス文書です。",
            "音声": "音楽や録音データなどの音声ファイルです。",
            "動画": "映像と音声を含む動画ファイルです。",
            "圧縮ファイル": "複数のファイルをまとめた圧縮ファイルです。",
            "Pythonコード": "ソースコードやスクリプトファイルです。"
        }

        description = descriptions.get(file_type, "")
        if not description:
            return None

        return FlexBox(
            layout="vertical",
            contents=[
                FlexText(
                    text="ファイルについて",
                    weight="bold",
                    size="md",
                    color="#6C5CE7"
                ),
                FlexText(
                    text=description,
                    size="sm",
                    wrap=True,
                    color="#666666",
                    margin="sm"
                )
            ],
            margin="xl",
            background_color="#F8F9FA",
            padding_all="12px",
            corner_radius="8px"
        )

    def _create_security_warning_footer(self, security_level: str) -> FlexBox:
        """セキュリティ警告フッターを作成"""
        if security_level == "危険":
            warning_text = "実行可能ファイルです。開く際は十分注意してください。"
            color = "#E84393"
        else:  # 注意
            warning_text = "圧縮ファイルです。中身を確認してから展開してください。"
            color = "#FDCB6E"

        return FlexBox(
            layout="vertical",
            contents=[
                FlexText(
                    text=warning_text,
                    size="sm",
                    color="#ffffff",
                    wrap=True,
                    weight="bold"
                )
            ],
            background_color=color,
            padding_all="16px"
        )

    def _get_security_color_theme(self, security_level: str) -> Dict[str, str]:
        """セキュリティレベル別の色テーマを取得"""
        themes = {
            "安全": {"primary": "#00B894", "secondary": "#D1F2EB"},
            "不明": {"primary": "#74B9FF", "secondary": "#EBF4FF"},
            "注意": {"primary": "#FDCB6E", "secondary": "#FFF9E6"},
            "危険": {"primary": "#E84393", "secondary": "#FDE8F4"}
        }
        return themes.get(security_level, themes["不明"])

    def _get_file_info(self, event: MessageEvent) -> Dict[str, Any]:
        """メッセージからファイル情報を抽出"""
        message = event.message

        file_info = {
            "message_id": getattr(message, "id", "unknown"),
            "file_name": getattr(message, "file_name", "unknown"),
            "file_size": getattr(message, "file_size", 0),
        }

        logger.info(
            f"File info: {file_info['file_name']} ({file_info['file_size']} bytes)"
        )

        return file_info

    def _analyze_file(self, file_info: Dict[str, Any]) -> Dict[str, Any]:
        """ファイル情報を分析"""
        file_name = file_info.get("file_name", "")
        file_size = file_info.get("file_size", 0)

        # 拡張子を取得
        file_extension = ""
        if "." in file_name:
            file_extension = file_name.split(".")[-1].lower()

        return {
            "extension": file_extension,
            "type": self._determine_file_type(file_extension),
            "size_category": self._determine_size_category(file_size),
            "formatted_size": self._format_file_size(file_size),
            "security_level": self._determine_security_level(file_extension),
            "is_executable": self._is_executable_file(file_extension),
        }

    def _determine_file_type(self, extension: str) -> str:
        """拡張子からファイルタイプを判定"""
        file_type_map = {
            # 画像ファイル
            "jpg": "画像", "jpeg": "画像", "png": "画像", "gif": "画像", 
            "bmp": "画像", "webp": "画像", "svg": "画像", "tiff": "画像",
            # 文書ファイル
            "pdf": "PDF文書", "doc": "Word文書", "docx": "Word文書",
            "xls": "Excel文書", "xlsx": "Excel文書", "ppt": "PowerPoint", "pptx": "PowerPoint",
            "txt": "テキスト", "rtf": "リッチテキスト",
            # 音声ファイル
            "mp3": "音声", "wav": "音声", "m4a": "音声", "aac": "音声", 
            "flac": "音声", "ogg": "音声", "wma": "音声",
            # 動画ファイル
            "mp4": "動画", "avi": "動画", "mov": "動画", "wmv": "動画", 
            "flv": "動画", "mkv": "動画", "webm": "動画",
            # 圧縮ファイル
            "zip": "圧縮ファイル", "rar": "圧縮ファイル", "7z": "圧縮ファイル",
            "tar": "圧縮ファイル", "gz": "圧縮ファイル", "bz2": "圧縮ファイル",
            # プログラムファイル
            "py": "Pythonコード", "js": "JavaScriptコード", "html": "HTMLファイル",
            "css": "CSSファイル", "json": "JSONファイル", "xml": "XMLファイル",
            "php": "PHPコード", "java": "Javaコード", "cpp": "C++コード",
            # その他
            "csv": "CSVデータ", "sql": "SQLファイル", "log": "ログファイル",
            "ini": "設定ファイル", "cfg": "設定ファイル", "conf": "設定ファイル",
        }
        return file_type_map.get(extension, "不明なファイル")

    def _determine_size_category(self, file_size: int) -> str:
        """ファイルサイズのカテゴリを判定"""
        if file_size < 1024:
            return "極小"
        elif file_size < 1024 * 1024:
            return "小"
        elif file_size < 10 * 1024 * 1024:
            return "中"
        elif file_size < 100 * 1024 * 1024:
            return "大"
        else:
            return "特大"

    def _determine_security_level(self, extension: str) -> str:
        """拡張子からセキュリティレベルを判定"""
        dangerous_extensions = {"exe", "bat", "cmd", "com", "scr", "pif", "vbs", "js", "jar"}
        suspicious_extensions = {"zip", "rar", "7z", "tar", "gz"}
        safe_extensions = {"txt", "pdf", "jpg", "jpeg", "png", "gif", "mp3", "mp4", "doc", "docx"}

        if extension in dangerous_extensions:
            return "危険"
        elif extension in suspicious_extensions:
            return "注意"
        elif extension in safe_extensions:
            return "安全"
        else:
            return "不明"

    def _is_executable_file(self, extension: str) -> bool:
        """実行可能ファイルかどうかを判定"""
        executable_extensions = {"exe", "bat", "cmd", "com", "scr", "pif", "app", "deb", "rpm"}
        return extension in executable_extensions

    def _format_file_size(self, file_size: int) -> str:
        """ファイルサイズを読みやすい形式にフォーマット"""
        if file_size >= 1024 * 1024 * 1024:
            return f"{file_size / (1024 * 1024 * 1024):.1f} GB"
        elif file_size >= 1024 * 1024:
            return f"{file_size / (1024 * 1024):.1f} MB"
        elif file_size >= 1024:
            return f"{file_size / 1024:.1f} KB"
        else:
            return f"{file_size} bytes"