"""Logging setup: technical details go to app.log, never tracebacks to the user."""
from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging(log_dir: Path, level: int = logging.INFO) -> logging.Logger:
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "app.log"
    logger = logging.getLogger("beatgen")
    logger.setLevel(level)
    if not logger.handlers:
        fh = RotatingFileHandler(str(log_file), maxBytes=512_000, backupCount=3, encoding="utf-8")
        fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
        fh.setFormatter(fmt)
        logger.addHandler(fh)
        sh = logging.StreamHandler()
        sh.setFormatter(fmt)
        logger.addHandler(sh)
    return logger


def get_logger() -> logging.Logger:
    return logging.getLogger("beatgen")
