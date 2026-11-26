from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

logger = logging.getLogger(__name__)

INDONESIAN_DAYS = {
    0: "Senin",
    1: "Selasa",
    2: "Rabu",
    3: "Kamis",
    4: "Jumat",
    5: "Sabtu",
    6: "Minggu",
}

INDONESIAN_MONTHS = {
    1: "Januari",
    2: "Februari",
    3: "Maret",
    4: "April",
    5: "Mei",
    6: "Juni",
    7: "Juli",
    8: "Agustus",
    9: "September",
    10: "Oktober",
    11: "November",
    12: "Desember",
}

REQUIRED_FIELDS = (
    "uraian aktivitas",
    "pembelajaran yang diperoleh",
    "kendala yang dialami",
)


@dataclass(frozen=True)
class AttendanceEntry:
    """Single day's attendance form payload."""

    date_iso: str
    date_label: str
    uraian_aktivitas: str
    pembelajaran_diperoleh: str
    kendala_dialami: str


def format_indonesian_date(target_date: date) -> str:
    """Format a date into the JSON key format, e.g. 'Jumat, 27 November 2026'."""
    day_name = INDONESIAN_DAYS[target_date.weekday()]
    month_name = INDONESIAN_MONTHS[target_date.month]
    return f"{day_name}, {target_date.day} {month_name} {target_date.year}"


def today_in_timezone(tz_name: str = "Asia/Jakarta") -> date:
    """Return today's date in the configured timezone."""
    return datetime.now(ZoneInfo(tz_name)).date()


def is_workday(target_date: date) -> bool:
    """Return True for Monday-Friday."""
    return target_date.weekday() < 5


def load_attendance_for_date(data_file: Path, target_date: date) -> AttendanceEntry | None:
    """Load and validate attendance data for target_date, returning None if absent."""
    if not data_file.exists():
        raise FileNotFoundError(f"File data presensi tidak ditemukan: {data_file}")

    with data_file.open("r", encoding="utf-8") as fh:
        raw_data = json.load(fh)

    if not isinstance(raw_data, dict):
        raise ValueError("Format JSON harus berupa object dengan key tanggal Indonesia.")

    date_label = format_indonesian_date(target_date)
    entry = raw_data.get(date_label)
    if entry is None:
        return None

    if not isinstance(entry, dict):
        raise ValueError(f"Data untuk '{date_label}' harus berupa object.")

    if bool(entry.get("libur")) or bool(entry.get("skip")):
        note = str(entry.get("keterangan", "")).strip()
        logger.info(
            "Tanggal '%s' ditandai libur/skip di JSON%s.",
            date_label,
            f" ({note})" if note else "",
        )
        return None

    missing = [field for field in REQUIRED_FIELDS if not str(entry.get(field, "")).strip()]
    if missing:
        raise ValueError(
            f"Field wajib kosong/hilang untuk '{date_label}': {', '.join(missing)}"
        )

    return AttendanceEntry(
        date_iso=target_date.isoformat(),
        date_label=date_label,
        uraian_aktivitas=str(entry["uraian aktivitas"]).strip(),
        pembelajaran_diperoleh=str(entry["pembelajaran yang diperoleh"]).strip(),
        kendala_dialami=str(entry["kendala yang dialami"]).strip(),
    )
