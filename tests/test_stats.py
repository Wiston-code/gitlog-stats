"""Aggregation tests."""

from __future__ import annotations

import pathlib
import sys
import unittest
from datetime import date, datetime

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from gitlog_stats.parser import Commit  # noqa: E402
from gitlog_stats.stats import (  # noqa: E402
    build_report,
    filter_since,
    longest_streak,
)


def commit(day, hour=10, author="Wiston", sha=None):
    year, month, dom = (int(x) for x in day.split("-"))
    return Commit(
        sha=sha or f"{day}{hour}",
        author=author,
        email="x@example.com",
        date=datetime(year, month, dom, hour, 0, 0),
        subject="test",
    )


class FilterTests(unittest.TestCase):
    def test_since_is_inclusive(self):
        commits = [commit("2026-01-01"), commit("2026-01-02"), commit("2026-01-03")]
        kept = filter_since(commits, date(2026, 1, 2))
        self.assertEqual([c.day for c in kept], ["2026-01-02", "2026-01-03"])

    def test_none_keeps_everything(self):
        commits = [commit("2026-01-01")]
        self.assertEqual(len(filter_since(commits, None)), 1)


class StreakTests(unittest.TestCase):
    def test_consecutive_days(self):
        days = [date(2026, 1, 1), date(2026, 1, 2), date(2026, 1, 3), date(2026, 1, 9)]
        self.assertEqual(longest_streak(days), 3)

    def test_duplicates_do_not_inflate(self):
        days = [date(2026, 1, 1)] * 5
        self.assertEqual(longest_streak(days), 1)

    def test_empty(self):
        self.assertEqual(longest_streak([]), 0)


class ReportTests(unittest.TestCase):
    def setUp(self):
        self.commits = [
            commit("2026-01-01", author="Wiston"),
            commit("2026-01-02", author="Wiston"),
            commit("2026-01-02", author="Ada", hour=23),
            commit("2026-02-01", author="Bob", hour=9),
        ]

    def test_totals_and_ranking(self):
        report = build_report(self.commits)
        self.assertEqual(report.total, 4)
        self.assertEqual(report.authors[0].name, "Wiston")
        self.assertEqual(report.authors[0].commits, 2)
        self.assertAlmostEqual(report.authors[0].share, 0.5)

    def test_top_limits_authors(self):
        report = build_report(self.commits, top=1)
        self.assertEqual(len(report.authors), 1)
        # 榜上只显示 1 人，但"总共几个作者"必须还是 3
        self.assertEqual(report.author_count, 3)

    def test_months_hours_and_span(self):
        report = build_report(self.commits)
        self.assertEqual(report.by_month, [("2026-01", 3), ("2026-02", 1)])
        self.assertEqual(report.by_hour[23], 1)
        self.assertEqual((report.first, report.last), (date(2026, 1, 1), date(2026, 2, 1)))
        self.assertEqual(report.active_days, 3)

    def test_since_filter_reduces_total(self):
        report = build_report(self.commits, since=date(2026, 2, 1))
        self.assertEqual(report.total, 1)

    def test_empty_report(self):
        report = build_report([])
        self.assertEqual(report.total, 0)
        self.assertEqual(report.authors, [])
        self.assertIsNone(report.first)

    def test_json_shape(self):
        payload = build_report(self.commits, top=2).as_dict()
        self.assertEqual(payload["total"], 4)
        self.assertEqual(len(payload["by_hour"]), 24)
        self.assertEqual(payload["first"], "2026-01-01")


if __name__ == "__main__":
    unittest.main()
