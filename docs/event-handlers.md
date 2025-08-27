# LINE Bot イベントハンドラ完全ガイド

LINE Messaging API v3 で受信する全 13 種類のイベントの詳細仕様、発生条件、実装例、活用方法を網羅的に解説します。

## � 目次

- [�📋 イベント概要一覧](#-イベント概要一覧)
- [🔍 各イベントの詳細解説](#-各イベントの詳細解説)
  - [メッセージ系イベント](#メッセージ系イベント)
  - [ユーザーインタラクション系イベント](#ユーザーインタラクション系イベント)
  - [グループ・ルーム管理系イベント](#グループ・ルーム管理系イベント)
  - [特殊機能系イベント](#特殊機能系イベント)
  - [サービス連携系イベント](#サービス連携系イベント)
- [🔧 実装のベストプラクティス](#-実装のベストプラクティス)
- [📊 エラーハンドリング](#-エラーハンドリング)

## 📋 イベント概要一覧

| カテゴリ                       | イベント                 | 発生条件         | reply_token | 対応ハンドラ                    | 実装状況    |
| ------------------------------ | ------------------------ | ---------------- | ----------- | ------------------------------- | ----------- |
| **メッセージ系**               | `MessageEvent`           | メッセージ送信   | ✅ あり     | `MessageEventHandler`           | ✅ 実装済み |
|                                | `UnsendEvent`            | メッセージ削除   | ❌ なし     | `UnsendEventHandler`            | ✅ 実装済み |
| **ユーザーインタラクション系** | `FollowEvent`            | 友だち追加       | ✅ あり     | `FollowEventHandler`            | ✅ 実装済み |
|                                | `UnfollowEvent`          | ブロック/削除    | ❌ なし     | `UnfollowEventHandler`          | ✅ 実装済み |
|                                | `PostbackEvent`          | ボタンタップ     | ✅ あり     | `PostbackEventHandler`          | ✅ 実装済み |
| **グループ・ルーム管理系**     | `JoinEvent`              | Bot 招待         | ✅ あり     | `JoinEventHandler`              | ✅ 実装済み |
|                                | `LeaveEvent`             | Bot 退出         | ❌ なし     | `LeaveEventHandler`             | ✅ 実装済み |
|                                | `MemberJoinedEvent`      | メンバー参加     | ✅ あり     | `MemberJoinedEventHandler`      | ✅ 実装済み |
|                                | `MemberLeftEvent`        | メンバー退出     | ❌ なし     | `MemberLeftEventHandler`        | ✅ 実装済み |
| **特殊機能系**                 | `BeaconEvent`            | Beacon 検出      | ✅ あり     | `BeaconEventHandler`            | ✅ 実装済み |
|                                | `VideoPlayCompleteEvent` | 動画再生完了     | ✅ あり     | `VideoPlayCompleteEventHandler` | ✅ 実装済み |
| **サービス連携系**             | `AccountLinkEvent`       | アカウント連携   | ✅ あり     | `AccountLinkEventHandler`       | ✅ 実装済み |
|                                | `ThingsEvent`            | IoT デバイス通知 | ⚠️ 条件付き | `ThingsEventHandler`            | ✅ 実装済み |

## 🔍 各イベントの詳細解説

---

## メッセージ系イベント

### 1. MessageEvent（メッセージイベント）

#### 📍 発生条件とタイミング

- **基本条件**: ユーザーが Bot にメッセージを送信したとき
- **発生場所**: 1 対 1 トーク、グループトーク、ルーム
- **送信者制限**: LINE ユーザーのみ（Bot 同士では発生しない）
- **頻度**: 最も高頻度で発生するイベント

#### 🎯 対応可能なメッセージタイプと特徴

| メッセージタイプ | 説明     | 取得可能な情報             | ビジネス活用例           |
| ---------------- | -------- | -------------------------- | ------------------------ |
| **text**         | テキスト | 本文、メンション、絵文字   | チャットボット、検索機能 |
| **image**        | 画像     | ファイルサイズ、形式       | 画像認識、商品検索       |
| **video**        | 動画     | 長さ、サイズ、サムネイル   | 動画解析、コンテンツ管理 |
| **audio**        | 音声     | 長さ、形式                 | 音声認識、音楽識別       |
| **file**         | ファイル | ファイル名、サイズ         | 文書管理、データ収集     |
| **location**     | 位置情報 | 緯度経度、住所、タイトル   | 店舗検索、配達サービス   |
| **sticker**      | スタンプ | スタンプ ID、パッケージ ID | ユーザー感情分析         |

#### 💡 高度な活用テクニック

**テキスト解析パターン**

```python
# 実装例：意図理解システム
patterns = {
    "商品検索": [r".*探して", r".*検索", r".*見つけて"],
    "予約": [r".*予約", r".*空いて", r".*取りたい"],
    "問い合わせ": [r"質問", r"教えて", r".*について"],
    "緊急": [r"緊急", r"至急", r"すぐに"]
}
```

**位置情報活用**

```python
# 実装例：近隣サービス検索
location_data = {
    "latitude": event.message.latitude,
    "longitude": event.message.longitude,
    "address": event.message.address
}
# 半径2km以内の店舗検索など
```

#### ⚠️ 重要な制限事項

- **ファイルサイズ制限**: 画像・動画は 100MB、音声は 200MB
- **メッセージ長制限**: テキストは最大 5,000 文字
- **レート制限**: 連続送信に注意が必要

---

### 2. UnsendEvent（送信取消イベント）

#### 📍 発生条件とタイミング

- **基本条件**: ユーザーが送信済みメッセージを「送信取消」したとき
- **対象範囲**: 24 時間以内に送信されたメッセージのみ
- **発生制限**: 送信者本人のみが取消可能

#### 🛠️ ビジネス活用シーン

- **誤送信対応**: 顧客の誤送信を検知してフォロー
- **データクリーンアップ**: 関連する処理済みデータの削除
- **統計調整**: メッセージ分析データの修正

#### イベント構造と活用例

```json
{
  "type": "unsend",
  "source": { "type": "user", "userId": "U1234..." },
  "unsend": { "messageId": "12345678901234567890" }
}
```

```python
# 実装例：関連データの削除
async def handle_unsend(self, event):
    message_id = event.unsend.message_id
    # データベースから関連情報を削除
    await delete_analysis_data(message_id)
    # 処理中のタスクがあればキャンセル
    await cancel_processing_task(message_id)
```

---

## ユーザーインタラクション系イベント

### 3. FollowEvent（フォローイベント）

#### 📍 発生条件とタイミング

- **友だち追加時**: QR コード、ID 検索、友だち紹介経由
- **ブロック解除時**: 以前ブロックしたユーザーが解除
- **公式アカウント**: 企業アカウントでの友だち登録

#### 🎯 マーケティング活用戦略

**セグメント別オンボーディング**

```python
# 流入経路別の初回メッセージ
onboarding_messages = {
    "qr_code": "QRコードからのご登録ありがとうございます！",
    "search": "検索からお見つけいただき、ありがとうございます！",
    "referral": "ご紹介いただき、ありがとうございます！"
}
```

**ユーザー属性分析**

```python
# 友だち登録と同時に基本情報取得
async def analyze_new_follower(user_id):
    profile = await get_user_profile(user_id)
    # セグメント分析、パーソナライズ設定
    return setup_personalization(profile)
```

#### 💼 ビジネス成果指標

- **CVR 向上**: 初回メッセージの開封率・反応率
- **LTV 最大化**: ユーザージャーニーの設計
- **リテンション**: 長期利用率の改善

---

### 4. UnfollowEvent（アンフォローイベント）

#### 📍 発生条件とタイミング

- **ブロック**: ユーザーが Bot をブロック
- **友だち削除**: 友だちリストから削除
- **アカウント削除**: ユーザーが LINE アカウント削除

#### 📊 チャーン分析の重要性

**離脱パターン分析**

```python
# 離脱前の行動分析
churn_analysis = {
    "last_interaction": "最後のやり取りからの経過時間",
    "interaction_frequency": "やり取り頻度の変化",
    "content_engagement": "コンテンツへの反応度",
    "support_history": "サポート利用歴"
}
```

**改善アクション**

- **プロダクト改善**: 離脱要因の特定と修正
- **コンテンツ最適化**: エンゲージメント向上施策
- **サポート強化**: 顧客満足度向上

---

### 5. PostbackEvent（ポストバックイベント）

#### 📍 発生条件と UI 要素

- **リッチメニュー**: 常時表示のメニューボタン
- **テンプレートメッセージ**: カルーセル、ボタンテンプレート
- **クイックリプライ**: メッセージ下部の選択肢
- **Flex Message**: カスタムレイアウト内のボタン

#### 🎨 UI/UX 設計パターン

**多段階フォーム**

```python
# 段階的な情報収集
postback_flows = {
    "reservation_start": "予約開始",
    "select_date": "日付選択",
    "select_time": "時間選択",
    "confirm_booking": "予約確認"
}
```

**パーソナライズメニュー**

```python
# ユーザー属性に応じたメニュー
def generate_menu(user_segment):
    if user_segment == "premium":
        return premium_menu_template
    else:
        return standard_menu_template
```

#### 📈 コンバージョン最適化

- **A/B テスト**: ボタンテキスト、色、配置の最適化
- **ファネル分析**: 各ステップの離脱率測定
- **UX 改善**: タップ数削減、直感的な操作性

---

## グループ・ルーム管理系イベント

### 6. JoinEvent（参加イベント）

#### 📍 発生条件とコンテキスト

- **グループ招待**: メンバーが Bot を招待
- **ルーム追加**: ルーム作成者が Bot 追加
- **権限付与**: 管理者権限での Bot 追加

#### 🌟 グループ活性化戦略

**初回挨拶とルール説明**

```python
welcome_messages = {
    "group": {
        "greeting": "グループに参加させていただきました！",
        "features": "以下の機能をご利用いただけます：
• メンション機能
• スケジュール管理
• 投票機能",
        "rules": "「@botname ヘルプ」で使い方を確認できます"
    }
}
```

**グループタイプ別対応**

```python
group_settings = {
    "business": {"formal_tone": True, "business_features": True},
    "casual": {"emoji_usage": True, "fun_features": True},
    "community": {"moderation": True, "announcement": True}
}
```

### 7. LeaveEvent（退出イベント）

#### 📍 発生条件

- **手動削除**: グループ管理者が Bot を削除
- **グループ解散**: グループ自体が解散
- **自動退出**: システムエラーや制限による退出

#### 🧹 データクリーンアップ戦略

```python
async def cleanup_group_data(group_id):
    # 関連データの整理
    await delete_group_messages(group_id)
    await remove_scheduled_tasks(group_id)
    await update_user_statistics(group_id)
    await notify_analytics_system(group_id, "group_left")
```

### 8. MemberJoinedEvent（メンバー参加イベント）

#### 📍 発生条件

- **新規招待**: 既存メンバーが新しいユーザーを招待
- **招待リンク**: 招待 URL からの参加
- **QR コード**: グループ QR コードでの参加

#### 👥 コミュニティ活性化

**歓迎フロー設計**

```python
async def welcome_new_members(joined_members):
    for member in joined_members:
        # 個別歓迎メッセージ
        await send_welcome_dm(member.user_id)
        # グループでの紹介
        await introduce_member_to_group(member)
        # オンボーディング開始
        await start_onboarding_flow(member.user_id)
```

### 9. MemberLeftEvent（メンバー退出イベント）

#### 📍 発生条件とパターン

- **自主退出**: メンバー自身がグループを退出
- **強制退出**: 管理者によるメンバー削除
- **アカウント削除**: ユーザーの LINE 退会

#### 📊 グループ健全性監視

```python
# グループの健全性指標
group_health_metrics = {
    "member_turnover": "メンバーの入退出率",
    "activity_level": "発言頻度・参加度",
    "engagement_score": "Bot機能の利用率",
    "satisfaction": "満足度調査結果"
}
```

---

## 特殊機能系イベント

### 10. BeaconEvent（ビーコンイベント）

#### 📍 発生条件と IoT 連携

- **物理的近接**: LINE Beacon デバイスの検出範囲内
- **アプリアクティブ**: LINE アプリがフォアグラウンド状態
- **Bluetooth 有効**: ユーザーの Bluetooth 機能が ON

#### 🏪 O2O（Online to Offline）戦略

**位置ベースサービス**

```python
beacon_services = {
    "retail": {
        "enter": "入店ポイント付与、クーポン配布",
        "stay": "商品レコメンデーション",
        "leave": "購入促進メッセージ"
    },
    "event": {
        "enter": "イベント情報、タイムテーブル",
        "stay": "リアルタイム情報更新",
        "leave": "アンケート、次回案内"
    }
}
```

**パーソナライズド体験**

```python
async def beacon_personalization(user_id, beacon_id, action_type):
    user_history = await get_visit_history(user_id, beacon_id)
    preferences = await get_user_preferences(user_id)

    if action_type == "enter":
        return generate_welcome_offer(user_history, preferences)
    elif action_type == "stay":
        return provide_contextual_info(preferences)
```

### 11. VideoPlayCompleteEvent（動画再生完了イベント）

#### 📍 発生条件

- **完全視聴**: ユーザーが動画を最後まで再生
- **trackingId 設定**: 動画メッセージでトラッキング ID が設定済み
- **アプリ内再生**: LINE アプリ内での再生のみ

#### 📺 動画マーケティング活用

**エンゲージメント分析**

```python
video_analytics = {
    "completion_rate": "完視聴率の測定",
    "user_segmentation": "視聴行動によるセグメント分け",
    "content_optimization": "人気コンテンツの特定",
    "funnel_analysis": "動画→アクションの転換率"
}
```

**フォローアップ戦略**

```python
async def video_follow_up(user_id, video_id):
    video_content = await get_video_metadata(video_id)

    if video_content.category == "tutorial":
        # チュートリアル完了→次のステップ案内
        return send_next_tutorial(user_id)
    elif video_content.category == "product":
        # 商品紹介→購入リンク送信
        return send_purchase_link(user_id, video_content.product_id)
```

---

## サービス連携系イベント

### 12. AccountLinkEvent（アカウント連携イベント）

#### 📍 発生条件と OAuth 連携

- **認証完了**: 外部サービス（Google、Facebook 等）との認証成功
- **連携解除**: ユーザーによる連携解除操作
- **トークン更新**: アクセストークンの自動更新

#### 🔗 シングルサインオン（SSO）活用

**マルチサービス連携**

```python
service_integrations = {
    "google": {
        "calendar": "スケジュール管理",
        "drive": "ファイル共有",
        "gmail": "メール通知"
    },
    "microsoft": {
        "teams": "会議連携",
        "office365": "文書編集",
        "outlook": "予定管理"
    },
    "salesforce": {
        "crm": "顧客管理",
        "marketing": "キャンペーン連携"
    }
}
```

**セキュリティベストプラクティス**

```python
async def secure_account_link(user_id, service, auth_result):
    if auth_result == "ok":
        # 暗号化してトークン保存
        await store_encrypted_token(user_id, service, auth_token)
        # 連携完了通知
        await notify_successful_link(user_id, service)
        # セキュリティログ記録
        await log_security_event(user_id, "account_linked", service)
```

### 13. ThingsEvent（LINE Things イベント）

#### 📍 発生条件と IoT エコシステム

- **デバイス接続**: IoT デバイスと LINE Things プラットフォームの連携
- **センサーデータ**: 温度、湿度、動きなどのセンサー情報
- **アクション実行**: デバイス操作の実行結果

#### 🏠 スマートホーム・IoT 活用例

**デバイスタイプ別活用**

```python
iot_device_handlers = {
    "smart_home": {
        "temperature": "エアコン自動制御",
        "security": "不審者検知通知",
        "lighting": "照明スケジュール管理"
    },
    "wearable": {
        "health": "健康データ記録",
        "activity": "運動量トラッキング",
        "sleep": "睡眠質監視"
    },
    "industrial": {
        "monitoring": "設備状態監視",
        "alert": "異常検知アラート",
        "maintenance": "メンテナンス予測"
    }
}
```

**リアルタイム通知システム**

```python
async def process_iot_data(device_id, sensor_data):
    # しきい値チェック
    if sensor_data.temperature > 35:
        await send_heat_alert(device_id)

    # 異常検知
    if detect_anomaly(sensor_data):
        await trigger_emergency_protocol(device_id)

    # データ蓄積・分析
    await store_sensor_data(device_id, sensor_data)
    await update_analytics_dashboard(device_id)
```

---

## 🔧 実装のベストプラクティス

### パフォーマンス最適化

#### 非同期処理の活用

```python
import asyncio

async def handle_multiple_events(events):
    # 並行処理で高速化
    tasks = [process_event(event) for event in events]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # エラーと正常処理を分離
    successes = [r for r in results if not isinstance(r, Exception)]
    errors = [r for r in results if isinstance(r, Exception)]

    return {"successes": len(successes), "errors": len(errors)}
```

#### レート制限対策

```python
from asyncio import Semaphore

class RateLimitedAPI:
    def __init__(self, max_concurrent=10):
        self.semaphore = Semaphore(max_concurrent)

    async def send_message(self, message):
        async with self.semaphore:
            # API呼び出し制限
            await asyncio.sleep(0.1)  # 100ms間隔
            return await self._api_call(message)
```

### セキュリティ強化

#### Webhook 検証

```python
import hmac
import hashlib

def verify_webhook_signature(body, signature, secret):
    expected = hmac.new(
        secret.encode(),
        body.encode(),
        hashlib.sha256
    ).digest()

    received = base64.b64decode(signature.split(',')[1])
    return hmac.compare_digest(expected, received)
```

#### データ暗号化

```python
from cryptography.fernet import Fernet

class SecureStorage:
    def __init__(self, key):
        self.cipher = Fernet(key)

    def encrypt_user_data(self, data):
        return self.cipher.encrypt(data.encode())

    def decrypt_user_data(self, encrypted_data):
        return self.cipher.decrypt(encrypted_data).decode()
```

---

## 📊 エラーハンドリング

### 段階的エラー対応

```python
class SmartErrorHandler:
    async def handle_api_error(self, error, context):
        if "rate limit" in str(error).lower():
            # レート制限→指数バックオフ
            await self.exponential_backoff(context)
        elif "token" in str(error).lower():
            # 認証エラー→トークン更新
            await self.refresh_token(context)
        elif "quota" in str(error).lower():
            # クォータ超過→代替手段
            await self.use_fallback_method(context)
        else:
            # その他→詳細ログ
            await self.log_detailed_error(error, context)
```

### 監視とアラート

```python
class MonitoringSystem:
    def __init__(self):
        self.error_threshold = 0.05  # 5%エラー率
        self.response_time_limit = 3.0  # 3秒

    async def monitor_health(self):
        metrics = await self.collect_metrics()

        if metrics.error_rate > self.error_threshold:
            await self.send_alert("HIGH_ERROR_RATE", metrics)

        if metrics.avg_response_time > self.response_time_limit:
            await self.send_alert("SLOW_RESPONSE", metrics)
```

このガイドを参考に、各イベントの特性を理解し、ビジネス要件に最適な LINE Bot を構築してください。

## パフォーマンス最適化のポイント

### 1. 非同期処理の活用

````

#### 特徴

- **reply_token なし**: 返信メッセージを送信できません
- **統計専用**: 退出の記録と統計更新に使用

#### ハンドラの処理

1. 退出メンバーの情報取得
2. 退出ログの記録
3. グループ統計の更新

### 8. PostbackEvent（ポストバックイベント）

#### 発生条件

- ユーザーがリッチメニューのボタンをタップ
- テンプレートメッセージのアクションを実行
- クイックリプライの選択肢をタップ

#### イベント情報

```json
{
  "type": "postback",
  "replyToken": "reply-token-string",
  "source": {
    "type": "user",
    "userId": "U1234567890abcdef"
  },
  "timestamp": 1625097600000,
  "mode": "active",
  "postback": {
    "data": "action=menu&item=1",
    "params": {
      "date": "2023-07-01"
    }
  }
}
````

#### ハンドラの処理

1. ポストバックデータの解析
2. アクションタイプに応じた処理分岐
3. 適切な応答メッセージの送信

### 9. BeaconEvent（ビーコンイベント）

#### 発生条件

- ユーザーが LINE Beacon 対応デバイスに近づく
- LINE アプリでビーコンが検出される

#### イベント情報

```json
{
  "type": "beacon",
  "replyToken": "reply-token-string",
  "source": {
    "type": "user",
    "userId": "U1234567890abcdef"
  },
  "timestamp": 1625097600000,
  "mode": "active",
  "beacon": {
    "hwid": "d41d8cd98f",
    "type": "enter"
  }
}
```

#### ビーコンタイプ

- **enter**: ビーコンエリアに入った
- **leave**: ビーコンエリアから出た
- **stay**: ビーコンエリアに滞在中

#### ハンドラの処理

1. ビーコン ID・タイプの取得
2. 位置情報ログの記録
3. 場所に応じたサービス提供

### 10. VideoPlayCompleteEvent（動画再生完了イベント）

#### 発生条件

- ユーザーが Bot 送信の動画を最後まで再生
- 動画メッセージで `trackingId` が設定されている場合

#### イベント情報

```json
{
  "type": "videoPlayComplete",
  "replyToken": "reply-token-string",
  "source": {
    "type": "user",
    "userId": "U1234567890abcdef"
  },
  "timestamp": 1625097600000,
  "mode": "active",
  "videoPlayComplete": {
    "trackingId": "tracking-id-string"
  }
}
```

#### ハンドラの処理

1. 動画トラッキング ID の取得
2. 視聴完了ログの記録
3. フォローアップメッセージの送信

### 11. UnsendEvent（送信取消イベント）

#### 発生条件

- ユーザーが自分の送信したメッセージを削除（送信取消）

#### イベント情報

```json
{
  "type": "unsend",
  "timestamp": 1625097600000,
  "mode": "active",
  "source": {
    "type": "user",
    "userId": "U1234567890abcdef"
  },
  "unsend": {
    "messageId": "message-id-string"
  }
}
```

#### 特徴

- **reply_token なし**: 返信メッセージを送信できません
- **削除対応**: 関連データの削除処理に使用

#### ハンドラの処理

1. 削除されたメッセージ ID の取得
2. 削除ログの記録
3. 関連データベース情報の削除

### 12. AccountLinkEvent（アカウント連携イベント）

#### 発生条件

- ユーザーがアカウント連携を完了
- 外部サービス（Google、Facebook 等）との認証が完了

#### イベント情報

```json
{
  "type": "accountLink",
  "replyToken": "reply-token-string",
  "source": {
    "type": "user",
    "userId": "U1234567890abcdef"
  },
  "timestamp": 1625097600000,
  "mode": "active",
  "link": {
    "result": "ok",
    "nonce": "nonce-string"
  }
}
```

#### 連携結果

- **ok**: 連携成功
- **failed**: 連携失敗

#### ハンドラの処理

1. 連携結果の確認
2. 成功時: 外部サービス機能の有効化
3. 失敗時: 再試行の案内

#### 応答メッセージ例

```
✅ アカウント連携が完了しました！
これで外部サービスと連携した機能をご利用いただけます。
```

### 13. ThingsEvent（LINE Things イベント）

#### 発生条件

- LINE Things デバイスからの通知
- IoT デバイスの状態変更
- センサーデータの受信

#### イベント情報

```json
{
  "type": "things",
  "source": {
    "type": "user",
    "userId": "U1234567890abcdef"
  },
  "timestamp": 1625097600000,
  "mode": "active",
  "things": {
    "deviceId": "device-id-string",
    "type": "link"
  }
}
```

#### デバイスイベントタイプ

- **link**: デバイス接続
- **unlink**: デバイス切断
- **scenarioResult**: シナリオ実行結果

#### ハンドラの処理

1. デバイス ID・イベントタイプの取得
2. デバイス状態の管理
3. ユーザーへの状況通知

#### 通知メッセージ例

```
� IoTデバイス（device-001）が正常に接続されました。
```

### 14. DeliveryEvent（配信イベント）

#### 発生条件

- Push メッセージの配信完了
- Broadcast メッセージの配信完了
- Multicast メッセージの配信完了

#### イベント情報

```json
{
  "type": "delivery",
  "timestamp": 1625097600000,
  "mode": "active",
  "delivery": {
    "requestId": "request-id-string"
  }
}
```

#### 特徴

- **reply_token なし**: 返信メッセージを送信できません
- **統計専用**: 配信状況の監視とメトリクス収集に使用

#### ハンドラの処理

1. 配信リクエスト ID の取得
2. 配信完了ログの記録
3. 配信統計の更新

### 15. ActivatedEvent（アクティベートイベント）

#### 発生条件

- LINE 公式アカウントが有効化
- Channel の Webhook URL が設定された直後

#### イベント情報

```json
{
  "type": "activated",
  "timestamp": 1625097600000,
  "mode": "active"
}
```

#### 特徴

- **reply_token なし**: 返信メッセージを送信できません
- **初期化専用**: アカウント設定の自動化に使用

#### ハンドラの処理

1. アカウント有効化ログの記録
2. 初期設定の自動実行
3. 管理者への通知

### 16. DeactivatedEvent（非アクティベートイベント）

#### 発生条件

- LINE 公式アカウントが無効化
- Channel の Webhook URL が削除

#### イベント情報

```json
{
  "type": "deactivated",
  "timestamp": 1625097600000,
  "mode": "active"
}
```

#### 特徴

- **reply_token なし**: 返信メッセージを送信できません
- **緊急対応**: アカウント無効化の緊急処理に使用

#### ハンドラの処理

1. アカウント無効化ログの記録
2. リソースのクリーンアップ
3. 管理者への緊急通知

## �🔧 ハンドラの内部処理フロー

### 共通エラーハンドリング

すべてのハンドラは以下の共通パターンに従います：

```python
async def handle(self, event) -> None:
    try:
        # メイン処理
        await self._process_event(event)

    except Exception as error:
        # 安全なエラーハンドリング
        await self._safe_error_handle(error, event)
        raise  # エラーを再発生させて上位に通知
```

### エラーレベル分類

| エラータイプ           | ログレベル | 対応                   |
| ---------------------- | ---------- | ---------------------- |
| **API 制限エラー**     | WARNING    | レート制限検出・再試行 |
| **認証エラー**         | ERROR      | トークン確認要求       |
| **一般的な処理エラー** | ERROR      | エラーログ記録         |
| **重要システムエラー** | CRITICAL   | 即座にアラート         |

### パフォーマンス監視

- **処理時間監視**: 1 秒超過時に警告ログ
- **大量イベント検出**: 5 件以上で情報ログ
- **並行処理**: `asyncio.gather` による高速処理

## 📊 イベント統計

### 処理統計の記録

```python
# 処理完了時のログ例
INFO: 処理完了 - 成功: 8 / エラー: 1  # エラーがある場合のみ
WARNING: 処理時間超過: 1.25秒         # 1秒超過時のみ
INFO: 大量イベント処理開始: 12件       # 5件以上の場合
```

### 重要エラーの自動検出

以下のキーワードを含むエラーは重要エラーとして詳細解析されます：

```python
CRITICAL_ERROR_KEYWORDS = {"rate", "limit", "timeout", "server", "quota"}
```

## 🎯 実装のベストプラクティス

### 1. イベント処理の最適化

- 即座に 200 レスポンスを返却
- バックグラウンドで並行処理
- エラー時もユーザー体験を損なわない

### 2. ログの効率化

- 通常時は必要最小限のログ
- エラー時は詳細な診断情報
- 本番環境での構造化ログ

### 3. 拡張性の確保

- 新しいイベントタイプの追加が容易
- ハンドラの独立性維持
- 設定による機能の ON/OFF

### 4. セキュリティ対策

- アカウント連携時の認証検証
- IoT デバイス通信の暗号化
- 管理者通知の適切な実装

このガイドを参考に、各イベントに対する理解を深め、効果的な LINE Bot を構築してください。
