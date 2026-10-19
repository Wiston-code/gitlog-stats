"""Parser tests. Run with: python -m unittest discover -s tests -v"""

from __future__ import annotations

import pathlib
import sys
import unittest
from datetime import datetime

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from gitlog_stats.parser import (  # noqa: E402
    FIELD_SEP,
    RECORD_SEP,
    parse_date,
    parse_log,
)


def record(sha, author, email, when, subject):
    return FIELD_SEP.join([sha, author, email, when, subject]) + RECORD_SEP


SAMPLE = (
    record("a1", "Wiston", "w@example.com", "2026-01-02 09:15:00 +0800", "feat: cli 骨架")
    + record("b2", "Ada", "ada@example.com", "2026-01-03 14:20:11 +0800", "fix: 边界条件")
    + record("c3", "Wiston", "w@example.com", "2026-02-10 23:05:00 +0800", "docs: README")
)


class ParseDateTests(unittest.TestCase):
    def test_iso_with_timezone(self):
        self.assertEqual(
            parse_date("2026-01-02 09:15:00 +0800"),
            datetime(2026, 1, 2, 9, 15, 0),
        )

    def test_iso_with_t_separator(self):
        self.assertEqual(parse_date("2026-03-04T05:06:07"), datetime(2026, 3, 4, 5, 6, 7))

    def test_rejects_garbage(self):
        with self.assertRaises(ValueError):
            parse_date("yesterday")


class ParseLogTests(unittest.TestCase):
    def test_counts_and_order(self):
        commits = parse_log(SAMPLE)
        self.assertEqual([c.sha for c in commits], ["a1", "b2", "c3"])
        self.assertEqual(commits[0].author, "Wiston")
        self.assertEqual(commits[1].email, "ada@example.com")

    def test_month_and_day_helpers(self):
        first = parse_log(SAMPLE)[0]
        self.assertEqual(first.month, "2026-01")
        self.assertEqual(first.day, "2026-01-02")

    def test_skips_truncated_and_bad_date_records(self):
        text = SAMPLE + "truncated" + RECORD_SEP
        text += record("d4", "Bob", "b@example.com", "not-a-date", "broken")
        self.assertEqual(len(parse_log(text)), 3)

    def test_empty_input(self):
        self.assertEqual(parse_log(""), [])

    def test_subject_containing_separator_is_glued_back(self):
        text = record("e5", "Wiston", "w@example.com", "2026-01-05 10:00:00 +0800", "a|b")
        text = text.replace("a|b", "a" + FIELD_SEP + "b")
        self.assertEqual(parse_log(text)[0].subject, "a" + FIELD_SEP + "b")


if __name__ == "__main__":
    unittest.main()
