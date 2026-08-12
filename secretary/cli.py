from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

from dateutil import parser as date_parser

# Google API 系（calendar_ops / tasks_ops / deadline_sync）は重い依存を引くため、
# 各コマンド内で遅延 import する。これにより note/x 系コマンドは Google 依存なしで動く。


def _cmd_cal_list(args: argparse.Namespace) -> None:
    from secretary import calendar_ops

    items = calendar_ops.list_events(days=args.days, max_results=args.max)
    for ev in items:
        start = ev.get("start", {})
        when = start.get("dateTime") or start.get("date") or ""
        print(f"{when}\t{ev.get('summary', '(無題)')}\tid={ev.get('id')}")


def _cmd_cal_add(args: argparse.Namespace) -> None:
    from secretary import calendar_ops

    start = date_parser.parse(args.start)
    end = date_parser.parse(args.end) if args.end else None
    ev = calendar_ops.create_event(
        args.summary,
        start=start,
        end=end,
        duration_minutes=args.duration,
        description=args.description,
    )
    print(json.dumps({"id": ev.get("id"), "htmlLink": ev.get("htmlLink")}, ensure_ascii=False))


def _cmd_cal_delete(args: argparse.Namespace) -> None:
    from secretary import calendar_ops

    calendar_ops.delete_event(args.event_id)
    print("deleted")


def _cmd_tasks_list(args: argparse.Namespace) -> None:
    from secretary import tasks_ops

    items = tasks_ops.list_tasks(show_completed=args.completed)
    for t in items:
        status = t.get("status", "")
        print(f"{status}\t{t.get('title', '')}\tid={t.get('id')}")


def _cmd_tasks_add(args: argparse.Namespace) -> None:
    from secretary import tasks_ops

    t = tasks_ops.add_task(args.title, notes=args.notes)
    print(json.dumps({"id": t.get("id")}, ensure_ascii=False))


def _cmd_tasks_done(args: argparse.Namespace) -> None:
    from secretary import tasks_ops

    tasks_ops.complete_task(args.task_id)
    print("completed")


def _cmd_tasks_delete(args: argparse.Namespace) -> None:
    from secretary import tasks_ops

    tasks_ops.delete_task(args.task_id)
    print("deleted")


def _cmd_tasklists(args: argparse.Namespace) -> None:
    from secretary import tasks_ops

    for tl in tasks_ops.list_tasklists():
        print(f"{tl.get('title', '')}\tid={tl.get('id')}")


def _cmd_goal_plan(args: argparse.Namespace) -> None:
    from secretary.goal_planner.interviewer import run_interview
    from secretary.goal_planner.decomposer import TaskDecomposer
    from secretary.goal_planner.scheduler import schedule_goal

    goal = run_interview()
    print("\nAIがタスクを分解中...")
    decomposer = TaskDecomposer()
    goal.sub_tasks = decomposer.decompose(goal)

    print(f"\n{len(goal.sub_tasks)}件のサブタスクを生成しました：")
    for t in goal.sub_tasks:
        print(f"  {t.order}. {t.title}（{t.estimated_minutes}分）")

    ans = input("\nこの内容でカレンダーに登録しますか？ [y/n]: ").strip().lower()
    if ans == "y":
        schedule_goal(goal)
        print("\n登録完了！")
    else:
        print("登録をキャンセルしました。")


def _cmd_goal_daily(args: argparse.Namespace) -> None:
    from secretary.daily_view import show_daily_view

    target = None
    if args.date:
        target = date_parser.parse(args.date).date()
    show_daily_view(target)


def _cmd_goal_complete(args: argparse.Namespace) -> None:
    from secretary.learning.tracker import TaskTracker
    from secretary import calendar_ops

    ev = calendar_ops.get_event(args.event_id)
    summary = ev.get("summary", "").removeprefix("【目標】")
    desc = ev.get("description", "")
    try:
        meta = json.loads(desc)
    except (json.JSONDecodeError, TypeError):
        meta = {}

    estimated = meta.get("estimated_minutes", 0)
    category = meta.get("category", "other")
    goal_id = meta.get("goal_id", "")

    print(f"タスク: {summary}")
    print(f"見積時間: {estimated}分")

    while True:
        raw = input("実際にかかった時間（分）を入力してください: ").strip()
        if raw.isdigit() and int(raw) > 0:
            actual = int(raw)
            break
        print("  ※ 正の整数を入力してください。")

    tracker = TaskTracker()
    tracker.record_completion(
        task_title=summary,
        category=category,
        estimated_minutes=estimated,
        actual_minutes=actual,
        goal_id=goal_id,
    )
    print(f"記録しました（見積: {estimated}分 / 実績: {actual}分）")


def _cmd_note_schedule(args: argparse.Namespace) -> None:
    from secretary.note_ops import NoteBrowser, PostConfig

    cfg = PostConfig.load(args.config)
    errors = cfg.validate()
    if errors:
        print("予約を中止しました（要修正）:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        raise SystemExit(2)

    if args.dry_run:
        print(json.dumps({
            "status": "ok",
            "title": cfg.title,
            "hashtags": cfg.hashtags,
            "magazine": cfg.magazine,
            "thumbnail": str(cfg.thumbnail),
            "publish_at": cfg.publish_at.isoformat() if cfg.publish_at else None,
            "links": {k: v.url for k, v in cfg.links.items()},
        }, ensure_ascii=False, indent=2))
        print("\n検証OK。--dry-run のため予約は実行していません。")
        return

    browser = NoteBrowser(headless=not args.show, slow_mo=args.slow_mo)
    result = browser.schedule(cfg)
    print(json.dumps(result, ensure_ascii=False, indent=2))

    if args.x_stock and cfg.x_announcement:
        from secretary import x_stock
        path = x_stock.add_from_config(cfg, note_url=result.get("url"))
        print(f"X告知をストックに追加: {path}")


def _cmd_note_login(args: argparse.Namespace) -> None:
    from secretary.note_ops import login_and_save

    login_and_save(headless=False)


def _cmd_x_stock(args: argparse.Namespace) -> None:
    from secretary import x_stock
    from secretary.note_ops import PostConfig

    cfg = PostConfig.load(args.config)
    path = x_stock.add_from_config(cfg, note_url=args.note_url)
    print(f"X告知をストックに追加: {path}")


def _cmd_deadline_sync(args: argparse.Namespace) -> None:
    from secretary.deadline_sync import default_rules_path, run as deadline_run

    cfg = Path(args.config) if args.config else default_rules_path()
    stats = deadline_run(
        config_path=cfg,
        horizon_days=args.days,
        dry_run=args.dry_run,
    )
    print(json.dumps(stats, ensure_ascii=False, indent=2))


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="secretary", description="Google Calendar / Tasks CLI")
    sub = p.add_subparsers(dest="cmd", required=True)

    pl = sub.add_parser("cal-list", help="直近の予定を一覧")
    pl.add_argument("--days", type=int, default=7)
    pl.add_argument("--max", type=int, default=50)
    pl.set_defaults(func=_cmd_cal_list)

    pa = sub.add_parser("cal-add", help="予定を追加")
    pa.add_argument("summary")
    pa.add_argument("--start", required=True, help="ISO または自然言語日時")
    pa.add_argument("--end", help="省略時は --duration 分後")
    pa.add_argument("--duration", type=int, default=60)
    pa.add_argument("--description", "-d", default=None)
    pa.set_defaults(func=_cmd_cal_add)

    pd = sub.add_parser("cal-delete", help="予定を削除")
    pd.add_argument("event_id")
    pd.set_defaults(func=_cmd_cal_delete)

    tl = sub.add_parser("tasks-list", help="タスク一覧")
    tl.add_argument("--completed", action="store_true")
    tl.set_defaults(func=_cmd_tasks_list)

    ta = sub.add_parser("tasks-add", help="タスク追加")
    ta.add_argument("title")
    ta.add_argument("--notes", "-n", default=None)
    ta.set_defaults(func=_cmd_tasks_add)

    td = sub.add_parser("tasks-done", help="タスク完了")
    td.add_argument("task_id")
    td.set_defaults(func=_cmd_tasks_done)

    tx = sub.add_parser("tasks-delete", help="タスク削除")
    tx.add_argument("task_id")
    tx.set_defaults(func=_cmd_tasks_delete)

    tz = sub.add_parser("tasklists", help="タスクリスト一覧")
    tz.set_defaults(func=_cmd_tasklists)

    gp = sub.add_parser("goal-plan", help="目標のヒアリング→タスク生成→カレンダー登録")
    gp.set_defaults(func=_cmd_goal_plan)

    gd = sub.add_parser("goal-daily", help="デイリービューを表示")
    gd.add_argument("--date", "-d", default=None, help="表示する日付（省略時は今日）")
    gd.set_defaults(func=_cmd_goal_daily)

    gc = sub.add_parser("goal-complete", help="タスク完了を記録（実績時間を入力）")
    gc.add_argument("event_id", help="カレンダーイベントID")
    gc.set_defaults(func=_cmd_goal_complete)

    ds = sub.add_parser(
        "deadline-sync",
        help="カレンダーから締切予定を逆算して同期（Google カレンダー通知＋タスク）",
    )
    ds.add_argument("--config", "-c", default=None, help="deadline_rules.yaml のパス")
    ds.add_argument("--days", type=int, default=45, help="先の予定を何日分見るか")
    ds.add_argument("--dry-run", action="store_true", help="書き込みせず件数のみ")
    ds.set_defaults(func=_cmd_deadline_sync)

    ns = sub.add_parser("note-schedule", help="note 記事を予約投稿（設定YAMLから）")
    ns.add_argument("--config", "-c", required=True, help="投稿設定 YAML のパス")
    ns.add_argument("--dry-run", action="store_true", help="検証のみ（ブラウザ操作なし）")
    ns.add_argument("--show", action="store_true", help="ブラウザを表示（既定はヘッドレス）")
    ns.add_argument("--slow-mo", type=int, default=0, help="各操作のディレイ(ms)")
    ns.add_argument("--x-stock", action="store_true", help="予約後に X 告知をストックへ追加")
    ns.set_defaults(func=_cmd_note_schedule)

    nl = sub.add_parser("note-login", help="note に手動ログインして Cookie を保存")
    nl.set_defaults(func=_cmd_note_login)

    xs = sub.add_parser("x-stock", help="X 告知文を手貼り用ストックへ追加")
    xs.add_argument("--config", "-c", required=True, help="投稿設定 YAML のパス")
    xs.add_argument("--note-url", default=None, help="[記事URL] を置換する記事URL")
    xs.set_defaults(func=_cmd_x_stock)

    args = p.parse_args(argv)
    try:
        args.func(args)
    except Exception as e:
        print(str(e), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
