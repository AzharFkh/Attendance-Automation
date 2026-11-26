from __future__ import annotations

import logging
import time
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

logger = logging.getLogger(__name__)


def cleanup_old_logs(logs_dir: Path, retention_days: int = 4) -> int:
    """Delete log and screenshot files in logs_dir older than retention_days."""
    if retention_days < 0 or not logs_dir.exists():
        return 0

    cutoff = time.time() - (retention_days * 86400)
    removed = 0
    for path in logs_dir.rglob("*"):
        if not path.is_file():
            continue
        try:
            if path.stat().st_mtime < cutoff:
                path.unlink()
                removed += 1
        except OSError as exc:
            logger.warning("Gagal menghapus log lama %s: %s", path, exc)

    if removed:
        logger.info("Membersihkan %d file log/screenshot yang lebih lama dari %d hari.", removed, retention_days)
    return removed


def setup_logging(logs_dir: Path, filename: str = "presensi.log", retention_days: int = 4) -> None:
    """Configure console + daily rotating file logging and prune old log files."""
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_path = logs_dir / filename

    file_handler = TimedRotatingFileHandler(
        log_path,
        when="midnight",
        interval=1,
        backupCount=max(retention_days, 1),
        encoding="utf-8",
    )

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(),
            file_handler,
        ],
    )
    cleanup_old_logs(logs_dir, retention_days=retention_days)
