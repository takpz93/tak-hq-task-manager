#!/bin/bash
# 毎朝の秘書エージェント起動スクリプト
# このファイルをダブルクリックするか、cronで自動実行してください

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_FILE="$SCRIPT_DIR/morning_agent.log"

echo "=== $(date '+%Y-%m-%d %H:%M:%S') 実行開始 ===" >> "$LOG_FILE"

cd "$SCRIPT_DIR"
source .venv/bin/activate
python morning_agent.py 2>&1 | tee -a "$LOG_FILE"

echo "=== 実行完了 ===" >> "$LOG_FILE"
