from __future__ import annotations

import json
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from secretary import calendar_ops

_TZ = ZoneInfo("Asia/Tokyo")

_DAYS_JA = ["月", "火", "水", "木", "金", "土", "日"]


def show_daily_view(target_date: date | None = None) -> None:
    """指定日（デフォルト：今日）のデイリービューを表示する。"""
    d = target_date or date.today()
    now = datetime.now(_TZ)

    day_start = datetime(d.year, d.month, d.day, 0, 0, tzinfo=_TZ)
    day_end = day_start + timedelta(days=1) - timedelta(seconds=1)

    events = calendar_ops.list_events_range(
        time_min=day_start.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
        time_max=day_end.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
    )

    weekday = _DAYS_JA[d.weekday()]
    print("=" * 52)
    print(f"  {d.strftime('%Y年%m月%d日')} ({weekday}) のデイリービュー")
    print("=" * 52)

    # 通常イベントとゴールタスクを分類
    goal_events: list[dict] = []
    normal_events: list[dict] = []
    for ev in events:
        desc = ev.get("description", "")
        try:
            meta = json.loads(desc)
            if "goal_id" in meta:
                goal_events.append(ev)
                continue
        except (json.JSONDecodeError, TypeError):
            pass
        normal_events.append(ev)

    # 今日の予定
    print("\n【今日の予定】")
    if not events:
        print("  （予定なし）")
    else:
        for ev in events:
            start_str = _format_event_time(ev)
            summary = ev.get("summary", "(無題)")
            marker = "★" if ev in goal_events else " "
            print(f"  {marker} {start_str}  {summary}")

    # 目標の進捗
    goal_summary = _collect_goal_progress(d)
    if goal_summary:
        print("\n【目標の進捗】")
        for gs in goal_summary:
            bar = _progress_bar(gs["done"], gs["total"])
            print(f"  {gs['title']}")
            print(f"    {bar} {gs['done']}/{gs['total']}タスク完了")
            print(f"    期限: {gs['deadline']}  （残{gs['remaining_days']}日）")

    # 今日のゴールタスク作業量
    goal_minutes = sum(
        _get_event_duration(ev) for ev in goal_events
    )
    if goal_minutes > 0:
        print(f"\n【今日の目標作業予定: {goal_minutes}分】")

    print("\n" + "=" * 52)


def _format_event_time(ev: dict) -> str:
    start = ev.get("start", {})
    dt_str = start.get("dateTime") or start.get("date") or ""
    if "T" in dt_str:
        dt = datetime.fromisoformat(dt_str).astimezone(_TZ)
        return dt.strftime("%H:%M")
    return dt_str


def _get_event_duration(ev: dict) -> int:
    start = ev.get("start", {})
    end = ev.get("end", {})
    s = start.get("dateTime")
    e = end.get("dateTime")
    if s and e:
        ds = datetime.fromisoformat(s)
        de = datetime.fromisoformat(e)
        return round((de - ds).total_seconds() / 60)
    return 0


def _collect_goal_progress(target_date: date) -> list[dict]:
    """今後90日分のカレンダーからゴールタスクを収集して進捗を集計する。"""
    today = date.today()
    start = datetime(today.year, today.month, today.day, tzinfo=_TZ)
    end = start + timedelta(days=90)

    events = calendar_ops.list_events_range(
        time_min=start.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
        time_max=end.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
        max_results=500,
    )

    # goal_id ごとに集計
    goals: dict[str, dict] = {}
    for ev in events:
        try:
            meta = json.loads(ev.get("description", ""))
        except (json.JSONDecodeError, TypeError):
            continue
        if "goal_id" not in meta:
            continue

        gid = meta["goal_id"]
        if gid not in goals:
            goals[gid] = {
                "title": meta.get("goal_title", "(不明)"),
                "total": 0,
                "done": 0,
                "deadline": "",
                "remaining_days": 0,
            }
        goals[gid]["total"] += 1
        # 完了済みイベントは status が cancelled
        if ev.get("status") == "cancelled":
            goals[gid]["done"] += 1

    # デッドラインは目標イベントから取れないため remaining_days は省略
    return list(goals.values())


def _progress_bar(done: int, total: int, width: int = 10) -> str:
    if total == 0:
        return "─" * width
    filled = round(done / total * width)
    return "█" * filled + "░" * (width - filled)
