import logging
import os

from ..config import CONFIG


def setup_logging(name: str, logfile: str = CONFIG['llm_driver']) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(CONFIG['log_level'])

    # Create a formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Create a file handler
    log_file = os.path.join(current_dir, '..', '..', 'logs', f'{logfile}.log')

    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(CONFIG['log_level'])
    file_handler.setFormatter(formatter)

    # Create a console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(CONFIG['log_level'])
    console_handler.setFormatter(formatter)

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # Increase the maximum log message size
    logger.maxBytes = 10 * 1024 * 1024  # 10 MB
    logger.backupCount = 5  # Keep 5 backup copies

    return logger
