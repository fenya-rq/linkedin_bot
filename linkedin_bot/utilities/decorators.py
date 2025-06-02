import asyncio
import functools
from typing import Any, Callable

from linkedin_bot.config import main_logger
from linkedin_bot.utilities import CaptchaSolverError
from .utils import log_writer


def retry_on_failure(
    max_attempts: int = 3, delay: int = 5, exceptions: tuple = (CaptchaSolverError,)
) -> Callable:
    """A decorator that retries an async function on specified exceptions.

    :param max_attempts: Maximum number of retry attempts
    :param delay: Delay between retries in seconds
    :param exceptions: Tuple of exceptions to catch and retry on
    :return: Decorated function that implements retry logic
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            attempt = 1

            while attempt <= max_attempts:
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    if attempt < max_attempts:
                        log_writer(
                            main_logger,
                            30,
                            f'Attempt {attempt} failed. Retrying in {delay} seconds...',
                        )
                        await asyncio.sleep(delay)
                        attempt += 1
                    else:
                        log_writer(
                            main_logger,
                            40,
                            f'All {max_attempts} attempts failed. Last error: {str(e)}',
                        )
                        raise e

        return wrapper

    return decorator
