# LINE Bot アカウント作成とセットアップ

このドキュメントでは、LINE Bot アカウントの作成からローカル環境での動作確認まで、ステップバイステップで説明します。

## 📋 前提条件

- Python 3.9 以上がインストールされていること
- LINE アカウントを持っていること
- インターネット接続があること

## 1. LINE Developers アカウントの準備

### 1.1 LINE Developers コンソールにアクセス

1. [LINE Developers コンソール](https://developers.line.biz/ja/) にアクセス
2. LINE アカウントでログイン
3. 初回の場合は開発者登録を完了

### 1.2 プロバイダーの作成

1. 「プロバイダー」タブをクリック
2. 「作成」ボタンをクリック
3. プロバイダー名を入力（例：`My Bot Provider`）
4. 「作成」をクリック

## 2. LINE Bot チャンネルの作成

### 2.1 新しいチャンネルの作成

1. 作成したプロバイダーをクリック
2. 「Messaging API」をクリック
3. 必要情報を入力：
   - **チャンネル名**: `My Python Bot`
   - **チャンネル説明**: `Python テンプレート Bot`
   - **大業種・小業種**: 適切なカテゴリを選択
   - **メールアドレス**: 連絡先メールアドレス
4. 各種規約に同意してチャンネルを作成

### 2.2 チャンネル設定の確認

1. 作成したチャンネルをクリック
2. 「チャンネル基本設定」タブで以下を確認：
   - チャンネル ID
   - チャンネルシークレット

## 3. 認証情報の取得

### 3.1 チャンネルアクセストークンの発行

1. 「Messaging API」タブを開く
2. 「チャンネルアクセストークン」セクションで「発行」をクリック
3. 有効期限を設定（推奨：無期限）
4. 生成されたトークンをコピーして保存

### 3.2 Webhook 設定

1. 「Messaging API」タブの「Webhook 設定」で：
   - **Webhook URL**: `https://your-domain.com/callback`
   - **Webhook の利用**: オンにする

### 3.3 応答設定

1. 「Messaging API」タブの「LINE 公式アカウント機能」で：
   - **応答メッセージ**: オフにする
   - **Webhook**: オンにする

## 4. ローカル環境のセットアップ

### 4.1 プロジェクトのセットアップ

```bash
# リポジトリをクローン
git clone <your-repository-url>
cd linebot-template-python

# Python仮想環境の作成（推奨）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存関係のインストール
pip install -r requirements.txt
```

### 4.2 環境変数の設定

```bash
# .envファイルの作成
cp .env.example .env
```

`.env` ファイルを編集して以下の値を設定：

```env
CHANNEL_ACCESS_TOKEN=your-channel-access-token-here
CHANNEL_SECRET=your-channel-secret-here
```

### 4.3 ngrok のセットアップ（開発用）

ローカル開発では、LINE からの Webhook を受信するため外部からアクセス可能な URL が必要です。ngrok を使用してローカルサーバーをインターネットに公開します。

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

# 手動インストール（全OS共通）
# https://ngrok.com/download からダウンロード
```

#### 認証トークンの設定

1. [ngrok](https://ngrok.com) でアカウントを作成（無料）
2. [ダッシュボード](https://dashboard.ngrok.com/get-started/your-authtoken) で auth token を取得
3. 認証トークンを設定：

```bash
ngrok config add-authtoken YOUR_AUTH_TOKEN_HERE
```

#### ngrok の起動

```bash
# ターミナルで ngrok を起動（ポート8000を公開）
ngrok http 8000
```

起動後、以下のような出力が表示されます：

```
Session Status                online
Account                      your-email@example.com (Plan: Free)
Version                      3.x.x
Region                       Japan (jp)
Latency                      -
Web Interface                http://127.0.0.1:4040
Forwarding                   https://abc123def456.ngrok-free.app -> http://localhost:8000
```

**重要**: `https://abc123def456.ngrok-free.app` の部分をコピーしてください。これが Webhook URL に使用するベース URL です。

## 5. Bot の起動と動作確認

### 5.1 アプリケーションの起動

**ターミナル 1** で LINE Bot アプリケーションを起動：

```bash
cd linebot-template-python
python -m uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

**ターミナル 2** で ngrok を起動（既に起動済みの場合はスキップ）：

```bash
ngrok http 8000
```

### 5.2 Webhook URL の設定

1. LINE Developers コンソールに戻る
2. 「Messaging API」タブの「Webhook 設定」セクション
3. 「Webhook URL」に ngrok の HTTPS URL + `/callback` を入力
   - 例：`https://abc123def456.ngrok-free.app/callback`
4. 「検証」ボタンをクリックして接続確認
5. 接続成功後、「Webhook の利用」をオンにする
6. 「更新」をクリック

### 5.3 Bot の動作テスト

1. LINE Developers コンソールの「Messaging API」タブで QR コードを表示
2. スマートフォンの LINE アプリで QR コードを読み取り、Bot を友だち追加
3. Bot に以下のメッセージを送信してテスト：
   - `こんにちは` → 鸚鵡返しが返ってくる
   - `profile` → あなたのプロフィール情報が表示される

### 5.4 開発時の注意点

- **ngrok 無料版の制限**: セッションは 8 時間で切れ、URL が変更されます
- **URL 変更時の対応**: ngrok 再起動時は新しい URL を Webhook URL に再設定
- **デバッグ**: ngrok の Web Interface（`http://127.0.0.1:4040`）でリクエスト内容を確認可能
- **複数開発者**: 有料版なら固定ドメインが利用可能

## 6. トラブルシューティング

### よくある問題と解決方法

#### Webhook 接続エラー

- ngrok が起動しているか確認
- Webhook URL が正しく設定されているか確認
- アプリケーションが起動しているか確認

#### 認証エラー

- `CHANNEL_ACCESS_TOKEN` と `CHANNEL_SECRET` が正しく設定されているか確認
- トークンに余計なスペースや改行がないか確認

#### メッセージが返ってこない

- ログを確認（`python -m uvicorn app:app --log-level debug`）
- LINE 公式アカウントの応答メッセージがオフになっているか確認

### ログの確認方法

```bash
# 詳細ログで起動
python -m uvicorn app:app --reload --host 0.0.0.0 --port 8000 --log-level debug
```

## 🎉 完了

これで LINE Bot が正常に動作するはずです！次は [カスタムハンドラの作成](./custom-handlers.md) で Bot の機能を拡張してみましょう。
