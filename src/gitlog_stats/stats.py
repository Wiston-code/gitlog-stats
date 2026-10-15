"""把 commit 列表算成报告里那些数字。"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from datetime import date
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from .parser import Commit


@dataclass
class AuthorStat:
    name: str
    commits: int
    share: float


@dataclass
class Report:
    total: int
    authors: List[AuthorStat]
    author_count: int = 0
    by_month: List[Tuple[str, int]] = field(default_factory=list)
    by_hour: Dict[int, int] = field(default_factory=dict)
    active_days: int = 0
    longest_streak: int = 0
    first: Optional[date] = None
    last: Optional[date] = None
    since: Optional[date] = None

    def as_dict(self) -> dict:
        return {
            "total": self.total,
            "author_count": self.author_count,
            "authors": [
                {"name": a.name, "commits": a.commits, "share": round(a.share, 4)}
                for a in self.authors
            ],
            "by_month": [{"month": m, "commits": c} for m, c in self.by_month],
            "by_hour": {str(h): self.by_hour.get(h, 0) for h in range(24)},
            "active_days": self.active_days,
            "longest_streak": self.longest_streak,
            "first": self.first.isoformat() if self.first else None,
            "last": self.last.isoformat() if self.last else None,
            "since": self.since.isoformat() if self.since else None,
        }


def filter_since(commits: Iterable[Commit], since: Optional[date]) -> List[Commit]:
    """留下 ``since`` 当天及之后的提交。"""
    if since is None:
        return list(commits)
    return [c for c in commits if c.date.date() >= since]


def longest_streak(days: Sequence[date]) -> int:
    """最长连续提交天数。"""
    if not days:
        return 0
    ordered = sorted(set(days))
    best = run = 1
    for prev, cur in zip(ordered, ordered[1:]):
        run = run + 1 if (cur - prev).days == 1 else 1
        best = max(best, run)
    return best


def build_report(
    commits: Iterable[Commit],
    top: Optional[int] = None,
    since: Optional[date] = None,
) -> Report:
    """生成报告；``top=None`` 表示作者不截断。"""
    kept = filter_since(commits, since)
    total = len(kept)
    if total == 0:
        return Report(total=0, authors=[], since=since)

    author_counts = Counter(c.author for c in kept)
    ranked = author_counts.most_common(top) if top else author_counts.most_common()
    authors = [
        AuthorStat(name=name, commits=count, share=count / total)
        for name, count in ranked
    ]

    months = Counter(c.month for c in kept)
    days = [c.date.date() for c in kept]

    return Report(
        total=total,
        authors=authors,
        author_count=len(author_counts),
        by_month=sorted(months.items()),
        by_hour=dict(Counter(c.date.hour for c in kept)),
        active_days=len(set(days)),
        longest_streak=longest_streak(days),
        first=min(days),
        last=max(days),
        since=since,
    )
