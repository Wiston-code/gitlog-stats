"""Parse ``git log`` output into :class:`Commit` records.

这里不碰子进程：要么喂它已经拿到的文本，要么让 cli 去调 git。
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from typing import List

RECORD_SEP = "\x1e"
FIELD_SEP = "\x1f"

#: CLI 向 git 要的格式，也是这个解析器吃的格式。
PRETTY_FORMAT = "--pretty=format:%H%x1f%an%x1f%ae%x1f%ad%x1f%s%x1e"

_DATE_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})[ T](\d{2}):(\d{2}):(\d{2})")


@dataclass(frozen=True)
class Commit:
    sha: str
    author: str
    email: str
    date: datetime
    subject: str

    @property
    def month(self) -> str:
        return f"{self.date:%Y-%m}"

    @property
    def day(self) -> str:
        return f"{self.date:%Y-%m-%d}"


def parse_date(raw: str) -> datetime:
    """解析 ``--date=iso`` 的时间戳，格式不对就抛 ``ValueError``。"""
    match = _DATE_RE.match(raw.strip())
    if not match:
        raise ValueError(f"unrecognised date: {raw!r}")
    year, month, day, hour, minute, second = (int(part) for part in match.groups())
    return datetime(year, month, day, hour, minute, second)


def parse_log(text: str) -> List[Commit]:
    """把 ``git log`` 的原始输出切成 commit 列表。

    空块、截断的记录、时间解析不了的记录都跳过 —— 一行坏了不该毁掉整份历史。
    """
    commits: List[Commit] = []
    for chunk in text.split(RECORD_SEP):
        chunk = chunk.strip("\r\n")
        if not chunk:
            continue
        parts = chunk.split(FIELD_SEP)
        if len(parts) < 5:
            continue
        sha, author, email, raw_date = parts[:4]
        # 提交信息里可能带字段分隔符，粘回去。
        subject = FIELD_SEP.join(parts[4:])
        try:
            date = parse_date(raw_date)
        except ValueError:
            continue
        commits.append(
            Commit(
                sha=sha.strip(),
                author=author.strip() or "(unknown)",
                email=email.strip(),
                date=date,
                subject=subject.strip(),
            )
        )
    return commits
