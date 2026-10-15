"""命令行入口：``gitlog-stats [PATH]``。"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import date, datetime
from typing import List, Optional

from . import __version__
from .parser import PRETTY_FORMAT, Commit, parse_log
from .stats import Report, build_report


class CliError(RuntimeError):
    """用户自己能修的问题：路径不对、没装 git、参数写错。"""


def run_git_log(repo: str) -> str:
    """向 git 要一份 :func:`parse_log` 能吃的日志。"""
    cmd = ["git", "-C", repo, "log", PRETTY_FORMAT, "--date=iso"]
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except FileNotFoundError as exc:  # git missing from PATH
        raise CliError(
            "git executable not found. Install Git and reopen your terminal, "
            "or pass --file examples/sample_gitlog.txt to run on a saved log."
        ) from exc
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout).strip().splitlines()
        raise CliError(detail[-1] if detail else "git log failed")
    return proc.stdout


def read_log(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as handle:
            return handle.read()
    except OSError as exc:
        raise CliError(f"cannot read {path}: {exc}") from exc


def bar(value: int, maximum: int, width: int) -> str:
    """Proportional bar using partial block glyphs."""
    if value <= 0 or maximum <= 0 or width <= 0:
        return ""
    cells = value / maximum * width
    full = int(cells)
    text = "█" * full
    if full < width and cells - full >= 0.5:
        text += "▌"
    return text or "▏"


def render(report: Report, title: str, width: int = 22, chart: bool = True) -> str:
    lines: List[str] = []
    span = (
        f"{report.first} -> {report.last}" if report.first and report.last else "no commits"
    )
    lines.append(f"repo    : {title}")
    lines.append(
        f"commits : {report.total}   authors: {report.author_count or len(report.authors)}   "
        f"range: {span}   active days: {report.active_days}   "
        f"longest streak: {report.longest_streak}d"
    )
    if report.total == 0:
        lines.append("")
        lines.append("no commits matched the filters")
        return "\n".join(lines)

    lines.append("")
    lines.append("top authors")
    ceiling = max(a.commits for a in report.authors)
    for index, author in enumerate(report.authors, 1):
        graph = bar(author.commits, ceiling, width) if chart else ""
        lines.append(
            f"  {index:>2}. {author.name[:24]:<24} {author.commits:>5}  "
            f"{author.share * 100:>5.1f}%  {graph}"
        )

    if chart and report.by_month:
        lines.append("")
        lines.append("commits by month")
        top_month = max(count for _, count in report.by_month)
        for month, count in report.by_month:
            lines.append(f"  {month}  {bar(count, top_month, width)} {count}")

    if chart and report.by_hour:
        lines.append("")
        lines.append("commits by hour")
        top_hour = max(report.by_hour.values())
        peak = max(report.by_hour, key=lambda hour: (report.by_hour[hour], -hour))
        for hour in sorted(report.by_hour):
            count = report.by_hour[hour]
            lines.append(f"  {hour:>2}h {bar(count, top_hour, 12):<13}{count}")
        lines.append(f"  peak hour: {peak:02d}:00")

    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gitlog-stats",
        description="Turn a git history into a readable activity report. No dependencies.",
        epilog="Examples:\n"
        "  gitlog-stats\n"
        "  gitlog-stats --repo C:/dev/my-project --since 2026-01-01\n"
        "  gitlog-stats --file examples/sample_gitlog.txt --json",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="path to the git repository (default: current directory)",
    )
    parser.add_argument("--repo", metavar="PATH", help="same as the positional path")
    parser.add_argument(
        "--file", metavar="LOG", help="read a saved git log instead of running git"
    )
    parser.add_argument(
        "--since", metavar="YYYY-MM-DD", help="only count commits on/after this date"
    )
    parser.add_argument(
        "--top", type=int, default=5, metavar="N", help="authors to show (default: 5)"
    )
    parser.add_argument(
        "--width", type=int, default=22, metavar="N", help="bar width (default: 22)"
    )
    parser.add_argument("--json", action="store_true", help="emit JSON instead of text")
    parser.add_argument("--no-chart", action="store_true", help="skip the bar charts")
    parser.add_argument("--version", action="version", version=f"gitlog-stats {__version__}")
    return parser


def parse_since(raw: Optional[str]) -> Optional[date]:
    if not raw:
        return None
    try:
        return datetime.strptime(raw, "%Y-%m-%d").date()
    except ValueError as exc:
        raise CliError(f"--since expects YYYY-MM-DD, got {raw!r}") from exc


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        since = parse_since(args.since)
        if args.file:
            title = args.file
            raw = read_log(args.file)
        else:
            title = args.repo or args.path
            raw = run_git_log(title)
        commits: List[Commit] = parse_log(raw)
        report = build_report(commits, top=args.top, since=since)
    except CliError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.json:
        payload = {"ok": True, "repo": title, "report": report.as_dict()}
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(render(report, title, width=args.width, chart=not args.no_chart))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
