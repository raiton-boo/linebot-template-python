import logging
import os
import csv
from datetime import datetime
from rich.console import Console
from rich.logging import RichHandler

class LogManager:
    def __init__(self, log_dir="logs/data"):
        # Richコンソールの設定
        self.console = Console()

        # ログデータ用ディレクトリを作成
        os.makedirs(log_dir, exist_ok=True)
        self.log_dir = log_dir

        # ログ設定
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(message)s",  # フォーマットはカスタムで出力
            handlers=[RichHandler(console=self.console, show_time=False, show_level=False, show_path=False)]
        )
        self.logger = logging.getLogger(__name__)

    def _write_to_csv(self, level: str, message: str):
        """ログをCSVファイルに書き込む"""
        log_file = os.path.join(self.log_dir, f"{level}.csv")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # ファイルが存在しない場合はテンプレートを作成
        if not os.path.exists(log_file):
            with open(log_file, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["timestamp", "level", "message"])  # ヘッダー行を追加

        # ログを書き込む
        with open(log_file, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([timestamp, level.upper(), message])

    def _log_to_console(self, level: str, message: str, color: str):
        """コンソールにカスタムフォーマットでログを出力"""
        timestamp = datetime.now().strftime("[%m/%d/%y %H:%M:%S]")  # 時間フォーマットを変更
        level_padded = level.upper().ljust(8)  # レベルを固定幅（8文字）に揃える
        self.console.print(f"{timestamp} | [{color}]{level_padded}[/] | {message}")

    def debug(self, message: str):
        self._log_to_console("debug", message, "cyan")  # 青色
        self._write_to_csv("debug", message)

    def info(self, message: str):
        self._log_to_console("info", message, "green")  # 緑色
        self._write_to_csv("info", message)

    def warning(self, message: str):
        self._log_to_console("warning", message, "yellow")  # 黄色
        self._write_to_csv("warning", message)

    def error(self, message: str):
        self._log_to_console("error", message, "red")  # 赤色
        self._write_to_csv("error", message)

    def critical(self, message: str):
        self._log_to_console("critical", message, "bold red")  # 太字赤色
        self._write_to_csv("critical", message)