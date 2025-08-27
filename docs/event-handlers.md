# イベントハンドラ詳細ガイド

LINE Bot が受信する各種イベントの詳細と対応するハンドラの動作を説明します。

## 📋 イベント概要

LINE Messaging API では以下のイベントが発生します：

| イベント | 発生条件 | 対応ハンドラ | 実装状況 |
|----------|----------|--------------|----------|
| **MessageEvent** | ユーザーがメッセージ送信 | `MessageEventHandler` | ✅ 実装済み |
| **FollowEvent** | ユーザーが友だち追加 | `FollowEventHandler` | ✅ 実装済み |
| **UnfollowEvent** | ユーザーがブロック | `UnfollowEventHandler` | ✅ 実装済み |
| **JoinEvent** | Botがグループ/ルームに招待 | `JoinEventHandler` | ✅ 実装済み |
| **LeaveEvent** | Botがグループ/ルームから退出 | `LeaveEventHandler` | ✅ 実装済み |
| **MemberJoinedEvent** | メンバーがグループに参加 | `MemberJoinedEventHandler` | ✅ 実装済み |
| **MemberLeftEvent** | メンバーがグループから退出 | `MemberLeftEventHandler` | ✅ 実装済み |
| **PostbackEvent** | ユーザーがPostbackアクション実行 | `PostbackEventHandler` | ✅ 実装済み |
| **BeaconEvent** | LINE Beacon検出 | `BeaconEventHandler` | ✅ 実装済み |
| **VideoPlayCompleteEvent** | 動画再生完了 | `VideoPlayCompleteEventHandler` | ✅ 実装済み |
| **UnsendEvent** | ユーザーがメッセージ削除 | `UnsendEventHandler` | ✅ 実装済み |

## 🔍 各イベントの詳細

### 1. MessageEvent（メッセージイベント）

#### 発生条件
- ユーザーがBotにテキスト、画像、音声、動画、スタンプ、位置情報などを送信
- 1対1トーク、グループ、ルームで発生

#### イベント情報
```json
{
  "type": "message",
  "replyToken": "reply-token-string",
  "source": {
    "type": "user",
    "userId": "U1234567890abcdef"
  },
  "timestamp": 1625097600000,
  "mode": "active",
  "message": {
    "type": "text",
    "id": "message-id",
    "text": "こんにちは"
  }
}
```

#### 対応メッセージタイプ

| メッセージタイプ | 説明 | ハンドラでの処理 |
|------------------|------|------------------|
| **text** | テキストメッセージ | パターンマッチング処理 |
| **image** | 画像メッセージ | 画像受信確認メッセージ |
| **video** | 動画メッセージ | 動画受信確認メッセージ |
| **audio** | 音声メッセージ | 音声受信確認メッセージ |
| **file** | ファイルメッセージ | ファイル名付き受信確認 |
| **location** | 位置情報メッセージ | 住所・緯度経度情報表示 |
| **sticker** | スタンプメッセージ | 親しみやすい返信 |

#### テキストメッセージのパターンマッチング

```python
# 実装されているパターン
patterns = {
    "プロフィール取得": ["profile", "プロフィール", "ぷろふぃーる"],
    "挨拶": ["こんにちは", "おはよう", "こんばんは", "hello", "hi"],
    "感謝": ["ありがとう", "サンキュー", "thanks", "thank you"],
    "ヘルプ": ["ヘルプ", "help", "使い方", "機能"],
    "質問": ["?", "？"]
}
```

### 2. FollowEvent（フォローイベント）

#### 発生条件
- ユーザーがBotを友だち追加
- ユーザーがBotのブロックを解除

#### イベント情報
```json
{
  "type": "follow",
  "replyToken": "reply-token-string",
  "source": {
    "type": "user", 
    "userId": "U1234567890abcdef"
  },
  "timestamp": 1625097600000,
  "mode": "active"
}
```

#### ハンドラの処理
1. ユーザーID取得・ログ記録
2. 歓迎メッセージの送信
3. Bot機能の簡単な説明

#### 歓迎メッセージ例
```
フォローありがとうございます！
何かメッセージを送ってみてください。
```

### 3. UnfollowEvent（アンフォローイベント）

#### 発生条件
- ユーザーがBotをブロック
- ユーザーがBotを友だちから削除

#### 特徴
- **返信不可**: このイベントでは返信メッセージを送信できません
- **統計用**: ユーザー離脱の統計やログ記録に使用

#### ハンドラの処理
1. ユーザーID取得・ログ記録
2. 内部統計の更新（必要に応じて）
3. データベースでのユーザーステータス更新

### 4. JoinEvent（参加イベント）

#### 発生条件
- BotがLINEグループまたはルームに招待される
- 招待者がBotを追加する

#### イベント情報
```json
{
  "type": "join",
  "replyToken": "reply-token-string", 
  "source": {
    "type": "group",
    "groupId": "G1234567890abcdef"
  },
  "timestamp": 1625097600000,
  "mode": "active"
}
```

#### ハンドラの処理
1. 参加先の種類判定（group/room）
2. 参加場所のID取得・ログ記録
3. グループ向け挨拶メッセージの送信

#### 挨拶メッセージ例
```
グループに招待していただき、ありがとうございます！
何かメッセージを送ってみてください。
```

### 5. LeaveEvent（退出イベント）

#### 発生条件
- Botがグループ/ルームから削除される
- グループが解散される

#### 特徴
- **返信不可**: 退出後のため返信メッセージを送信できません
- **ログ専用**: 退出の記録とクリーンアップ処理に使用

#### ハンドラの処理
1. 退出場所の種類・ID取得
2. 退出ログの記録
3. 必要に応じて関連データのクリーンアップ

### 6. MemberJoinedEvent（メンバー参加イベント）

#### 発生条件
- 新しいメンバーがグループに参加
- 他のユーザーが友だちをグループに招待

#### イベント情報
```json
{
  "type": "memberJoined",
  "replyToken": "reply-token-string",
  "source": {
    "type": "group",
    "groupId": "G1234567890abcdef"
  },
  "timestamp": 1625097600000,
  "mode": "active", 
  "joined": {
    "members": [
      {
        "type": "user",
        "userId": "U1234567890abcdef"
      }
    ]
  }
}
```

#### ハンドラの処理
1. 参加メンバー数の取得
2. 参加ログの記録
3. 歓迎メッセージの送信

#### 歓迎メッセージ例
```
2名のメンバーが参加しました！
ようこそ！
```

### 7. MemberLeftEvent（メンバー退出イベント）

#### 発生条件
- メンバーがグループから退出
- メンバーがグループから削除される

#### イベント情報
```json
{
  "type": "memberLeft", 
  "timestamp": 1625097600000,
  "mode": "active",
  "source": {
    "type": "group",
    "groupId": "G1234567890abcdef"
  },
  "left": {
    "members": [
      {
        "type": "user",
        "userId": "U1234567890abcdef"
      }
    ]
  }
}
```

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
```

#### ハンドラの処理
1. ポストバックデータの解析
2. アクションタイプに応じた処理分岐
3. 適切な応答メッセージの送信

### 9. BeaconEvent（ビーコンイベント）

#### 発生条件
- ユーザーがLINE Beacon対応デバイスに近づく
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
1. ビーコンID・タイプの取得
2. 位置情報ログの記録
3. 場所に応じたサービス提供

### 10. VideoPlayCompleteEvent（動画再生完了イベント）

#### 発生条件
- ユーザーがBot送信の動画を最後まで再生
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
1. 動画トラッキングIDの取得
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
1. 削除されたメッセージIDの取得
2. 削除ログの記録
3. 関連データベース情報の削除

## 🔧 ハンドラの内部処理フロー

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

| エラータイプ | ログレベル | 対応 |
|-------------|------------|------|
| **API制限エラー** | WARNING | レート制限検出・再試行 |
| **認証エラー** | ERROR | トークン確認要求 |
| **一般的な処理エラー** | ERROR | エラーログ記録 |
| **重要システムエラー** | CRITICAL | 即座にアラート |

### パフォーマンス監視

- **処理時間監視**: 1秒超過時に警告ログ
- **大量イベント検出**: 5件以上で情報ログ
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

- 即座に200レスポンスを返却
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

このガイドを参考に、各イベントに対する理解を深め、効果的なLINE Botを構築してください。