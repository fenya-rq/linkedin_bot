import logging
import logging.config
import os
from pathlib import Path

from dotenv import load_dotenv

# Defined before constants because we need load secrets to system environment
load_dotenv()

DEBUG = os.getenv('DEBUG')
ROOT_DIR = Path(__file__).resolve().parent

LINKEDIN_NAME = os.getenv('LINKEDIN_NAME')
LINKEDIN_PASSWORD = os.getenv('LINKEDIN_PASSWORD')
LOGIN_URL = os.getenv('LOGIN_URL')

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'debug': {
            'format': '%(filename)s:%(lineno)d - %(funcName)s: %(asctime)s - %(levelname)s - %(message)s',
        },
        'prod': {
            'format': '%(filename)s: %(asctime)s - %(levelname)s - %(message)s',
        },
    },
    'handlers': {
        'file_dbg': {
            'class': 'logging.FileHandler',
            'filename': Path(ROOT_DIR.parent, 'logs', 'parser_debug.log'),
            'mode': 'w+',
            'encoding': 'utf-8',
            'formatter': 'debug',
            'level': 'DEBUG',
        },
        'file_prd': {
            'class': 'logging.FileHandler',
            'filename': Path(ROOT_DIR.parent, 'logs', 'parser_prod.log'),
            'mode': 'w',
            'encoding': 'utf-8',
            'formatter': 'prod',
            'level': 'ERROR',
        },
    },
    'loggers': {
        'logger_dbg': {
            'handlers': ['file_dbg'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'logger_prd': {
            'handlers': ['file_prd'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}

logging.config.dictConfig(LOGGING_CONFIG)

logger_dbg = logging.getLogger('logger_dbg')
logger_prd = logging.getLogger('logger_prd')
