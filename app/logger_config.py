import logging
from logging.handlers import RotatingFileHandler
import os

LOG_DIR = 'logs'

LOG_FILE = 'app.log'
LOG_PATH = os.path.join(LOG_DIR, LOG_FILE)

os.makedirs(LOG_DIR, exist_ok=True)

class ColorFormatter(logging.Formatter):
    COLORS = {
        'WARNING': '\033[93m',
        'ERROR': '\033[91m',
        'CRITICAL': '\033[91m', 
        'INFO': '\033[92m', 
        'DEBUG': '\033[94m', 
        'RESET': '\033[0m', 
    }

    def format(self, record):
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        message = super().format(record)
        return f'{color}{message}{self.COLORS["RESET"]}'

logger = logging.getLogger('api_logger')
logger.setLevel(logging.INFO)

log_format = '%(levelname)-8s | %(asctime)s | %(name)s | %(message)s'
date_format = '%d.%m.%Y %H:%M:%S'
formatter = logging.Formatter(fmt=log_format, datefmt=date_format)
color_formatter = ColorFormatter(fmt=log_format, datefmt=date_format)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(color_formatter)

file_handler = RotatingFileHandler(
        filename=LOG_PATH,
        maxBytes=1 * 1024 * 1024,
        backupCount=5,
        encoding='utf-8'
    )
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)


if not logger.handlers:
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)