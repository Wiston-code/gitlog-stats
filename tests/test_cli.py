"""End-to-end CLI tests: exit codes, text output, JSON output."""

from __future__ import annotations

import io
import json
import pathlib
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from gitlog_stats.cli import main  # noqa: E402
from gitlog_stats.parser import FIELD_SEP  # noqa: E402

RECORD_SEP = "\x1e"


def make_log(tmpdir):
    rows = [
        ("a1", "Wiston", "w@example.com", "2026-01-02 09:15:00 +0800", "feat: init"),
        ("b2", "Ada", "ada@example.com", "2026-01-03 14:20:11 +0800", "fix: edge case"),
        ("c3", "Wiston", "w@example.com", "2026-02-10 23:05:00 +0800", "docs: readme"),
    ]
    text = "".join(FIELD_SEP.join(row) + RECORD_SEP for row in rows)
    path = pathlib.Path(tmpdir) / "sample.log"
    path.write_text(text, encoding="utf-8")
    return str(path)


class CliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.log = make_log(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def run_cli(self, argv):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = main(argv)
        return code, out.getvalue(), err.getvalue()

    def test_text_output(self):
        code, out, _ = self.run_cli(["--file", self.log])
        self.assertEqual(code, 0)
        self.assertIn("commits : 3", out)
        self.assertIn("top authors", out)
        self.assertIn("Wiston", out)

    def test_json_output(self):
        code, out, _ = self.run_cli(["--file", self.log, "--json"])
        self.assertEqual(code, 0)
        payload = json.loads(out)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["report"]["total"], 3)
        self.assertEqual(payload["report"]["authors"][0]["name"], "Wiston")

    def test_since_filter(self):
        code, out, _ = self.run_cli(["--file", self.log, "--since", "2026-02-01", "--json"])
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out)["report"]["total"], 1)

    def test_bad_date_returns_2(self):
        code, _, err = self.run_cli(["--file", self.log, "--since", "02/01/2026"])
        self.assertEqual(code, 2)
        self.assertIn("YYYY-MM-DD", err)

    def test_missing_file_returns_2(self):
        code, _, err = self.run_cli(["--file", str(pathlib.Path(self.tmp.name) / "nope.log")])
        self.assertEqual(code, 2)
        self.assertIn("cannot read", err)

    def test_no_chart_flag(self):
        code, out, _ = self.run_cli(["--file", self.log, "--no-chart"])
        self.assertEqual(code, 0)
        self.assertNotIn("commits by month", out)


if __name__ == "__main__":
    unittest.main()
