#!/usr/bin/env bash
# 一键验证脚本（macOS / Linux）：不联网、不安装，直接跑测试 + 示例
set -euo pipefail
cd "$(dirname "$0")"
export PYTHONPATH="$PWD/src:${PYTHONPATH:-}"

echo "[1/2] 单元测试"
python3 -m unittest discover -s tests -v

echo "[2/2] 示例输出"
python3 -m gitlog_stats.cli --file examples/sample_gitlog.txt

echo
echo "想看当前仓库的统计: python3 -m gitlog_stats.cli ."
echo "想装成全局命令:     pip install -e ."