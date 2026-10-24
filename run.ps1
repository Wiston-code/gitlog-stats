# 一键验证脚本（Windows）：不联网、不安装，直接跑测试 + 示例
# 用法: .\run.ps1
# 说明: 本文件保存为「UTF-8 带 BOM」，否则 Windows PowerShell 5.1 会把中文读成乱码。

$ErrorActionPreference = 'Stop'
$env:PYTHONUTF8 = '1'
$env:PYTHONPATH = Join-Path $PSScriptRoot 'src'
Set-Location -Path $PSScriptRoot

Write-Host "[1/2] 单元测试" -ForegroundColor Cyan
python -m unittest discover -s tests -v

Write-Host "[2/2] 示例输出" -ForegroundColor Cyan
python -m gitlog_stats.cli --file examples\sample_gitlog.txt

Write-Host ""
Write-Host "想看当前仓库的统计: python -m gitlog_stats.cli ." -ForegroundColor Green
Write-Host "想装成全局命令:     pip install -e .  ->  然后直接输 gitlog-stats" -ForegroundColor Green