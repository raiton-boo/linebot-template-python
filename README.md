# linebot-template-python

## 🚀 このリポジトリについて
このリポジトリはライブラリじゃないです！  
「これを参考にして、自分のLINE BOTを作ってみてね」というテンプレです👾

まずはこのリポジトリをクローンして、好きなようにカスタムして使ってください！

```bash
git clone https://github.com/raiton-boo/linebot-template-python.git
cd linebot-template-python
```

## 📦 セットアップ方法
1. 必要なパッケージをインストール
```bash
pip install -r requirements.txt
```

2. `.env` を作成して、以下の内容を記述
```plaintext
LINE_CHANNEL_SECRET=あなたのチャンネルシークレット
LINE_CHANNEL_ACCESS_TOKEN=あなたのアクセストークン
```

3. サーバー起動（FastAPIの場合）
```bash
uvicorn app:app --reload
```

## 🗂 ファイル・フォルダ構成

| パス | 説明 |
|:---|:---|
| `app.py` | アプリのメインエントリーポイント。Webhook受信して、イベントを各ハンドラーに流す役割。 |
| `commands/` | コマンド関連をまとめるフォルダ。コマンドの管理・実行を行う。 |
| `handlers/` | LINEイベント（メッセージ受信、友達追加、グループ参加など）の処理をまとめるフォルダ。 |

## 🛠 使用技術
- Python 3.12
- FastAPI
- line-bot-sdk-python

## ✨ ライセンス
MIT License