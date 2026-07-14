import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from app.config import settings

LOG_DIR = Path("logs")
LOG_FILE = LOG_DIR / "app.log"


def setup_logging() -> None:
    LOG_DIR.mkdir(exist_ok=True)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    file_handler = RotatingFileHandler(LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3)
    file_handler.setFormatter(formatter)

    logging.basicConfig(
        level=logging.DEBUG if settings.debug else logging.INFO,
        handlers=[console_handler, file_handler],
    )
