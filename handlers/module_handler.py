# handlers/module_handler.py
from typing import Any, Dict, Optional

from linebot.v3.webhooks import ModuleEvent
from linebot.v3.messaging import AsyncMessagingApi

from .base_handler import BaseEventHandler


class ModuleEventHandler(BaseEventHandler):
    """
    ModuleEvent handler

    モジュールチャンネルがLINE Official Accountにアタッチされた際のイベントを処理します。
    """

    async def handle(self, event: ModuleEvent) -> None:
        """
        Process module event

        Args:
            event (ModuleEvent): Module event

        Raises:
            Exception: Error occurred during event processing
        """
        try:
            module_type = (
                event.module.type
                if event.module and hasattr(event.module, "type")
                else None
            )

            self.logger.info(f"Module event received: type={module_type}")

            # モジュールイベントに応じた処理を実装
            # 例: Moduleの attach/detach 状態の管理、設定の更新など

        except Exception as error:
            await self._error_handle(
                error,
                event,
                context={
                    "module_type": module_type if "module_type" in locals() else None
                },
            )
            raise

    async def _error_handle(
        self,
        error: Exception,
        event: ModuleEvent,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Handle error

        Args:
            error (Exception): Occurred error
            event (ModuleEvent): Event where error occurred
            context (Optional[Dict[str, Any]]): Context information when error occurred
        """
        try:
            self.logger.error(
                f"Error handling module event: {type(error).__name__} - {str(error)}",
                exc_info=True,
            )
        except Exception:
            # 絶対に例外を投げてはいけません
            pass
