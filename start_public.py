#!/usr/bin/env python3
"""
スマホからアクセスできる公開URLでアプリを起動する。

使い方:
    cd "/Users/takmiura/Desktop/Tak HQ/secretary"
    .venv/bin/python start_public.py

──────────────────────────────────────────
URLは起動のたびに変わります（無料・登録不要）。
固定URLにしたい場合は ngrok の有料プランをご利用ください。
"""
import re
import subprocess
import sys
import threading
import time
from pathlib import Path

DIR = Path(__file__).resolve().parent
PORT = 8501


def start_streamlit():
    subprocess.Popen(
        [str(DIR / ".venv/bin/streamlit"), "run", str(DIR / "app.py"),
         "--server.port", str(PORT),
         "--server.headless", "true",
         "--server.address", "0.0.0.0"],
        cwd=str(DIR),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def main():
    print("=" * 52)
    print("📱 タスク管理アプリ 公開起動スクリプト")
    print("=" * 52)

    # ── Streamlit 起動 ────────────────────────────────
    print("\n[1/2] Streamlit を起動中...")
    start_streamlit()
    time.sleep(4)

    # ── serveo.net で SSH トンネル ────────────────────
    print("[2/2] 公開URLを取得中（serveo.net）...")
    proc = subprocess.Popen(
        ["ssh",
         "-o", "StrictHostKeyChecking=no",
         "-o", "ServerAliveInterval=60",
         "-o", "ExitOnForwardFailure=yes",
         "-R", f"80:localhost:{PORT}",
         "serveo.net"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    url = None
    for line in proc.stdout:
        m = re.search(r"https?://\S+", line)
        if m:
            url = m.group(0)
            break

    if url:
        print("\n" + "=" * 52)
        print("✅ 起動完了！スマホで以下のURLを開いてください")
        print()
        print(f"   🌐  {url}")
        print()
        print("=" * 52)
        print("（このウィンドウを閉じると停止します）\n")
    else:
        print("⚠️  公開URL取得に失敗しました。")
        print(f"ローカルURL: http://localhost:{PORT}")

    try:
        proc.wait()
    except KeyboardInterrupt:
        print("\n停止します...")
        proc.terminate()


if __name__ == "__main__":
    main()
