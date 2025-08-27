# LINE Bot セットアップガイド

このドキュメントでは、LINE Bot アカウントの作成からローカル環境での動作確認まで、ステップバイステップで説明します。

## 📋 前提条件

- Python 3.8 以上がインストールされていること
- LINE アカウントを持っていること
- インターネット接続があること

## 🔧 1. LINE Developers アカウントの準備

### 1.1 LINE Developers コンソールにアクセス

1. [LINE Developers コンソール](https://developers.line.biz/ja/) にアクセス
2. LINE アカウントでログイン
3. 初回の場合は開発者登録を完了

### 1.2 プロバイダーの作成

1. 「プロバイダー」タブをクリック
2. 「作成」ボタンをクリック
3. プロバイダー名を入力（例：`My Bot Provider`）
4. 「作成」をクリック

## 🤖 2. LINE Bot チャンネルの作成

### 2.1 新しいチャンネルの作成

1. 作成したプロバイダーをクリック
2. 「Messaging API」をクリック
3. 必要情報を入力：
   - **チャンネル名**: `Python Bot Template`
   - **チャンネル説明**: `高性能Python Bot テンプレート`
   - **大業種・小業種**: 適切なカテゴリを選択
   - **メールアドレス**: 連絡先メールアドレス
4. 各種規約に同意してチャンネルを作成

### 2.2 チャンネル設定の確認

作成したチャンネルをクリックし、「チャンネル基本設定」タブで以下を確認：
- **チャンネル ID**: 後で使用（メモ推奨）
- **チャンネルシークレット**: 後で環境変数として設定

## 🔑 3. 認証情報の取得

### 3.1 チャンネルアクセストークンの発行

1. 「Messaging API」タブを開く
2. 「チャンネルアクセストークン」セクションで「発行」をクリック
3. 有効期限を設定（推奨：無期限 - 本番環境では適切な期限を設定）
4. **重要**: 生成されたトークンをすぐにコピーして安全な場所に保存
   - このトークンは再表示できないため注意

### 3.2 Webhook 設定

1. 「Messaging API」タブの「Webhook 設定」で：
   - **Webhook URL**: 後で設定（一時的に `https://example.com/callback` でOK）
   - **Webhook の利用**: 一旦オフのままでOK

### 3.3 応答設定（重要）

1. 「Messaging API」タブの「LINE 公式アカウント機能」で：
   - **応答メッセージ**: **オフにする**（重要：これをしないとBotが二重応答する）
   - **あいさつメッセージ**: お好みで設定
   - **Webhook**: 後でオンにする

## 💻 4. ローカル環境のセットアップ

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

#### Unix/Linux/macOS の場合
```bash
export CHANNEL_ACCESS_TOKEN="your-channel-access-token-here"
export CHANNEL_SECRET="your-channel-secret-here"
```

#### Windows の場合
```cmd
set CHANNEL_ACCESS_TOKEN=your-channel-access-token-here
set CHANNEL_SECRET=your-channel-secret-here
```

#### .env ファイルを使用する場合（推奨）
```bash
# .env ファイルを作成
cat > .env << EOF
CHANNEL_ACCESS_TOKEN=your-channel-access-token-here
CHANNEL_SECRET=your-channel-secret-here
EOF
```

**注意**: `.env` ファイルは `.gitignore` に含まれていることを確認してください。

### 4.3 ngrok のセットアップ（開発用）

ローカル開発では、LINE からの Webhook を受信するため外部からアクセス可能な URL が必要です。

#### ngrok のインストール

```bash
# macOS (Homebrew)
brew install ngrok

# Windows (Chocolatey)
choco install ngrok

# Ubuntu/Debian
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
sudo apt update && sudo apt install ngrok

# 手動インストール（全OS対応）
# https://ngrok.com/download からダウンロードして PATH に配置
```

#### 認証トークンの設定

1. [ngrok](https://ngrok.com) でアカウントを作成（無料）
2. [ダッシュボード](https://dashboard.ngrok.com/get-started/your-authtoken) で auth token を取得
3. 認証トークンを設定：

```bash
ngrok config add-authtoken YOUR_AUTH_TOKEN_HERE
```

## 🚀 5. Bot の起動と動作確認

### 5.1 アプリケーションの起動

**ターミナル 1: LINE Bot アプリケーション起動**

```bash
cd linebot-template-python

# 環境変数が設定されていることを確認
echo $CHANNEL_ACCESS_TOKEN
echo $CHANNEL_SECRET

# アプリケーション起動
python app.py
```

起動成功時の表示例：
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

**ターミナル 2: ngrok でトンネル作成**

```bash
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

**重要**: `https://abc123def456.ngrok-free.app` の部分をコピーしてください。

### 5.2 Webhook URL の設定

1. LINE Developers コンソールに戻る
2. 「Messaging API」タブの「Webhook 設定」セクション
3. **Webhook URL** に ngrok の HTTPS URL + `/callback` を入力
   - 例：`https://abc123def456.ngrok-free.app/callback`
4. **「検証」ボタンをクリック**して接続確認
   - 成功時：✅ 成功
   - 失敗時：アプリケーションとngrokが起動しているか確認
5. 接続成功後、**「Webhook の利用」をオンにする**
6. **「更新」をクリック**

### 5.3 Bot の動作テスト

1. LINE Developers コンソールの「Messaging API」タブで **QR コード** を表示
2. **スマートフォンの LINE アプリ** で QR コードを読み取り、Bot を友だち追加
3. Bot に以下のメッセージを送信してテスト：

#### 基本テスト
- `こんにちは` → 挨拶メッセージが返ってくる
- `ありがとう` → 感謝に対する返信が返ってくる
- `help` → Bot機能一覧が表示される

#### 高度なテスト
- `プロフィール` / `profile` → あなたのプロフィール情報が表示される
- 画像を送信 → 画像受信メッセージが返ってくる
- スタンプを送信 → スタンプに対する返信が返ってくる

### 5.4 ログ確認

アプリケーションのターミナルで以下のようなログが表示されることを確認：

```
INFO:app:Message received: text from U1234567890abcdef
INFO:app:Follow event: U1234567890abcdef
```

ngrok の Web Interface（`http://127.0.0.1:4040`）でリクエストの詳細も確認可能です。

## 🐛 6. トラブルシューティング

### よくある問題と解決方法

#### Webhook 接続エラー
**エラー**: LINE Developers コンソールで「検証」が失敗する

**解決方法**:
1. ngrok が起動しているか確認
2. アプリケーションが `http://0.0.0.0:8000` で起動しているか確認
3. Webhook URL が正確に入力されているか確認（`/callback` を含む）
4. HTTPS URL を使用しているか確認（HTTP不可）

#### 認証エラー
**エラー**: `署名検証失敗` または `Invalid signature`

**解決方法**:
1. `CHANNEL_SECRET` が正しく設定されているか確認
2. 環境変数に余計なスペースや改行がないか確認
3. トークンが正確にコピーされているか確認

#### メッセージが返ってこない
**症状**: Bot にメッセージを送っても応答がない

**解決方法**:
1. LINE 公式アカウント機能で「応答メッセージ」がオフになっているか確認
2. 「Webhook の利用」がオンになっているか確認
3. アプリケーションのログでエラーが出ていないか確認

#### ngrok セッション期限切れ
**エラー**: しばらく使っていると Bot が応答しなくなる

**解決方法**:
1. ngrok を再起動
2. 新しい URL を Webhook URL に再設定
3. 有料版の利用を検討（固定ドメイン使用可能）

### 詳細ログでのデバッグ

```bash
# より詳細なログで起動
uvicorn app:app --reload --host 0.0.0.0 --port 8000 --log-level debug
```

### 環境変数の確認

```bash
# 環境変数が正しく設定されているか確認
python -c "import os; print('CHANNEL_SECRET:', bool(os.getenv('CHANNEL_SECRET'))); print('CHANNEL_ACCESS_TOKEN:', bool(os.getenv('CHANNEL_ACCESS_TOKEN')))"
```

## 📝 7. 次のステップ

基本的な動作確認が完了したら：

1. [📖 イベントハンドラガイド](./event-handlers.md) でイベント処理の詳細を学習
2. [🔧 カスタムハンドラ作成ガイド](./custom-handlers.md) で機能拡張
3. [🚀 デプロイメントガイド](./deployment.md) で本番環境への展開

## 🎉 完了

これで LINE Bot が正常に動作するはずです！何か問題が発生した場合は、ログを確認してトラブルシューティングセクションを参照してください。