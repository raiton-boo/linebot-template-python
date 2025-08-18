# LINE Bot Template Python

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)
![LINE SDK](https://img.shields.io/badge/LINE%20SDK-v3-yellow.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

Python + FastAPI + LINE Messaging API v3 を使用したシンプルな LINE Bot テンプレートです。

## 🚀 特徴

- **モジュール設計**: イベントタイプごとのハンドラパターンで拡張しやすい構成
- **非同期処理**: FastAPI + asyncio による高速レスポンス
- **エラー分析**: `linebot-error-analyzer` による詳細なエラー解析とログ管理
- **プロフィール取得**: `profile` コマンドでユーザー情報を取得
- **オウム返し**: 基本的なメッセージエコー機能

## 📋 機能一覧

### イベントハンドリング

- ✅ **メッセージイベント**: テキストメッセージの受信・返信
- ✅ **フォローイベント**: ユーザーの友だち追加時の処理
- ✅ **アンフォローイベント**: ユーザーのブロック時の処理
- ✅ **参加/退室イベント**: グループ・ルームでの入退室処理

### 追加機能

- 🔍 **プロフィール取得**: `profile` と送信するとユーザー情報を表示
- 📊 **エラー分析**: LINE API エラーの詳細分析とユーザーフレンドリーなメッセージ
- ⚡ **パフォーマンス監視**: 処理時間とイベント数の軽量ログ

## 🛠 技術スタック

- **Python**: 3.9+
- **WebFramework**: FastAPI
- **LINE SDK**: linebot-v3-sdk
- **エラー分析**: linebot-error-analyzer
- **非同期処理**: asyncio
- **サーバー**: Uvicorn

## ⚡ クイックスタート

### 1. リポジトリをクローン

```bash
git clone <your-repo-url>
cd linebot-template-python
```

### 2. 依存関係をインストール

```bash
pip install -r requirements.txt
```

### 3. 環境変数を設定

```bash
cp .env.example .env
# .env ファイルを編集してLINE Bot の認証情報を入力
```

### 4. ローカル開発環境の起動

```bash
# アプリケーションを起動
python -m uvicorn app:app --reload --host 0.0.0.0 --port 8000

# 別のターミナルでngrokを起動（外部公開用）
ngrok http 8000
```

### 5. Webhook URL を設定

ngrok で表示された HTTPS URL を使用して LINE Developers Console で Webhook URL を設定  
詳細な手順は [セットアップガイド](./docs/setup.md) を参照

## 🔧 設定

### 必要な環境変数

| 変数名                 | 説明                                  | 必須 |
| ---------------------- | ------------------------------------- | ---- |
| `CHANNEL_ACCESS_TOKEN` | LINE Bot のチャンネルアクセストークン | ✅   |
| `CHANNEL_SECRET`       | LINE Bot のチャンネルシークレット     | ✅   |

## 📖 詳細ドキュメント

- [LINE Bot アカウント作成とセットアップ](./docs/setup.md)
- [本番環境デプロイメント](./docs/deployment.md)
- [カスタムハンドラの作成](./docs/custom-handlers.md)

## 🤝 使い方

### 基本的なメッセージ

- 任意のテキストを送信 → 鸚鵡返し
- `profile` と送信 → ユーザープロフィール情報を表示

### カスタマイズ

- `handlers/` ディレクトリ内の各ハンドラを編集して機能を追加
- 新しいコマンドは `message_handler.py` の `handle` メソッドに追加

## 🔍 ログとモニタリング

- エラーは `linebot-error-analyzer` で自動解析
- パフォーマンス情報（処理時間、イベント数）を軽量ログ
- ユーザーフレンドリーなエラーメッセージを自動生成

## 📄 ライセンス

MIT License - 詳細は [LICENSE](LICENSE) ファイルを参照

## 🙋‍♂️ サポート

質問や問題がある場合は [Issues](../../issues) でお気軽にお尋ねください。
