from __future__ import annotations

import unittest
from datetime import date
from pathlib import Path

from src.data_loader import format_indonesian_date, is_workday, load_attendance_for_date

DATA_FILE = Path(__file__).resolve().parent.parent / "data_presensi_maganghub.json"


class TestDataLoader(unittest.TestCase):
    def test_format_indonesian_date(self) -> None:
        self.assertEqual(format_indonesian_date(date(2026, 11, 27)), "Jumat, 27 November 2026")
        self.assertEqual(format_indonesian_date(date(2026, 12, 1)), "Selasa, 1 Desember 2026")

    def test_is_workday(self) -> None:
        self.assertTrue(is_workday(date(2026, 11, 27)))   # Jumat
        self.assertFalse(is_workday(date(2026, 11, 28)))  # Sabtu
        self.assertFalse(is_workday(date(2026, 11, 29)))  # Minggu
        self.assertTrue(is_workday(date(2026, 11, 30)))   # Senin

    def test_load_all_planned_workdays_from_json(self) -> None:
        expected_dates = [
            date(2026, 11, 27),
            date(2026, 11, 30),
            date(2026, 12, 1),
            date(2026, 12, 2),
            date(2026, 12, 3),
            date(2026, 12, 4),
            date(2026, 12, 7),
            date(2026, 12, 8),
            date(2026, 12, 9),
            date(2026, 12, 10),
        ]
        for target in expected_dates:
            entry = load_attendance_for_date(DATA_FILE, target)
            self.assertIsNotNone(entry, f"Data hilang untuk {target}")
            assert entry is not None
            self.assertTrue(entry.uraian_aktivitas)
            self.assertTrue(entry.pembelajaran_diperoleh)
            self.assertTrue(entry.kendala_dialami)

    def test_missing_date_returns_none(self) -> None:
        self.assertIsNone(load_attendance_for_date(DATA_FILE, date(2026, 11, 28)))


if __name__ == "__main__":
    unittest.main()
