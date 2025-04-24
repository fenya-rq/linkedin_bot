import atexit
import logging
import logging.config
import logging.handlers
import os
from pathlib import Path
from queue import Queue

from dotenv import load_dotenv

# Defined before constants because we need load secrets to system environment
load_dotenv()

DEBUG = os.getenv('DEBUG')
ROOT_DIR = Path(__file__).resolve().parent

LINKEDIN_NAME = os.getenv('LINKEDIN_NAME')
LINKEDIN_PASSWORD = os.getenv('LINKEDIN_PASSWORD')
LINKEDIN_LOGIN_URL = os.getenv('LINKEDIN_LOGIN_URL')

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'debug': {
            'format': '%(filename)s:%(lineno)d - %(funcName)s: '
                      '%(asctime)s - %(levelname)s - %(message)s'
        },
        'prod': {
            'format': '%(filename)s: %(asctime)s - %(levelname)s - %(message)s'
        },
    },

    'handlers': {
        'queue': {
            'class': 'logging.handlers.QueueHandler',
            'queue': Queue(-1),
        },
    },

    'loggers': {
        'main': {
            'handlers': ['queue'],
            'level': 'DEBUG',
            'propagate': False,
        }
    },
}

logging.config.dictConfig(LOGGING_CONFIG)

queue = LOGGING_CONFIG['handlers']['queue']['queue']  # type: ignore

file_logger = logging.FileHandler(
    Path(ROOT_DIR.parent, 'logs', 'manager.log'),
    mode='w', encoding='utf-8'
)
file_logger.setFormatter(logging.Formatter(LOGGING_CONFIG['formatters']['debug']['format']))  # type: ignore

# Create queue listener
listener = logging.handlers.QueueListener(
    queue, file_logger, respect_handler_level=True
)
listener.start()

# Ensure flush on shutdown
atexit.register(listener.stop)

main_logger = logging.getLogger('main')
