from __future__ import annotations

import json
import logging
from datetime import date, datetime, timedelta
from typing import Callable
from zoneinfo import ZoneInfo

from secretary import calendar_ops
from secretary.goal_planner.models import Goal, SubTask

logger = logging.getLogger(__name__)

_TZ = ZoneInfo("Asia/Tokyo")
_WORK_START_HOUR = 9   # 作業開始時刻（時）
_WORK_END_HOUR = 22    # 作業終了時刻（時）


def schedule_goal(
    goal: Goal,
    print_fn: Callable[[str], None] = print,
    input_fn: Callable[[str], str] = input,
) -> Goal:
    """目標のサブタスクをカレンダーに均等分散して登録する。"""
    today = date.today()
    if goal.deadline <= today:
        print_fn("  ※ 期限が過去または今日です。今日から開始します。")

    working_days = _get_working_days(today, goal.deadline)
    if not working_days:
        print_fn("  ※ 稼働日が見つかりません。今日1日で実行します。")
        working_days = [today]

    total_minutes = sum(t.estimated_minutes for t in goal.sub_tasks)
    print_fn(
        f"\nタスク合計時間: {total_minutes}分 / 稼働日数: {len(working_days)}日"
    )

    placements = _distribute_tasks(goal.sub_tasks, working_days, goal.daily_minutes)

    # 複数プロジェクトがある場合の確認
    if goal.parallel_projects:
        parallel = "、".join(goal.parallel_projects)
        ans = input_fn(
            f"\n並行プロジェクト（{parallel}）があります。"
            "このまま登録しますか？ [y/n]: "
        ).strip().lower()
        if ans != "y":
            print_fn("  登録をキャンセルしました。")
            return goal

    print_fn("\nGoogle Calendarにタスクを登録しています...")
    for task, scheduled_dt in placements:
        try:
            ev = calendar_ops.create_event(
                f"【目標】{task.title}",
                start=scheduled_dt,
                duration_minutes=task.estimated_minutes,
                description=json.dumps(
                    {
                        "goal_id": goal.goal_id,
                        "goal_title": goal.title,
                        "task_order": task.order,
                        "category": task.category,
                        "estimated_minutes": task.estimated_minutes,
                    },
                    ensure_ascii=False,
                ),
                reminder_minutes_before=[30],
            )
            task.calendar_event_id = ev.get("id")
            print_fn(f"  + {scheduled_dt.strftime('%m/%d %H:%M')} {task.title}")
        except Exception as e:
            logger.error("イベント登録失敗: %s: %s", task.title, e)
            print_fn(f"  ✗ 登録失敗: {task.title} ({e})")

    return goal


def _get_working_days(start: date, end: date) -> list[date]:
    """start〜end（含む）の平日リストを返す。"""
    days = []
    cur = max(start, date.today())
    while cur <= end:
        if cur.weekday() < 5:  # 月〜金
            days.append(cur)
        cur += timedelta(days=1)
    return days


def _distribute_tasks(
    tasks: list[SubTask],
    working_days: list[date],
    daily_minutes: int,
) -> list[tuple[SubTask, datetime]]:
    """タスクを稼働日に均等に分散し、(タスク, 開始日時) のリストを返す。"""
    placements: list[tuple[SubTask, datetime]] = []
    day_index = 0
    day_used: dict[date, int] = {}  # 日付ごとの使用済み分数

    for task in sorted(tasks, key=lambda t: t.order):
        placed = False
        attempts = 0
        while not attempts or (not placed and attempts < len(working_days) * 2):
            if day_index >= len(working_days):
                day_index = 0
            d = working_days[day_index]
            used = day_used.get(d, 0)
            if used + task.estimated_minutes <= daily_minutes:
                start_dt = _next_slot(d, used)
                placements.append((task, start_dt))
                day_used[d] = used + task.estimated_minutes
                placed = True
            day_index += 1
            attempts += 1

        if not placed:
            # どの日にも入らない場合は最初の日に強制配置
            d = working_days[0]
            used = day_used.get(d, 0)
            start_dt = _next_slot(d, used)
            placements.append((task, start_dt))
            day_used[d] = used + task.estimated_minutes

    return placements


def _next_slot(day: date, used_minutes: int) -> datetime:
    """その日のWORK_START_HROURから used_minutes 分後のdatetimeを返す。"""
    base = datetime(day.year, day.month, day.day, _WORK_START_HOUR, 0, tzinfo=_TZ)
    return base + timedelta(minutes=used_minutes)
