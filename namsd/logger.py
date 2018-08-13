import os
import logging
from logging import FileHandler
from logging.handlers import TimedRotatingFileHandler

from config import config
from defs import get_log_dir


def create_rotate_logger(name, level, filename):
    _logger = logging.getLogger(name)
    _logger.setLevel(level)

    handler = TimedRotatingFileHandler(
        os.path.join(config['log_dir'], filename), when="midnight")
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    _logger.addHandler(handler)

    return _logger


def create_file_logger(name, level, timestamp, filename):
    _logger = logging.getLogger(name)
    _logger.setLevel(level)

    handler = FileHandler(os.path.join(get_log_dir(timestamp), filename))
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    _logger.addHandler(handler)

    return _logger
