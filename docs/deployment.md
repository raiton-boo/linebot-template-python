# ローカル開発と本番環境デプロイメント

ローカル開発環境のセットアップと各種プラットフォームでの本番デプロイメント方法を説明します。

## 🖥 ローカル開発環境（ngrok 使用）

### 前提条件

- Python 3.9+ がインストール済み
- ngrok アカウント（無料で利用可能）

### 1. ngrok のセットアップ

#### ngrok のインストール

```bash
# macOS (Homebrew)
brew install ngrok

# Windows (Chocolatey)
choco install ngrok

# Linux
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
sudo apt update && sudo apt install ngrok
```

#### 認証トークンの設定

1. [ngrok ダッシュボード](https://dashboard.ngrok.com/get-started/your-authtoken) で auth token を取得
2. トークンを設定：

```bash
ngrok config add-authtoken YOUR_AUTH_TOKEN
```

### 2. アプリケーションの起動

#### ターミナル 1: LINE Bot アプリケーション起動

```bash
cd /path/to/your/linebot-template-python
python -m uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

#### ターミナル 2: ngrok でトンネル作成

```bash
ngrok http 8000
```

ngrok が起動すると以下のような出力が表示されます：

```
Session Status                online
Account                      your-email@example.com
Version                      3.x.x
Region                       Japan (jp)
Latency                      -
Web Interface                http://127.0.0.1:4040
Forwarding                   https://abc123def456.ngrok-free.app -> http://localhost:8000
```

### 3. Webhook URL の設定

1. LINE Developers コンソールを開く
2. Webhook URL に ngrok の HTTPS URL + `/callback` を設定
   - 例：`https://abc123def456.ngrok-free.app/callback`
3. 「検証」ボタンで接続確認
4. 「Webhook の利用」をオンにする

### 4. 動作確認

- LINE Bot を友だち追加
- メッセージを送信して鸚鵡返しを確認
- `profile` コマンドでプロフィール取得を確認

### ngrok 使用時の注意点

- 無料版では 8 時間で URL が変更されるため、定期的に Webhook URL の更新が必要
- セッションが切れた場合は ngrok を再起動して新しい URL を設定
- 有料版（Pro 以上）では固定ドメインが利用可能

## 🏗 本番環境デプロイメントオプション

本番環境では各自でサーバーを用意してデプロイしてください。以下は推奨プラットフォームです：

### 推奨プラットフォーム

- **Railway**: モダンなプラットフォーム、Git 連携、シンプル
- **Google Cloud Run**: サーバーレス、スケーラブル、従量課金
- **AWS Lambda**: サーバーレス、高可用性
- **VPS**: 自由度が高い、コスト効率（Linode、DigitalOcean 等）

## 🚂 Railway デプロイメント

### 1. Railway プロジェクトの作成

1. [Railway](https://railway.app) にサインアップ
2. 「New Project」→「Deploy from GitHub repo」を選択
3. リポジトリを選択

### 2. 環境変数の設定

1. Railway ダッシュボードで「Variables」タブを開く
2. 以下の環境変数を追加：
   - `CHANNEL_ACCESS_TOKEN`: your-channel-access-token
   - `CHANNEL_SECRET`: your-channel-secret

### 3. 自動デプロイ

- Git にプッシュすると自動的にデプロイされます
- デプロイ完了後、生成された URL に `/callback` を付けて Webhook URL に設定

### 4. Webhook URL の設定

1. Railway ダッシュボードで生成されたドメインを確認
2. LINE Developers コンソールで Webhook URL を設定
   - 例：`https://your-app-name.up.railway.app/callback`
3. 接続確認を実行

## ☁️ Google Cloud Run デプロイメント

### 1. Dockerfile の作成

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
```

### 2. Cloud Run へのデプロイ

```bash
# Google Cloud CLI でログイン
gcloud auth login

# プロジェクトを設定
gcloud config set project YOUR_PROJECT_ID

# Cloud Run にデプロイ
gcloud run deploy linebot-template \
  --source . \
  --platform managed \
  --region asia-northeast1 \
  --allow-unauthenticated \
  --port 8080 \
  --set-env-vars CHANNEL_ACCESS_TOKEN=your-token,CHANNEL_SECRET=your-secret
```

### 3. Webhook URL の設定

1. デプロイ完了後、表示される URL に `/callback` を付けて Webhook URL に設定
2. LINE Developers コンソールで接続確認を実行

## 🔧 本番環境の設定とベストプラクティス

### セキュリティ設定

#### 環境変数の管理

```python
# app.py での設定例
import os
from dotenv import load_dotenv

# 本番環境では .env ファイルを使用しない
if os.getenv("ENVIRONMENT") != "production":
    load_dotenv()

CHANNEL_ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET = os.getenv("CHANNEL_SECRET")

if not CHANNEL_ACCESS_TOKEN or not CHANNEL_SECRET:
    raise ValueError("必須の環境変数が設定されていません")
```

#### ログレベルの調整

```python
# 本番環境でのログ設定
import logging

# 本番環境では INFO レベル以上のみ
log_level = logging.INFO if os.getenv("ENVIRONMENT") == "production" else logging.DEBUG
logging.basicConfig(level=log_level)
```

### パフォーマンス最適化

#### ワーカープロセス数の設定

```bash
# 本番環境での起動例
uvicorn app:app --host 0.0.0.0 --port $PORT --workers 2
```

#### ヘルスチェックエンドポイント

```python
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": time.time()}
```

## 📊 監視とアラート

### 基本的な監視項目

- HTTP レスポンス時間
- エラー率
- メモリ・CPU 使用率
- Webhook 応答成功率

### おすすめ監視ツール

- **Google Cloud**: Cloud Monitoring
- **Railway**: 組み込み監視ダッシュボード
- **外部**: New Relic, Datadog
- **無料**: UptimeRobot（外形監視）

## 🔒 セキュリティチェックリスト

- [ ] 環境変数で認証情報を管理
- [ ] HTTPS の強制
- [ ] Webhook 署名の検証
- [ ] レート制限の実装
- [ ] ログでの機密情報の除去
- [ ] 依存関係の脆弱性チェック

### 依存関係の脆弱性チェック

```bash
# 定期的に実行
pip audit
```

## 🎯 本番環境チェックリスト

デプロイ前に以下を確認：

- [ ] 環境変数が正しく設定されている
- [ ] Webhook URL が正しく設定されている
- [ ] ヘルスチェックエンドポイントが動作する
- [ ] ログが適切に出力される
- [ ] エラーハンドリングが適切に動作する
- [ ] LINE Bot の基本機能（鸚鵡返し、profile）が動作する
- [ ] 監視・アラートが設定されている

## 💡 トラブルシューティング

### よくある問題

#### Webhook 接続エラー

- サーバーが起動しているか確認
- Webhook URL が正しく設定されているか確認
- HTTPS でアクセス可能か確認

#### 認証エラー

- `CHANNEL_ACCESS_TOKEN` と `CHANNEL_SECRET` が正しく設定されているか確認
- 環境変数に余計なスペースや改行がないか確認

#### メッセージが返ってこない

- サーバーログを確認
- LINE 公式アカウントの応答メッセージがオフになっているか確認
- エラーログで API 呼び出しの失敗を確認

各プラットフォーム固有の問題については、それぞれの公式ドキュメントを参照してください。

#### 1. ヘルスチェックエンドポイント

```python
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": time.time()}
```

#### 2. 構造化ログ（推奨）

```python
import json
import logging

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module
        }
        return json.dumps(log_entry, ensure_ascii=False)

# 本番環境でJSON形式のログを使用
if os.getenv("ENVIRONMENT") == "production":
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    logging.getLogger().addHandler(handler)
```

## 📊 監視とアラート

### 基本的な監視項目

- HTTP レスポンス時間
- エラー率
- メモリ・CPU 使用率
- Webhook 応答成功率

### おすすめ監視ツール

- **Heroku**: Heroku Metrics
- **Google Cloud**: Cloud Monitoring
- **外部**: New Relic, Datadog
- **無料**: UptimeRobot（外形監視）

## 🔒 セキュリティチェックリスト

- [ ] 環境変数で認証情報を管理
- [ ] HTTPS の強制
- [ ] Webhook 署名の検証
- [ ] レート制限の実装
- [ ] ログでの機密情報の除去
- [ ] 依存関係の脆弱性チェック

### 依存関係の脆弱性チェック

```bash
# 定期的に実行
pip audit
```

## 🎯 本番環境チェックリスト

デプロイ前に以下を確認：

- [ ] 環境変数が正しく設定されている
- [ ] Webhook URL が正しく設定されている
- [ ] ヘルスチェックエンドポイントが動作する
- [ ] ログが適切に出力される
- [ ] エラーハンドリングが適切に動作する
- [ ] LINE Bot の基本機能（鸚鵡返し、profile）が動作する
- [ ] 監視・アラートが設定されている

## 📈 スケーリング

### トラフィック増加への対応

- ワーカープロセス数の増加
- 水平スケーリング（複数インスタンス）
- 非同期処理の最適化
- キャッシュの導入（Redis 等）

高トラフィック環境では、より本格的なアーキテクチャ（ロードバランサー、データベース、キューシステム）の導入を検討してください。
