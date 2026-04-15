from __future__ import annotations

from datetime import date
from typing import Callable

from dateutil import parser as date_parser

from secretary.goal_planner.models import Goal


def run_interview(
    input_fn: Callable[[str], str] = input,
    print_fn: Callable[[str], None] = print,
) -> Goal:
    print_fn("\n" + "=" * 50)
    print_fn("  目標プランニング - ヒアリング開始")
    print_fn("=" * 50)

    title = _ask(input_fn, print_fn, "目標・やりたいことを教えてください: ").strip()
    deadline = _ask_deadline(input_fn, print_fn)
    daily_minutes = _ask_daily_minutes(input_fn, print_fn)
    parallel_projects = _ask_parallel_projects(input_fn, print_fn)
    priority = _ask_priority(input_fn, print_fn)

    goal = Goal(
        title=title,
        deadline=deadline,
        daily_minutes=daily_minutes,
        parallel_projects=parallel_projects,
        priority=priority,
    )

    _confirm_goal(goal, print_fn)
    return goal


def _ask(
    input_fn: Callable[[str], str],
    print_fn: Callable[[str], None],
    prompt: str,
) -> str:
    while True:
        val = input_fn(prompt).strip()
        if val:
            return val
        print_fn("  ※ 入力が空です。もう一度お試しください。")


def _ask_deadline(
    input_fn: Callable[[str], str],
    print_fn: Callable[[str], None],
) -> date:
    while True:
        raw = _ask(input_fn, print_fn, "達成期限はいつですか？（例: 2026-05-31、来月末、3週間後）: ")
        try:
            return date_parser.parse(raw, dayfirst=False, fuzzy=True).date()
        except Exception:
            print_fn("  ※ 日付を認識できませんでした。YYYY-MM-DD 形式でも試してみてください。")


def _ask_daily_minutes(
    input_fn: Callable[[str], str],
    print_fn: Callable[[str], None],
) -> int:
    while True:
        raw = _ask(
            input_fn,
            print_fn,
            "この目標に1日に使える時間はどのくらいですか？（例: 60、90分、2時間）: ",
        )
        digits = "".join(c for c in raw if c.isdigit())
        if not digits:
            # "2時間" → 120
            for unit, mult in [("時間", 60), ("hour", 60), ("h", 60)]:
                if unit in raw.lower():
                    num_part = "".join(c for c in raw.split(unit)[0] if c.isdigit() or c == ".")
                    try:
                        return round(float(num_part) * mult)
                    except ValueError:
                        pass
            print_fn("  ※ 分単位の数値を入力してください（例: 90）。")
            continue
        val = int(digits)
        if val <= 0:
            print_fn("  ※ 0より大きい値を入力してください。")
            continue
        return val


def _ask_parallel_projects(
    input_fn: Callable[[str], str],
    print_fn: Callable[[str], None],
) -> list[str]:
    raw = input_fn(
        "並行して進めているプロジェクトはありますか？（カンマ区切り、なければそのままEnter）: "
    ).strip()
    if not raw:
        return []
    return [p.strip() for p in raw.split(",") if p.strip()]


def _ask_priority(
    input_fn: Callable[[str], str],
    print_fn: Callable[[str], None],
) -> int:
    while True:
        raw = _ask(input_fn, print_fn, "この目標の優先度を教えてください（1=最高、2=高、3=普通、4=低）: ")
        digits = "".join(c for c in raw if c.isdigit())
        if digits and 1 <= int(digits) <= 4:
            return int(digits)
        print_fn("  ※ 1〜4 の数値を入力してください。")


def _confirm_goal(goal: Goal, print_fn: Callable[[str], None]) -> None:
    parallel = "、".join(goal.parallel_projects) if goal.parallel_projects else "なし"
    print_fn("\n--- ヒアリング内容の確認 ---")
    print_fn(f"  目標      : {goal.title}")
    print_fn(f"  期限      : {goal.deadline}")
    print_fn(f"  1日の時間 : {goal.daily_minutes}分")
    print_fn(f"  並行PJ    : {parallel}")
    print_fn(f"  優先度    : {goal.priority}")
    print_fn("----------------------------\n")
