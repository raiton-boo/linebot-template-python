"""
基底ハンドラクラス
すべてのイベントハンドラの基底となるクラス
"""

import logging
from abc import ABC, abstractmethod
from typing import Any

from linebot.v3.messaging import AsyncMessagingApi

logger = logging.getLogger(__name__)


class BaseEventHandler(ABC):
    """
    イベントハンドラの基底クラス

    すべてのハンドラはこのクラスを継承し、handle メソッドを実装する必要があります。
    """

    def __init__(self, line_bot_api: AsyncMessagingApi) -> None:
        """
        ハンドラを初期化

        Args:
            line_bot_api (AsyncMessagingApi): LINE Bot API クライアント
        """
        self.line_bot_api = line_bot_api
        self.logger = logger.getChild(self.__class__.__name__)

    @abstractmethod
    async def handle(self, event: Any) -> None:
        """
        イベントを処理する抽象メソッド

        Args:
            event (Any): 処理対象のイベント
        """
        pass
