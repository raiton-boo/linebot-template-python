

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
| `commands/` | コマンド関連をまとめるフォルダ。カスタムコマンドの追加が超楽になる設計。 |
| ├─ `command_manager.py` | 登録されたコマンドを管理して、実行をコントロールするクラス。 |
| ├─ `command/` | 実際のコマンド（例：`echo`, `ping`）を個別に定義してるフォルダ。 |
| `handlers/` | LINEイベント（メッセージ受信、友達追加、グループ参加など）の処理をまとめるフォルダ。 |
| ├─ `follow_event.py` | フォローイベント（友だち追加されたとき）の処理。 |
| ├─ `join_event.py` | グループやトークルームに追加されたときの処理。 |
| ├─ `message_event.py` | メッセージ受信時の処理。 |
| `logs/` | ログ関連をまとめたフォルダ。デバッグや運用監視にも対応できる設計。 |
| ├─ `log.py` | ロギング処理を一元化している。 |
| ├─ `data/debug.csv` | デバッグログ保存用CSV。 |
| ├─ `data/info.csv` | 通常ログ保存用CSV。 |
| `README.md` | このリポジトリの使い方説明ファイル。 |
| `requirements.txt` | 必要なPythonライブラリをまとめたファイル。 |

※`__pycache__`はPythonが自動で作るキャッシュファイルなので、気にしなくてOK！

## 🛠 使用技術
- Python 3.12
- FastAPI
- line-bot-sdk-python

## ✨ ライセンス
MIT License