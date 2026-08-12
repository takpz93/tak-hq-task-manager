"""X（旧Twitter）告知文の「コピペ予約用ストック」管理。

X も API を使わない前提のため、手貼り用の告知文を 1 つのストックファイルに
時刻付きで積んでおく。19:00 などの投稿時刻に、この一覧からコピペする運用。
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from secretary.note_ops import PostConfig, repo_root

STOCK_PATH = repo_root() / "note_posts" / "x_stock.md"


def add_from_config(cfg: PostConfig, note_url: str | None = None) -> Path:
    """PostConfig の x_announcement をストックに追加する。"""
    xa = cfg.x_announcement
    if xa is None or not xa.text.strip():
        raise ValueError("x_announcement が設定されていません。")
    text = xa.text
    if note_url:
        text = text.replace("[記事URL]", note_url)
    return append(text=text, post_at=xa.post_at, source=cfg.title)


def append(text: str, post_at: datetime | None, source: str = "") -> Path:
    STOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    when = post_at.strftime("%Y-%m-%d %H:%M") if post_at else "(時刻未定)"
    header = f"## {when}  手貼り用"
    if source:
        header += f"  ── {source}"
    block = f"{header}\n\n```\n{text.rstrip()}\n```\n"
    existing = STOCK_PATH.read_text(encoding="utf-8") if STOCK_PATH.is_file() else \
        "# X 告知ストック（手貼り用・ハッシュタグなし）\n"
    STOCK_PATH.write_text(existing.rstrip("\n") + "\n\n" + block, encoding="utf-8")
    return STOCK_PATH
