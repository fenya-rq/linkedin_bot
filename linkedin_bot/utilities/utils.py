import json
import re
from logging import Logger


def log_writer(logger: Logger, lvl: int, log: str) -> None:
    """
    Write a log message using the provided logger.

    :param logger: Logger instance to use
    :param lvl: Log level
    :param log: Log message
    """
    logger.log(lvl, log)


def clean_json(string: str, load: bool = False):
    json_data = re.search(r'```(?:json)?\s*(.*?)```', string, re.DOTALL | re.IGNORECASE)
    if not json_data:
        raise Exception('json is not found')

    if load:
        return json.loads(json_data.group(1))

    return json_data.group(1)


def dict_to_string(data: dict):
    post_to_add = data.get('post')
    return '\n'.join(f'{k}: {v}' for k, v in post_to_add.items())
