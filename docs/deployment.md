# デプロイメントガイド

このドキュメントでは、ローカル開発環境から本番環境へのデプロイメント方法を説明します。

## 🖥 開発環境（ngrok使用）

開発環境のセットアップについては [📝 セットアップガイド](./setup.md) を参照してください。

## 🌐 本番環境デプロイメントオプション

### 推奨プラットフォーム

| プラットフォーム | 難易度 | コスト | 特徴 |
|------------------|--------|--------|------|
| **Railway** | 低 | 低 | Git連携、簡単デプロイ |
| **Heroku** | 低 | 中 | 老舗PaaS、豊富なドキュメント |
| **Google Cloud Run** | 中 | 低 | サーバーレス、スケーラブル |
| **AWS Lambda** | 高 | 低 | サーバーレス、高可用性 |
| **VPS** | 高 | 低 | 自由度高、コスト効率 |

## 🚂 Railway デプロイメント（推奨）

### メリット
- Git プッシュだけで自動デプロイ
- 無料枠が充実
- 環境変数管理が簡単
- ログ確認が容易

### デプロイ手順

#### 1. Railway プロジェクトの作成

1. [Railway](https://railway.app) にサインアップ
2. GitHub アカウントで連携
3. 「New Project」をクリック
4. 「Deploy from GitHub repo」を選択
5. LINE Bot テンプレートリポジトリを選択

#### 2. 環境変数の設定

1. Railway ダッシュボードで作成されたプロジェクトをクリック
2. 「Variables」タブを開く
3. 以下の環境変数を追加：

```env
CHANNEL_ACCESS_TOKEN=your-channel-access-token-here
CHANNEL_SECRET=your-channel-secret-here
ENVIRONMENT=production
```

#### 3. 自動デプロイ確認

- Git にコミット・プッシュすると自動的にデプロイされます
- デプロイ状況は「Deployments」タブで確認

#### 4. ドメインの確認と Webhook URL 設定

1. Railway ダッシュボードの「Settings」→「Domains」でアプリのURLを確認
   - 例：`https://your-app-name.up.railway.app`
2. LINE Developers コンソールで Webhook URL を設定
   - 例：`https://your-app-name.up.railway.app/callback`
3. 「検証」をクリックして接続確認
4. 「Webhook の利用」をオンにする

## 🎯 Heroku デプロイメント

### 前提条件
- Heroku アカウント
- Heroku CLI のインストール

### デプロイ手順

#### 1. Heroku の準備

```bash
# Heroku CLI のインストール（macOS）
brew tap heroku/brew && brew install heroku

# ログイン
heroku login
```

#### 2. Procfile の作成

```bash
# Procfile
web: python app.py
```

#### 3. runtime.txt の作成

```bash
# runtime.txt
python-3.11.0
```

#### 4. Heroku アプリの作成とデプロイ

```bash
# Heroku アプリ作成
heroku create your-linebot-app-name

# 環境変数設定
heroku config:set CHANNEL_ACCESS_TOKEN=your-token
heroku config:set CHANNEL_SECRET=your-secret
heroku config:set ENVIRONMENT=production

# デプロイ
git push heroku main
```

#### 5. Webhook URL の設定

1. Heroku アプリのドメインを確認：`https://your-linebot-app-name.herokuapp.com`
2. LINE Developers コンソールで Webhook URL を設定
3. 接続テストを実行

## ☁️ Google Cloud Run デプロイメント

### 前提条件
- Google Cloud アカウント
- Google Cloud CLI のインストール

### デプロイ手順

#### 1. Dockerfile の作成

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 依存関係のコピーとインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションファイルのコピー
COPY . .

# ポート設定（Cloud Run は PORT 環境変数を使用）
ENV PORT=8080

# アプリケーション起動
CMD exec uvicorn app:app --host 0.0.0.0 --port $PORT
```

#### 2. app.py の修正

```python
# app.py - ポート設定部分を修正
import os

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))  # Cloud Run対応
    uvicorn.run(
        "app:app", 
        host="0.0.0.0", 
        port=port, 
        reload=False  # 本番環境ではreloadオフ
    )
```

#### 3. Cloud Run へのデプロイ

```bash
# Google Cloud CLI でログイン
gcloud auth login

# プロジェクトID設定
gcloud config set project YOUR_PROJECT_ID

# Cloud Run にデプロイ
gcloud run deploy linebot-template \
  --source . \
  --platform managed \
  --region asia-northeast1 \
  --allow-unauthenticated \
  --set-env-vars CHANNEL_ACCESS_TOKEN=your-token,CHANNEL_SECRET=your-secret,ENVIRONMENT=production
```

## 🐳 Docker デプロイメント

### ローカル Docker テスト

```bash
# Docker イメージのビルド
docker build -t linebot-template .

# コンテナの実行
docker run -p 8000:8000 \
  -e CHANNEL_ACCESS_TOKEN=your-token \
  -e CHANNEL_SECRET=your-secret \
  linebot-template
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'
services:
  linebot:
    build: .
    ports:
      - "8000:8000"
    environment:
      - CHANNEL_ACCESS_TOKEN=${CHANNEL_ACCESS_TOKEN}
      - CHANNEL_SECRET=${CHANNEL_SECRET}
      - ENVIRONMENT=production
    restart: unless-stopped

  # オプション: Redis やデータベースを追加
  # redis:
  #   image: redis:alpine
  #   ports:
  #     - "6379:6379"
```

## 🔧 本番環境最適化

### 1. パフォーマンス設定

```python
# app.py - 本番環境設定
import os

# 本番環境では不要な機能を無効化
app = FastAPI(
    title="LINE Bot Template",
    docs_url=None if os.getenv("ENVIRONMENT") == "production" else "/docs",
    redoc_url=None if os.getenv("ENVIRONMENT") == "production" else "/redoc",
    openapi_url=None if os.getenv("ENVIRONMENT") == "production" else "/openapi.json"
)

# ログレベルの調整
log_level = logging.INFO if os.getenv("ENVIRONMENT") == "production" else logging.DEBUG
logging.basicConfig(level=log_level)
```

### 2. ヘルスチェックエンドポイント

```python
# app.py - ヘルスチェック追加
@app.get("/health")
async def health_check():
    """ヘルスチェック用エンドポイント"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "handlers": len(event_handler_map),
        "message": "OK"
    }
```

### 3. 環境変数の検証

```python
# app.py - 本番環境での厳密な検証
def validate_production_environment():
    """本番環境の環境変数を厳密に検証"""
    if os.getenv("ENVIRONMENT") == "production":
        required_vars = ["CHANNEL_ACCESS_TOKEN", "CHANNEL_SECRET"]
        missing = [var for var in required_vars if not os.getenv(var)]
        
        if missing:
            raise ValueError(f"本番環境で必須の環境変数が不足: {missing}")
        
        # トークンの形式チェック（基本的な検証）
        token = os.getenv("CHANNEL_ACCESS_TOKEN")
        if not token or len(token) < 50:
            raise ValueError("CHANNEL_ACCESS_TOKEN が無効です")
        
        secret = os.getenv("CHANNEL_SECRET") 
        if not secret or len(secret) < 20:
            raise ValueError("CHANNEL_SECRET が無効です")
```

## 📊 監視とログ

### 1. 基本的な監視項目

- **応答時間**: Webhook レスポンス時間
- **エラー率**: 4xx, 5xx エラーの発生率
- **メモリ使用量**: アプリケーションメモリ消費
- **CPU 使用率**: プロセッサ使用状況

### 2. ログ管理

```python
# 本番環境での構造化ログ
import json
import logging

class ProductionFormatter(logging.Formatter):
    """本番環境用JSON形式ログフォーマッター"""
    
    def format(self, record):
        log_entry = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry, ensure_ascii=False)

# 本番環境でJSON形式ログを使用
if os.getenv("ENVIRONMENT") == "production":
    handler = logging.StreamHandler()
    handler.setFormatter(ProductionFormatter())
    logging.getLogger().handlers = [handler]
```

### 3. 監視ツールの推奨

| ツール | 用途 | 無料枠 |
|--------|------|--------|
| **UptimeRobot** | 外形監視 | ✅ |
| **Google Cloud Monitoring** | インフラ監視 | ✅ |
| **Railway Metrics** | アプリケーション監視 | ✅ |
| **Sentry** | エラー追跡 | ✅ |

## 🔒 セキュリティ

### 1. 必須セキュリティ設定

```python
# セキュリティヘッダーの追加
from fastapi.middleware.security import SecurityHeadersMiddleware

app.add_middleware(SecurityHeadersMiddleware)

# HTTPS強制（本番環境）
if os.getenv("ENVIRONMENT") == "production":
    @app.middleware("http")
    async def force_https(request, call_next):
        if request.url.scheme != "https":
            return RedirectResponse(
                url=str(request.url).replace("http://", "https://"),
                status_code=301
            )
        return await call_next(request)
```

### 2. レート制限

```python
# レート制限の実装例
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/callback")
@limiter.limit("100/minute")  # 1分間に100リクエストまで
async def webhook_callback(request: Request):
    # 既存の処理
```

## 🎯 本番環境チェックリスト

デプロイ前の確認項目：

### 環境設定
- [ ] 環境変数が正しく設定されている
- [ ] `ENVIRONMENT=production` が設定されている
- [ ] 本番用のログレベルになっている
- [ ] 不要なデバッグ機能が無効化されている

### LINE設定
- [ ] Webhook URL が正しく設定されている
- [ ] 「Webhook の利用」がオンになっている
- [ ] 「応答メッセージ」がオフになっている
- [ ] Bot の基本機能が動作する

### 監視・セキュリティ
- [ ] ヘルスチェックエンドポイントが動作する
- [ ] ログが適切に出力される
- [ ] エラー処理が適切に動作する
- [ ] HTTPS でアクセス可能
- [ ] セキュリティヘッダーが設定されている

### パフォーマンス
- [ ] レスポンス時間が許容範囲内
- [ ] メモリ使用量が適切
- [ ] 並行処理が正しく動作する

## 💡 トラブルシューティング

### よくある本番環境の問題

#### 1. Webhook タイムアウト
**症状**: LINE からの Webhook が失敗する

**解決方法**:
- バックグラウンド処理の実装確認
- 外部API呼び出しのタイムアウト設定
- データベース処理の最適化

#### 2. メモリ不足
**症状**: アプリケーションが頻繁に再起動する

**解決方法**:
- メモリ使用量の監視
- 不要なオブジェクトの削除
- ガベージコレクションの最適化

#### 3. 高負荷時の性能劣化
**症状**: レスポンス時間が長くなる

**解決方法**:
- 非同期処理の最適化
- コネクションプールの使用
- キャッシュの実装

各プラットフォーム固有の問題については、それぞれの公式ドキュメントも参照してください。