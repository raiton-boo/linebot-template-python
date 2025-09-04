from .help_command import HelpCommand
from .ping_command import PingCommand
from .loading_command import LoadingCommand
from .mention_command import MentionCommand
from .postback_command import PostbackCommand
from .police_command import PoliceCommand

# 利用可能なコマンドを定義
AVAILABLE_COMMANDS = {
    "/help": HelpCommand,
    "/ping": PingCommand,
    "/test": PingCommand,
    "/loading": LoadingCommand,
    "/mention": MentionCommand,
    "/allmention": MentionCommand,  # 同じクラスで処理
    "/postback": PostbackCommand,
    "/police": PoliceCommand,
}

# コマンドのヘルプテキストを定義
COMMAND_HELP_TEXT = (
    "利用可能なコマンド:\n"
    "/help - ヘルプ表示\n"
    "/ping - 疎通確認\n"
    "/loading - ローディングアニメーション表示（個チャのみ）\n"
    "/mention - メンション機能テスト（グループチャットのみ）\n"
    "/allmention - 全員メンション機能テスト (グループチャットのみ・極力使わないように)\n"
    "/postback - Postback機能テスト（ボタン付きメッセージ）\n"
    "/police - 警察庁本部の位置情報を送信"
)