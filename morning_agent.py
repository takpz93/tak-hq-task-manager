"""
morning_agent.py
毎朝自動実行：今日のスケジュールサマリー＋未来の予定へのマイルストーン自動生成
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

# secretaryモジュールのパスを追加
SECRETARY_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SECRETARY_DIR))

# Google認証ファイルのパスを環境変数で指定
os.environ.setdefault("GOOGLE_CREDENTIALS", str(SECRETARY_DIR / "credentials.json"))
os.environ.setdefault("GOOGLE_TOKEN", str(SECRETARY_DIR / "token.json"))

from secretary import calendar_ops, tasks_ops
import anthropic

TZ = ZoneInfo("Asia/Tokyo")


def get_today_events() -> list[dict]:
    """今日の予定を取得"""
    now = datetime.now(TZ)
    end_of_day = now.replace(hour=23, minute=59, second=59)
    return calendar_ops.list_events_range(
        time_min=now.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
        time_max=end_of_day.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
    )


def get_upcoming_events(days: int = 30) -> list[dict]:
    """今後30日の予定を取得"""
    return calendar_ops.list_events(days=days, max_results=100)


def get_pending_tasks() -> list[dict]:
    """未完了タスクを取得"""
    try:
        return tasks_ops.list_tasks(show_completed=False)
    except Exception:
        return []


def format_event(ev: dict) -> str:
    """イベントを読みやすい文字列に変換"""
    start = ev.get("start", {})
    when = start.get("dateTime") or start.get("date") or ""
    if "T" in when:
        dt = datetime.fromisoformat(when).astimezone(TZ)
        when_str = dt.strftime("%m/%d %H:%M")
    else:
        when_str = when
    return f"{when_str} {ev.get('summary', '(無題)')}"


def generate_morning_report(today_events: list, upcoming_events: list, tasks: list) -> dict:
    """Claude AIで朝のレポートとマイルストーンを生成"""

    today_str = datetime.now(TZ).strftime("%Y年%m月%d日 (%A)")

    today_list = "\n".join(f"- {format_event(e)}" for e in today_events) or "（予定なし）"
    upcoming_list = "\n".join(f"- {format_event(e)}" for e in upcoming_events[:20])
    tasks_list = "\n".join(f"- {t.get('title', '')}" for t in tasks[:20]) or "（タスクなし）"

    prompt = f"""今日は{today_str}です。
あなたはTakeshiの秘書AIです。以下の情報をもとに、朝のレポートとマイルストーンを作成してください。

【今日の予定】
{today_list}

【今後30日の予定】
{upcoming_list}

【現在の未完了タスク】
{tasks_list}

以下のJSON形式で返してください：

```json
{{
  "greeting": "今日の一言（励ましや気づきなど、2〜3文）",
  "today_summary": "今日のスケジュールの簡潔なまとめ（3〜5文）",
  "milestones": [
    {{
      "event_title": "対象の予定タイトル",
      "event_date": "予定の日付（YYYY-MM-DD）",
      "tasks": [
        {{
          "title": "マイルストーンのタスク名",
          "days_before": 3,
          "notes": "タスクの補足説明"
        }}
      ]
    }}
  ],
  "focus": "今日特に集中すべきことや優先事項（1〜2文）"
}}
```

ルール：
- マイルストーンは準備が必要そうな予定（会議・撮影・締切など）にだけ作る
- すでに同じようなタスクがある場合は作らない
- タスク名は具体的で行動できる内容にする（例：「MUSUBI定例の資料作成」「撮影機材の確認リスト作成」）
- days_beforeは予定の何日前にやるべきかの数値
"""

    client = anthropic.Anthropic()
    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )

    import re
    text = response.content[0].text
    match = re.search(r"```json\n([\s\S]*?)\n```", text)
    if match:
        return json.loads(match.group(1))
    return json.loads(text)


def add_milestones_to_tasks(milestones: list, upcoming_events: list) -> list[str]:
    """マイルストーンをGoogle Tasksに追加"""
    added = []

    # 既存タスクのタイトル一覧（重複防止）
    existing = {t.get("title", "").strip() for t in get_pending_tasks()}

    for milestone in milestones:
        event_title = milestone.get("event_title", "")
        event_date_str = milestone.get("event_date", "")
        if not event_date_str:
            continue

        try:
            event_date = datetime.strptime(event_date_str, "%Y-%m-%d").date()
        except ValueError:
            continue

        for task_info in milestone.get("tasks", []):
            title = task_info.get("title", "").strip()
            days_before = task_info.get("days_before", 1)
            notes = task_info.get("notes", "")

            if not title or title in existing:
                continue

            due_date = event_date - timedelta(days=days_before)
            if due_date < datetime.now(TZ).date():
                due_date = datetime.now(TZ).date()

            full_notes = f"📅 {event_title}（{event_date_str}）の{days_before}日前タスク\n{notes}"

            try:
                tasks_ops.add_task(title, notes=full_notes)
                added.append(title)
                existing.add(title)
            except Exception as e:
                print(f"  タスク追加エラー: {title} → {e}", file=sys.stderr)

    return added


def print_report(report: dict, added_tasks: list):
    """レポートを表示"""
    today_str = datetime.now(TZ).strftime("%Y年%m月%d日")

    print("=" * 60)
    print(f"  🌅 おはようございます！{today_str}の朝レポート")
    print("=" * 60)

    print(f"\n{report.get('greeting', '')}\n")

    print("【📅 今日のスケジュール】")
    print(report.get("today_summary", ""))

    print(f"\n【🎯 今日のフォーカス】")
    print(report.get("focus", ""))

    if added_tasks:
        print(f"\n【✅ 新しく追加したマイルストーンタスク（{len(added_tasks)}件）】")
        for t in added_tasks:
            print(f"  + {t}")
    else:
        print("\n【✅ マイルストーン】新規タスクの追加はありませんでした。")

    print("\n" + "=" * 60)


def main():
    print("📡 カレンダーとタスクを取得中...")
    today_events = get_today_events()
    upcoming_events = get_upcoming_events(days=30)
    tasks = get_pending_tasks()

    print(f"  今日の予定: {len(today_events)}件")
    print(f"  今後30日の予定: {len(upcoming_events)}件")
    print(f"  未完了タスク: {len(tasks)}件")

    print("\n🤖 AIがレポートを作成中...")
    report = generate_morning_report(today_events, upcoming_events, tasks)

    print("📝 マイルストーンタスクをGoogle Tasksに追加中...")
    added_tasks = add_milestones_to_tasks(report.get("milestones", []), upcoming_events)

    print_report(report, added_tasks)


if __name__ == "__main__":
    main()
