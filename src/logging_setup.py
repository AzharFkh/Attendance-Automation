from __future__ import annotations

import logging
from pathlib import Path


def setup_logging(logs_dir: Path, filename: str = "presensi.log") -> None:
    """Configure console and file logging."""
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_path = logs_dir / filename

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_path, encoding="utf-8"),
        ],
    )
