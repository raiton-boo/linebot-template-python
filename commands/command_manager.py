class CommandManager:
    """コマンドを管理するクラス"""

    # コマンドの登録情報を保持する辞書
    _commands = {}

    @classmethod
    def register_command(cls, name=None, aliases=None, description=None):
        """
        コマンドを登録するデコレータ
        :param name: コマンド名（省略時は関数名を使用）
        :param aliases: コマンドのエイリアス（別名）のリスト
        :param description: コマンドの説明
        """
        def decorator(func):
            command_name = name or func.__name__
            if command_name in cls._commands:
                raise ValueError(f"コマンド '{command_name}' は既に登録されています。")
            cls._commands[command_name] = {
                "aliases": aliases or [],
                "description": description or "",
                "func": func,
            }
            # エイリアスも同じコマンドとして登録
            for alias in aliases or []:
                if alias in cls._commands:
                    raise ValueError(f"エイリアス '{alias}' は既に登録されています。")
                cls._commands[alias] = cls._commands[command_name]
            return func
        return decorator

    @classmethod
    async def execute_command(cls, name: str, *args, **kwargs):
        """
        コマンドを実行する
        :param name: 実行するコマンド名またはエイリアス
        :param args: コマンドに渡す引数
        :param kwargs: コマンドに渡すキーワード引数
        :return: コマンドの実行結果
        """
        command = cls._commands.get(name)
        if not command:
            # コマンドが存在しない場合
            return None
        return await command["func"](*args, **kwargs)

    @classmethod
    def list_commands(cls) -> str:
        """
        登録されているコマンドの一覧を表示する
        :return: コマンド一覧の文字列
        """
        command_list = "\n".join(
            [
                f"{name} (エイリアス: {', '.join(command['aliases'])}) - {command['description']}"
                for name, command in cls._commands.items()
                if name == command["aliases"][0] or not command["aliases"]  # 重複を避ける
            ]
        )
        return f"登録されているコマンド:\n{command_list}" if command_list else "登録されているコマンドはありません。"