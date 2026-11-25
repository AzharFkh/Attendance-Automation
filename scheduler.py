from __future__ import annotations

import logging
import signal
import sys
from zoneinfo import ZoneInfo

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from src.config import AppConfig
from src.data_loader import is_workday, today_in_timezone
from src.logging_setup import setup_logging
from src.presensi_bot import run_attendance

logger = logging.getLogger(__name__)


def scheduled_job() -> None:
    config = AppConfig.from_env()
    target_date = today_in_timezone(config.timezone)
    if not is_workday(target_date):
        logger.info("Hari libur akhir pekan (%s), job dilewati.", target_date.isoformat())
        return

    logger.info("Memulai jadwal presensi harian untuk %s...", target_date.isoformat())
    run_attendance(config, target_date=target_date)


def main() -> None:
    config = AppConfig.from_env()
    setup_logging(config.logs_dir, filename="scheduler.log")

    tz = ZoneInfo(config.timezone)
    scheduler = BlockingScheduler(timezone=tz)
    trigger = CronTrigger(
        day_of_week="mon-fri",
        hour=config.schedule_hour,
        minute=config.schedule_minute,
        timezone=tz,
    )
    scheduler.add_job(
        scheduled_job,
        trigger=trigger,
        id="maganghub_presensi",
        max_instances=1,
        coalesce=True,
        misfire_grace_time=1800,
    )

    def _shutdown(signum, _frame) -> None:
        logger.info("Menerima sinyal %s, menghentikan scheduler...", signum)
        scheduler.shutdown(wait=False)
        sys.exit(0)

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    logger.info(
        "Scheduler aktif: Senin-Jumat pukul %02d:%02d (%s). DRY_RUN=%s",
        config.schedule_hour,
        config.schedule_minute,
        config.timezone,
        config.dry_run,
    )
    scheduler.start()


if __name__ == "__main__":
    main()
