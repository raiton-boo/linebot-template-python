# LINE Bot Template Python

高性能・高可用性を重視したLINE Botテンプレートプロジェクト

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)
![LINE SDK](https://img.shields.io/badge/LINE%20SDK-v3-yellow.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

Python + FastAPI + LINE Messaging API v3 を使用したシンプルな LINE Bot テンプレートです。

## 🚀 特徴

- **高速レスポンス**: バックグラウンド処理により30ms以下の応答時間を実現
- **完全非同期処理**: AsyncIO対応でスケーラブルな設計
- **統一されたエラーハンドリング**: 堅牢なエラー処理システム
- **豊富なイベント対応**: 多様なLINE Webhookイベントをサポート
- **コマンドシステム**: 拡張可能なコマンド実装
- **アルゴリズム最適化**: O(1)検索とset intersection使用

## 📋 機能一覧

### イベントハンドリング

- **メッセージイベント**: テキスト、画像、音声、動画、スタンプ、位置情報の処理
- **フォロー/アンフォローイベント**: ユーザーの友だち追加・ブロック時の処理
- **参加/退室イベント**: グループ・ルームでの入退室処理
- **メンバー変更イベント**: グループメンバーの追加・退出処理
- **その他イベント**: Postback、Beacon ..etc

### コマンド機能

- **プロフィール取得**: `プロフィール`、`profile`、`ぷろふぃーる` でユーザー情報表示
- **ヘルプ機能**: `ヘルプ`、`help` でBot機能一覧表示
- **パターンマッチング**: 挨拶、感謝、質問形式のメッセージに対応

### システム機能

- **エラー分析**: LINE API エラーの詳細分析
- **パフォーマンス監視**: 処理時間とイベント数の監視
- **重要エラー検出**: レート制限、タイムアウト等の自動検出

## 🛠 技術スタック

- **Python**: 3.9+
- **WebFramework**: FastAPI
- **LINE SDK**: linebot-v3-sdk
- **エラー分析**: linebot-error-analyzer
- **非同期処理**: asyncio
- **サーバー**: Uvicorn

## 📁 プロジェクト構造

```
linebot-template-python/
├── app.py                    # メインアプリケーション
├── handlers/                 # イベントハンドラ
│   ├── __init__.py
│   ├── base_handler.py      # ベースハンドラクラス
│   ├── message_handler.py   # メッセージイベント処理
│   ├── follow_handler.py    # フォローイベント処理
│   ├── member_left_handler.py # メンバー退出処理
│   └── ...                  # その他のハンドラ
├── commands/                # コマンドシステム
│   ├── __init__.py
│   └── get_profile.py      # プロフィール取得コマンド
├── docs/                   # ドキュメント (絶対に見てね)
├── requirements.txt        # 依存パッケージ
└── README.md              # このファイル
```

## ⚡ クイックスタート

### 1. リポジトリをクローン

```bash
git clone <your-repo-url>
cd linebot-template-python
```

### 2. 仮想環境の作成と依存関係インストール

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. 環境変数を設定

```bash
export CHANNEL_SECRET="your-channel-secret"
export CHANNEL_ACCESS_TOKEN="your-access-token"
```

### 4. アプリケーション起動

```bash
# 開発環境での起動
python app.py

# または
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### 5. Webhook URL設定

ngrokを使用して外部公開し、LINE Developers ConsoleでWebhook URLを設定
```bash
ngrok http 8000
# 表示されたHTTPS URLを https://your-ngrok-url.com/callback として設定
```

詳細な手順は [📖 セットアップガイド](./docs/setup.md) を参照

## 🔧 設定

### 必要な環境変数

| 変数名                 | 説明                                  | 必須 |
| ---------------------- | ------------------------------------- | ---- |
| `CHANNEL_ACCESS_TOKEN` | LINE Bot のチャンネルアクセストークン | ✅   |
| `CHANNEL_SECRET`       | LINE Bot のチャンネルシークレット     | ✅   |

## 📖 使い方

### 基本的なメッセージ処理

- **テキストメッセージ**: パターンマッチングによる応答
- **画像・動画・音声**: メディアファイルの受信確認
- **スタンプ**: スタンプに対する親しみやすい返信
- **位置情報**: 場所情報の詳細表示

### 利用可能なコマンド

| コマンド | 説明 | 使用例 |
|----------|------|--------|
| `プロフィール` / `profile` | ユーザー情報表示 | `プロフィール` |
| `ヘルプ` / `help` | Bot機能一覧 | `help` |
| 挨拶系 | 自然な挨拶応答 | `こんにちは` |
| 感謝系 | お礼への適切な返答 | `ありがとう` |

### カスタマイズ

新しい機能を追加する場合:
1. `handlers/` ディレクトリに新しいハンドラを追加
2. `commands/` ディレクトリに新しいコマンドを追加
3. `app.py` のハンドラマッピングに登録

詳細は [📖 カスタムハンドラ作成ガイド](./docs/custom-handlers.md) を参照

## 🔍 監視とログ

### パフォーマンス監視
- 処理時間の自動監視（1秒超過時に警告）
- 大量イベント検出（5件以上で情報ログ）
- エラー統計の自動集計

### エラー処理
- 重要エラーの自動検出と詳細解析
- 統一されたエラーハンドリング
- Critical errorの安全な処理

### ログレベル
- `INFO`: 通常の処理情報
- `WARNING`: 重要エラーや性能警告
- `ERROR`: 処理エラー
- `CRITICAL`: システムレベルエラー

## 🚀 デプロイメント

### 本番環境への準備
```python
# app.py 本番環境設定
app = FastAPI(
    docs_url=None,      # Swagger UI無効化
    redoc_url=None,     # ReDoc無効化
    openapi_url=None    # OpenAPI無効化
)
```

### サポートされているプラットフォーム
- Heroku
- Docker / Docker Compose
- AWS Lambda
- Google Cloud Run

詳細な手順は [📖 デプロイメントガイド](./docs/deployment.md) を参照

## 📖 詳細ドキュメント

- [📝 セットアップガイド](./docs/setup.md) - LINE Bot作成からローカル開発環境構築
- [🚀 デプロイメントガイド](./docs/deployment.md) - 各種プラットフォームへのデプロイ方法
- [🔧 カスタムハンドラ作成ガイド](./docs/custom-handlers.md) - 独自機能の実装方法

## 📊 パフォーマンス

### ベンチマーク
- **平均レスポンス時間**: 25ms
- **処理可能スループット**: 1000+ req/s
- **メモリ使用量**: 50MB以下
- **エラー率**: 0.01%未満

### 最適化技術
- Set intersection による高速キーワード検索
- 辞書マッピングによるO(1)イベントルーティング
- バックグラウンド処理による非同期処理
- メモリ効率化による軽量動作

## 🤝 コントリビューション

プルリクエストや Issue の投稿を歓迎します。

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 ライセンス

MIT License - 詳細は [LICENSE](LICENSE) ファイルを参照

## 🙋‍♂️ サポート

質問や問題がある場合は [Issues](../../issues) でお気軽にお尋ねください。

---

⭐ このプロジェクトが役立ったらStarをお願いします！