"""
グループ退出イベントハンドラ
ボットがグループから退出させられた際の処理を担当
"""

from linebot.v3.webhooks import LeaveEvent

from .base_handler import BaseEventHandler


class LeaveEventHandler(BaseEventHandler):
    """
    グループ退出イベントを処理するハンドラ

    ボットがグループから退出させられた際の処理を行います。
    退出時は返信ができないため、ログ出力のみ行います。
    """

    async def handle(self, event: LeaveEvent) -> None:
        """
        グループ退出イベントを処理

        Args:
            event (LeaveEvent): グループ退出イベント
        """
        try:
            group_id = getattr(event.source, "group_id", "unknown")
            self.logger.info(f"グループから退出しました: {group_id}")

            # グループ退出の場合は返信できないため、ログ出力のみ
            # 必要に応じて内部処理（データベース更新など）を行う

        except Exception as e:
            await self.handle_error(e, event)
