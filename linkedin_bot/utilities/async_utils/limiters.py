import asyncio
import time
from asyncio import Condition

from linkedin_bot.config import main_logger
from linkedin_bot.utilities.utils import log_writer


class TokenLimiter:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.max_capacity = capacity
        self.condition: Condition = Condition()
        self.counter: int = 0

    async def spend_tokens(self, tokens):
        async with self.condition:
            while self.capacity < tokens:
                log_writer(main_logger, 55, f'Tokens limit is reached {self.counter}')
                await self.condition.wait()
            self.capacity -= tokens

    async def refill_loop(self):
        while True:
            current_time = time.localtime().tm_sec
            await asyncio.sleep(60 - current_time)
            async with self.condition:
                self.capacity = self.max_capacity
                self.condition.notify_all()
                log_writer(main_logger, 55, f'Tokens limit is refilled {self.counter}.')
