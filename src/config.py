from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv


def _parse_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _parse_optional_int(value: str | None) -> int | None:
    if not value or not value.strip():
        return None
    return int(value.strip())


@dataclass(frozen=True)
class AppConfig:
    """Application configuration loaded from environment variables."""

    kemnaker_email: str
    kemnaker_password: str
    base_url: str
    data_file: Path
    chrome_profile_dir: Path
    logs_dir: Path
    screenshots_dir: Path
    headless: bool
    dry_run: bool
    chrome_version_main: int | None
    timezone: str
    schedule_hour: int
    schedule_minute: int

    @classmethod
    def from_env(cls, env_path: Path | None = None, dry_run_override: bool | None = None) -> "AppConfig":
        project_root = Path(__file__).resolve().parent.parent
        load_dotenv(dotenv_path=env_path or (project_root / ".env"))

        data_file_raw = os.getenv("DATA_FILE", "data_presensi_maganghub.json")
        profile_raw = os.getenv("CHROME_PROFILE_DIR", "./chrome_profile")
        logs_dir = project_root / "logs"
        screenshots_dir = logs_dir / "screenshots"

        dry_run = _parse_bool(os.getenv("DRY_RUN"), default=True)
        if dry_run_override is not None:
            dry_run = dry_run_override

        return cls(
            kemnaker_email=os.getenv("KEMNAKER_EMAIL", "").strip(),
            kemnaker_password=os.getenv("KEMNAKER_PASSWORD", "").strip(),
            base_url=os.getenv("BASE_URL", "https://monev.maganghub.kemnaker.go.id/dashboard/riwayat").rstrip("/"),
            data_file=(project_root / data_file_raw).resolve()
            if not Path(data_file_raw).is_absolute()
            else Path(data_file_raw),
            chrome_profile_dir=(project_root / profile_raw).resolve()
            if not Path(profile_raw).is_absolute()
            else Path(profile_raw),
            logs_dir=logs_dir,
            screenshots_dir=screenshots_dir,
            headless=_parse_bool(os.getenv("HEADLESS"), default=True),
            dry_run=dry_run,
            chrome_version_main=_parse_optional_int(os.getenv("CHROME_VERSION_MAIN")),
            timezone=os.getenv("TIMEZONE", "Asia/Jakarta").strip(),
            schedule_hour=int(os.getenv("SCHEDULE_HOUR", "15")),
            schedule_minute=int(os.getenv("SCHEDULE_MINUTE", "0")),
        )

    def validate_credentials(self) -> None:
        if not self.kemnaker_email or not self.kemnaker_password:
            raise ValueError(
                "KEMNAKER_EMAIL dan KEMNAKER_PASSWORD wajib diisi pada file .env."
            )
