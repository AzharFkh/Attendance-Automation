from __future__ import annotations

import argparse
import logging
import sys
from datetime import date

from src.config import AppConfig
from src.data_loader import is_workday, today_in_timezone
from src.logging_setup import setup_logging
from src.presensi_bot import run_attendance

logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Automasi presensi harian MagangHub Kemnaker (stealth Selenium)."
    )
    parser.add_argument(
        "--run-now",
        action="store_true",
        help="Jalankan proses presensi sekarang juga.",
    )
    parser.add_argument(
        "--date",
        type=str,
        default=None,
        help="Tanggal target format YYYY-MM-DD (default: hari ini sesuai TIMEZONE).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Isi form & simpan screenshot tanpa menekan tombol submit.",
    )
    parser.add_argument(
        "--headed",
        action="store_true",
        help="Tampilkan jendela browser Chrome (HEADLESS=false) untuk pemantauan.",
    )
    parser.add_argument(
        "--step-delay",
        type=float,
        default=None,
        help="Jeda antar tahap dalam detik (contoh: 3 atau 5) untuk inspeksi manual.",
    )
    parser.add_argument(
        "--force-weekend",
        action="store_true",
        help="Tetap jalankan meskipun tanggal target adalah Sabtu/Minggu.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = AppConfig.from_env(
        dry_run_override=True if args.dry_run else None,
        headless_override=False if args.headed else None,
        step_delay_override=args.step_delay,
    )
    setup_logging(config.logs_dir, retention_days=config.log_retention_days)

    if not args.run_now:
        logger.info("Gunakan '--run-now' untuk eksekusi sekali atau jalankan 'scheduler.py'.")
        return 0

    target_date = date.fromisoformat(args.date) if args.date else today_in_timezone(config.timezone)
    if not args.force_weekend and not is_workday(target_date):
        logger.info("Tanggal %s adalah akhir pekan. Proses presensi dilewati.", target_date.isoformat())
        return 0

    success = run_attendance(config, target_date=target_date)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
