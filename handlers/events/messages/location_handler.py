import logging
import math
from typing import Dict, Any, List
from linebot.v3.messaging import (
    AsyncMessagingApi,
    ReplyMessageRequest,
    TextMessage,
    FlexMessage,
    FlexBubble,
    FlexBox,
    FlexText,
    FlexSeparator,
    FlexButton,
    URIAction,
)
from linebot.v3.webhooks import MessageEvent

logger = logging.getLogger(__name__)


class LocationHandler:

    def __init__(self, api: AsyncMessagingApi):
        self.api = api

    async def handle(self, event: MessageEvent) -> None:
        try:
            user_id = event.source.user_id
            logger.info(f"Received location from user: {user_id}")

            # 位置情報を取得
            location_info = self._get_location_info(event)

            if not location_info:
                response_text = "位置情報を受信しましたが、詳細を取得できませんでした。"
                await self.api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text=response_text)],
                    )
                )
                return

            # 位置情報の分析
            analysis = self._analyze_location(location_info)

            # Flexメッセージで応答
            flex_message = self._create_location_flex_message(location_info, analysis)

            await self.api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[flex_message],
                )
            )

        except Exception as e:
            logger.error(f"LocationHandler error: {e}")

    def _create_location_flex_message(
        self, location_info: Dict[str, Any], analysis: Dict[str, Any]
    ) -> FlexMessage:

        title = location_info.get("title", "位置情報")
        address = location_info.get("address", "住所不明")
        lat = location_info.get("latitude", "不明")
        lng = location_info.get("longitude", "不明")

        region = analysis.get("region", "不明")
        area = analysis.get("area", "")
        precision = analysis.get("coordinate_precision", "不明")
        location_type = analysis.get("location_type", "一般位置")
        nearest_city = analysis.get("nearest_city")
        nearest_distance = analysis.get("nearest_distance")

        # 地域に応じた色テーマ
        color_theme = self._get_location_color_theme(region, location_type)

        # ヘッダーボックス
        header_box = FlexBox(
            layout="vertical",
            contents=[
                FlexText(
                    text="位置情報受信",
                    weight="bold",
                    size="xl",
                    color="#ffffff"
                ),
                FlexText(
                    text=title,
                    size="md",
                    color="#ffffff",
                    wrap=True
                ),
            ],
            background_color=color_theme["primary"],
            padding_all="20px",
            spacing="md"
        )

        # 基本情報セクション
        basic_info_contents = [
            FlexText(
                text="基本情報",
                weight="bold",
                size="md",
                color=color_theme["primary"]
            ),
            FlexSeparator(margin="sm"),
            self._create_info_row("住所", address),
            self._create_info_row("座標", f"{lat}, {lng}"),
            self._create_info_row("精度", precision),
        ]

        basic_info_box = FlexBox(
            layout="vertical",
            contents=basic_info_contents,
            margin="lg"
        )

        # 地域情報セクション
        region_info_contents = [
            FlexText(
                text="地域情報",
                weight="bold",
                size="md",
                color=color_theme["primary"]
            ),
            FlexSeparator(margin="sm"),
            self._create_info_row("地域", region),
        ]

        if area:
            region_info_contents.append(self._create_info_row("エリア", area))

        if location_type != "一般位置":
            region_info_contents.append(self._create_info_row("場所タイプ", location_type))

        if nearest_city and nearest_distance is not None:
            distance_text = (
                f"約{nearest_distance*1000:.0f}m" if nearest_distance < 1
                else f"約{nearest_distance:.1f}km"
            )
            region_info_contents.append(
                self._create_info_row("最寄り都市", f"{nearest_city} ({distance_text})")
            )

        region_info_box = FlexBox(
            layout="vertical",
            contents=region_info_contents,
            margin="xl"
        )

        # メインボディ
        body_contents = [basic_info_box, region_info_box]

        body_box = FlexBox(
            layout="vertical",
            contents=body_contents,
            spacing="sm",
            padding_all="20px"
        )

        # フッターボタン（地図リンク）
        footer_contents = []
        if lat != "不明" and lng != "不明":
            map_button = FlexButton(
                style="primary",
                action=URIAction(
                    label="地図で確認",
                    uri=f"https://maps.google.com/?q={lat},{lng}"
                ),
                color=color_theme["primary"]
            )
            footer_contents.append(map_button)

        footer_contents.append(
            FlexText(
                text="位置情報をありがとうございます",
                size="sm",
                color=color_theme["primary"],
                align="center",
                weight="bold",
                wrap=True,
                margin="md"
            )
        )

        footer_box = FlexBox(
            layout="vertical",
            contents=footer_contents,
            spacing="sm",
            padding_all="20px"
        ) if footer_contents else None

        # バブル作成
        bubble = FlexBubble(
            hero=header_box,
            body=body_box,
            footer=footer_box
        )

        return FlexMessage(
            alt_text=f"位置情報: {title}",
            contents=bubble
        )

    def _create_info_row(self, label: str, value: str) -> FlexBox:
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
                    max_lines=3  # 最大3行で表示
                ),
            ],
            margin="md"
        )

    def _get_location_color_theme(self, region: str, location_type: str) -> Dict[str, str]:

        # 地域別色テーマ
        region_colors = {
            "東京": "#FF6B6B",  # 赤系
            "大阪": "#4ECDC4",  # 青緑系
            "名古屋": "#45B7D1", # 青系
            "福岡": "#96CEB4",  # 緑系
            "札幌": "#FFEAA7",  # 黄系
            "沖縄": "#74B9FF",  # 水色系
            "海外": "#A29BFE",  # 紫系
            "日本": "#6C5CE7"   # デフォルト紫
        }

        # 場所タイプ別色テーマ
        type_colors = {
            "交通機関": "#0984E3",
            "飲食店": "#E17055",
            "宿泊施設": "#6C5CE7",
            "公園・レジャー": "#00B894",
            "医療機関": "#E84393",
            "教育機関": "#FDCB6E",
            "商業施設": "#E84393",
            "公共施設": "#74B9FF"
        }

        # 優先度: 場所タイプ > 地域
        primary_color = type_colors.get(location_type) or region_colors.get(region, "#6C5CE7")

        return {
            "primary": primary_color,
            "secondary": "#DDD6FE"
        }

    def _get_location_info(self, event: MessageEvent) -> Dict[str, Any]:
        message = event.message
        location_info = {}

        try:
            # 各属性を安全に取得
            title = getattr(message, "title", None)
            address = getattr(message, "address", None)
            latitude = getattr(message, "latitude", None)
            longitude = getattr(message, "longitude", None)

            # 値が存在する場合のみ追加
            if title:
                location_info["title"] = title
            if address:
                location_info["address"] = address
            if latitude is not None:
                location_info["latitude"] = latitude
            if longitude is not None:
                location_info["longitude"] = longitude

            logger.info(f"Location info: {title} at ({latitude}, {longitude})")

        except Exception as e:
            logger.warning(f"位置情報属性取得エラー: {e}")

        return location_info

    def _analyze_location(self, location_info: Dict[str, Any]) -> Dict[str, Any]:
        lat = location_info.get("latitude")
        lng = location_info.get("longitude")

        analysis = {
            "region": "unknown",
            "timezone": "unknown",
            "type": "point",
            "coordinate_precision": "unknown",
            "location_type": "一般位置",
            "nearest_city": None,
            "nearest_distance": None,
        }

        if lat is not None and lng is not None:
            # 座標の精度を判定
            analysis["coordinate_precision"] = self._determine_coordinate_precision(lat, lng)

            # 日本の地域判定
            region_info = self._determine_japanese_region(lat, lng)
            analysis.update(region_info)

            # 最寄り都市からの距離計算
            distances = self._calculate_distance_from_major_cities(lat, lng)
            nearest_city, nearest_distance = self._get_nearest_city(distances)
            analysis["nearest_city"] = nearest_city
            analysis["nearest_distance"] = nearest_distance

        # 場所のタイプを判定
        analysis["location_type"] = self._determine_location_type(location_info)

        return analysis

    def _determine_coordinate_precision(self, lat: float, lng: float) -> str:
        lat_str = str(lat)
        lng_str = str(lng)

        # 小数点以下の桁数を取得
        lat_decimals = len(lat_str.split(".")[-1]) if "." in lat_str else 0
        lng_decimals = len(lng_str.split(".")[-1]) if "." in lng_str else 0

        min_decimals = min(lat_decimals, lng_decimals)

        if min_decimals >= 5:
            return "高精度"  # 約1m精度
        elif min_decimals >= 3:
            return "中精度"  # 約100m精度
        elif min_decimals >= 1:
            return "低精度"  # 約10km精度
        else:
            return "極低精度"

    def _determine_japanese_region(self, lat: float, lng: float) -> Dict[str, str]:
        # 詳細な地域判定（現在のコードをベース）
        if 35.5 <= lat <= 35.8 and 139.6 <= lng <= 139.9:
            return {"region": "東京都心", "timezone": "JST", "area": "首都圏"}
        elif 34.6 <= lat <= 34.8 and 135.4 <= lng <= 135.6:
            return {"region": "大阪市内", "timezone": "JST", "area": "関西圏"}
        elif 35.1 <= lat <= 35.3 and 139.5 <= lng <= 139.7:
            return {"region": "横浜市内", "timezone": "JST", "area": "首都圏"}
        elif 35.0 <= lat <= 36.0 and 139.0 <= lng <= 140.5:
            return {"region": "東京周辺", "timezone": "JST", "area": "関東地方"}
        elif 34.0 <= lat <= 35.0 and 135.0 <= lng <= 136.5:
            return {"region": "大阪周辺", "timezone": "JST", "area": "関西地方"}
        elif 35.0 <= lat <= 35.3 and 136.8 <= lng <= 137.0:
            return {"region": "名古屋周辺", "timezone": "JST", "area": "中部地方"}
        elif 33.5 <= lat <= 33.7 and 130.3 <= lng <= 130.5:
            return {"region": "福岡周辺", "timezone": "JST", "area": "九州地方"}
        elif 43.0 <= lat <= 43.2 and 141.2 <= lng <= 141.5:
            return {"region": "札幌周辺", "timezone": "JST", "area": "北海道"}
        elif 26.1 <= lat <= 26.3 and 127.6 <= lng <= 127.8:
            return {"region": "那覇周辺", "timezone": "JST", "area": "沖縄県"}
        elif 43.0 <= lat <= 45.5 and 141.0 <= lng <= 146.0:
            return {"region": "北海道", "timezone": "JST", "area": "北海道"}
        elif 24.0 <= lat <= 26.5 and 123.0 <= lng <= 131.5:
            return {"region": "沖縄", "timezone": "JST", "area": "沖縄県"}
        elif 30.0 <= lat <= 46.0 and 129.0 <= lng <= 146.0:
            return {"region": "日本国内", "timezone": "JST", "area": "日本"}
        else:
            return {"region": "海外", "timezone": "unknown", "area": "海外"}

    def _calculate_distance_from_major_cities(self, lat: float, lng: float) -> Dict[str, float]:
        """主要都市からの距離を計算"""
        major_cities = {
            "東京": (35.6762, 139.6503),
            "大阪": (34.6937, 135.5023),
            "名古屋": (35.1815, 136.9066),
            "福岡": (33.5904, 130.4017),
            "札幌": (43.0642, 141.3469),
            "仙台": (38.2682, 140.8694),
            "広島": (34.3853, 132.4553),
            "京都": (35.0116, 135.7681),
            "神戸": (34.6901, 135.1956),
            "熊本": (32.7898, 130.7417),
        }

        distances = {}

        for city_name, (city_lat, city_lng) in major_cities.items():
            # ハバーサイン公式で距離計算
            dlat = math.radians(lat - city_lat)
            dlng = math.radians(lng - city_lng)
            a = (math.sin(dlat / 2) ** 2 +
                 math.cos(math.radians(city_lat)) * math.cos(math.radians(lat)) *
                 math.sin(dlng / 2) ** 2)
            c = 2 * math.asin(math.sqrt(a))
            distance_km = 6371 * c  # 地球の半径 6371km
            distances[city_name] = distance_km

        return distances

    def _get_nearest_city(self, distances: Dict[str, float]) -> tuple:
        if not distances:
            return None, None

        nearest_city = min(distances.keys(), key=lambda city: distances[city])
        nearest_distance = distances[nearest_city]

        return nearest_city, nearest_distance

    def _determine_location_type(self, location_info: Dict[str, Any]) -> str:
        title = location_info.get("title", "").lower()
        address = location_info.get("address", "").lower()
        
        # 複合的にチェック
        combined_text = f"{title} {address}".lower()

        # 交通機関
        if any(keyword in combined_text for keyword in [
            "station", "駅", "停留所", "バス停", "空港", "airport", "port", "港"
        ]):
            return "交通機関"

        # 飲食店
        elif any(keyword in combined_text for keyword in [
            "restaurant", "cafe", "食", "レストラン", "カフェ", "居酒屋", "bar", "バー"
        ]):
            return "飲食店"

        # 宿泊施設
        elif any(keyword in combined_text for keyword in [
            "hotel", "ホテル", "宿泊", "旅館", "民宿", "inn"
        ]):
            return "宿泊施設"

        # 公園・レジャー
        elif any(keyword in combined_text for keyword in [
            "park", "公園", "緑地", "広場", "動物園", "水族館", "遊園地", "テーマパーク"
        ]):
            return "公園・レジャー"

        # 医療機関
        elif any(keyword in combined_text for keyword in [
            "hospital", "病院", "医院", "クリニック", "診療所", "clinic"
        ]):
            return "医療機関"

        # 教育機関
        elif any(keyword in combined_text for keyword in [
            "school", "university", "学校", "大学", "高校", "中学", "小学", "幼稚園"
        ]):
            return "教育機関"

        # 商業施設
        elif any(keyword in combined_text for keyword in [
            "store", "shop", "mall", "店", "モール", "デパート", "百貨店", "コンビニ"
        ]):
            return "商業施設"

        # 公共施設
        elif any(keyword in combined_text for keyword in [
            "市役所", "区役所", "町役場", "図書館", "博物館", "美術館", "hall", "ホール"
        ]):
            return "公共施設"

        else:
            return "一般位置"

    def _format_location_response(
        self, location_info: Dict[str, Any], analysis: Dict[str, Any]
    ) -> str:
        title = location_info.get("title", "位置情報")
        address = location_info.get("address", "住所不明")
        lat = location_info.get("latitude", "不明")
        lng = location_info.get("longitude", "不明")

        region = analysis.get("region", "不明")
        area = analysis.get("area", "")
        precision = analysis.get("coordinate_precision", "不明")
        location_type = analysis.get("location_type", "一般位置")
        nearest_city = analysis.get("nearest_city")
        nearest_distance = analysis.get("nearest_distance")

        response_parts = [
            "位置情報を受信しました！",
            f"タイトル: {title}",
            f"住所: {address}",
            f"座標: {lat}, {lng}",
            f"精度: {precision}",
        ]

        if region != "unknown":
            response_parts.append(f"地域: {region}")

        if area:
            response_parts.append(f"エリア: {area}")

        # 場所タイプ
        if location_type != "一般位置":
            response_parts.append(f"場所タイプ: {location_type}")

        # 最寄り都市情報
        if nearest_city and nearest_distance is not None:
            if nearest_distance < 1:
                response_parts.append(f"最寄り都市: {nearest_city} (約{nearest_distance*1000:.0f}m)")
            else:
                response_parts.append(f"最寄り都市: {nearest_city} (約{nearest_distance:.1f}km)")

        response_parts.append("")  # 空行

        # 地域別のメッセージ
        if "東京" in region:
            response_parts.append("東京からの位置情報ですね！")
        elif "大阪" in region:
            response_parts.append("大阪からの位置情報ですね！")
        elif "沖縄" in region:
            response_parts.append("沖縄からの位置情報ですね！")
        elif "北海道" in region:
            response_parts.append("北海道からの位置情報ですね！")
        elif "海外" in region:
            response_parts.append("海外からの位置情報ですね！")
        elif "日本" in region:
            response_parts.append("日本国内の位置情報ですね！")

        # 場所タイプ別のメッセージ
        if location_type == "交通機関":
            response_parts.append("駅や交通関連の場所ですね！")
        elif location_type == "飲食店":
            response_parts.append("美味しそうなお店ですね！")
        elif location_type == "宿泊施設":
            response_parts.append("宿泊施設ですね！")
        elif location_type == "公園・レジャー":
            response_parts.append("楽しそうな場所ですね！")
        elif location_type == "医療機関":
            response_parts.append("医療関連の施設ですね")
        elif location_type == "教育機関":
            response_parts.append("学校関連の施設ですね")
        elif location_type == "商業施設":
            response_parts.append("ショッピング関連の場所ですね！")
        elif location_type == "公共施設":
            response_parts.append("公共施設ですね")

        # 精度による追加情報
        if precision == "高精度":
            response_parts.append("とても正確な位置情報です！")
        elif precision == "極低精度":
            response_parts.append("おおまかな位置情報ですね")

        # 距離による追加コメント
        if nearest_city and nearest_distance is not None:
            if nearest_distance < 5:
                response_parts.append(f"{nearest_city}市内の位置ですね！")
            elif nearest_distance < 50:
                response_parts.append(f"{nearest_city}近郊の位置情報ですね")

        response_parts.extend(["", "位置情報をありがとうございます！"])

        return "\n".join(response_parts)