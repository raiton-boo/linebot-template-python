import os

# 親ディレクトリのパスを取得
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

# データディレクトリのパスを取得
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
# ログデータのパスを取得
LOG_DIR = os.path.join(DATA_DIR, "logs")
