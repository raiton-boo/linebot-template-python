from utils.log.log import LogManager


class BaseMessageHandler:
    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api
        self.logger = LogManager()

    async def log_ignore(self, reason: str):
        await self.logger.info(f"無視した理由: {reason}")
