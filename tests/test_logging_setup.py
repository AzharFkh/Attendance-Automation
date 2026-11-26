from __future__ import annotations

import os
import tempfile
import time
import unittest
from pathlib import Path

from src.logging_setup import cleanup_old_logs


class TestLoggingCleanup(unittest.TestCase):
    def test_cleanup_removes_only_files_older_than_retention_days(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            logs_dir = Path(tmpdir)
            screenshots_dir = logs_dir / "screenshots"
            screenshots_dir.mkdir(parents=True)

            old_log = logs_dir / "old.log"
            old_shot = screenshots_dir / "old.png"
            recent_shot = screenshots_dir / "recent.png"

            for f in (old_log, old_shot, recent_shot):
                f.write_text("dummy", encoding="utf-8")

            now = time.time()
            five_days_ago = now - (5 * 86400)
            two_days_ago = now - (2 * 86400)

            os.utime(old_log, (five_days_ago, five_days_ago))
            os.utime(old_shot, (five_days_ago, five_days_ago))
            os.utime(recent_shot, (two_days_ago, two_days_ago))

            removed = cleanup_old_logs(logs_dir, retention_days=4)

            self.assertEqual(removed, 2)
            self.assertFalse(old_log.exists())
            self.assertFalse(old_shot.exists())
            self.assertTrue(recent_shot.exists())


if __name__ == "__main__":
    unittest.main()
