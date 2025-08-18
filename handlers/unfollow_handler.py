"""
アンフォローイベントハンドラ
ユーザーがボットのフォローを解除した際の処理を担当
"""

from linebot.v3.webhooks import UnfollowEvent

from .base_handler import BaseEventHandler


class UnfollowEventHandler(BaseEventHandler):
    """
    アンフォローイベントを処理するハンドラ

    ユーザーがボットのフォローを解除した際の処理を行います。
    アンフォロー時は返信ができないため、ログ出力のみ行います。
    """

    async def handle(self, event: UnfollowEvent) -> None:
        """
        アンフォローイベントを処理

        Args:
            event (UnfollowEvent): アンフォローイベント
        """
        try:
            user_id = (
                event.source.user_id if hasattr(event.source, "user_id") else "unknown"
            )
            self.logger.info(f"ユーザーがアンフォローしました: {user_id}")

            # アンフォローの場合は返信できないため、ログ出力のみ
            # 必要に応じて内部処理（データベース更新など）を行う

        except Exception as e:
            await self.handle_error(e, event)
