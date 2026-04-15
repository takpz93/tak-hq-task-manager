#!/usr/bin/env python3
"""
スマホからアクセスできる公開URLでアプリを起動する。

使い方:
    cd "/Users/takmiura/Desktop/Tak HQ/secretary"
    .venv/bin/python start_public.py

ngrok の無料アカウント（authtoken）を設定すると URL が固定される:
    .venv/bin/python -c "from pyngrok import ngrok; ngrok.set_auth_token('YOUR_TOKEN')"
"""
import subprocess
import sys
import time
from pathlib import Path

DIR = Path(__file__).resolve().parent


def main():
    print("=" * 50)
    print("📱 タスク管理アプリ 公開起動スクリプト")
    print("=" * 50)

    # Streamlit を起動
    print("\n[1/2] Streamlit を起動中...")
    proc = subprocess.Popen(
        [str(DIR / ".venv/bin/streamlit"), "run", str(DIR / "app.py"),
         "--server.port", "8501",
         "--server.headless", "true",
         "--server.address", "0.0.0.0"],
        cwd=str(DIR),
    )
    time.sleep(3)

    # ngrok トンネルを開く
    print("[2/2] ngrok トンネルを開いています...")
    try:
        from pyngrok import ngrok, conf
        tunnel = ngrok.connect(8501, "http")
        public_url = tunnel.public_url
        # http → https に変換
        if public_url.startswith("http://"):
            public_url = "https://" + public_url[7:]

        print("\n" + "=" * 50)
        print("✅ 起動完了！スマホで以下のURLを開いてください")
        print()
        print(f"  🌐 {public_url}")
        print()
        print("=" * 50)
        print("（Ctrl+C で停止）\n")

    except Exception as e:
        print(f"ngrok 接続エラー: {e}")
        print("ローカルURL: http://localhost:8501")

    try:
        proc.wait()
    except KeyboardInterrupt:
        print("\n停止します...")
        proc.terminate()
        from pyngrok import ngrok
        ngrok.kill()


if __name__ == "__main__":
    main()
