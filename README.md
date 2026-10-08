# gitlog-stats

[![CI](https://github.com/Wiston-code/gitlog-stats/actions/workflows/ci.yml/badge.svg)](https://github.com/Wiston-code/gitlog-stats/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

看仓库提交历史的小工具：谁提交最多、哪几个月在忙、习惯几点写代码、最长连着提交了几天。

只用标准库。不想装也能跑 —— `--file` 直接读存下来的 git log。

## 安装

```bash
git clone https://github.com/Wiston-code/gitlog-stats.git
cd gitlog-stats
pip install -e .
```

## 用法

```bash
gitlog-stats                                     # 当前目录
gitlog-stats --repo D:/dev/some-project          # 指定仓库
gitlog-stats --since 2026-01-01                  # 只看今年
gitlog-stats --json                              # 给脚本用
gitlog-stats --file examples/sample_gitlog.txt   # 没装 git 也能看效果
```

## 输出

`gitlog-stats --file examples/sample_gitlog.txt`：

```text
repo    : examples/sample_gitlog.txt
commits : 9   authors: 3   range: 2025-09-02 -> 2025-11-18   active days: 7   longest streak: 2d

top authors
   1. Wiston                       6   66.7%  ██████████████████████
   2. Ada                          2   22.2%  ███████
   3. Bob                          1   11.1%  ███▌

commits by month
  2025-09  ██████████████████████ 3
  2025-10  ██████████████████████ 3
  2025-11  ██████████████████████ 3

commits by hour
   8h ████████████ 1
   9h ████████████ 1
  10h ████████████ 1
  11h ████████████ 1
  14h ████████████ 1
  19h ████████████ 1
  21h ████████████ 1
  22h ████████████ 1
  23h ████████████ 1
  peak hour: 08:00
```

`--json` 是同一份数据的结构化版本：

```json
{
  "ok": true,
  "repo": "examples/sample_gitlog.txt",
  "report": {
    "total": 9,
    "author_count": 3,
    "authors": [{ "name": "Wiston", "commits": 6, "share": 0.6667 }],
    "active_days": 7,
    "longest_streak": 2,
    "first": "2025-09-02",
    "last": "2025-11-18",
    "since": null
  }
}
```

## 参数

| 参数 | 说明 |
|---|---|
| `path` / `--repo PATH` | 仓库路径，默认当前目录 |
| `--file LOG` | 读已保存的 `git log` 文本，不需要 git |
| `--since YYYY-MM-DD` | 只算这天（含）之后的提交 |
| `--top N` | 显示前 N 个作者，默认 5 |
| `--width N` | 柱状图宽度，默认 22 |
| `--json` | 输出 JSON |
| `--no-chart` | 不画柱状图 |

退出码 0 正常，2 是参数、路径或 git 不可用。

## 怎么算的

`git log --pretty=format:%H%x1f%an%x1f%ae%x1f%ad%x1f%s%x1e --date=iso` 拿原始文本，`parser.py` 按 `\x1e` 分记录、`\x1f` 分字段，`stats.py` 聚合，`cli.py` 管参数和渲染。

解析和聚合都是纯函数，不碰 subprocess，所以写测试的时候不需要真的准备一个仓库。

## 测试

```bash
python -m unittest discover -s tests -v
```

Windows 上 `.\run.ps1`，macOS / Linux 上 `./run.sh`，不联网不安装，直接跑测试加示例。

## License

MIT
