from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import yaml
from dateutil import parser as date_parser
from zoneinfo import ZoneInfo

from googleapiclient.errors import HttpError

from secretary import calendar_ops, tasks_ops

_TZ = ZoneInfo("Asia/Tokyo")
MARKER = "secretary_deadline_v1"


@dataclass
class Rule:
    match_title_contains: str
    task_title: str
    before_event_hours: float
    reminder_minutes_before: list[int] | None = None


def _secretary_dir() -> Path:
    return Path(__file__).resolve().parent.parent


def default_rules_path() -> Path:
    return Path(os.environ.get("DEADLINE_RULES", _secretary_dir() / "deadline_rules.yaml"))


def load_rules(path: Path) -> tuple[dict[str, Any], list[Rule]]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    defaults = raw.get("defaults") or {}
    rows = raw.get("rules") or []
    rules: list[Rule] = []
    for row in rows:
        rules.append(
            Rule(
                match_title_contains=str(row["match_title_contains"]),
                task_title=str(row["task_title"]),
                before_event_hours=float(row["before_event_hours"]),
                reminder_minutes_before=row.get("reminder_minutes_before"),
            )
        )
    return defaults, rules


def build_deadline_description(anchor_id: str, task_key: str, anchor_summary: str, anchor_start: datetime) -> str:
    safe = (anchor_summary or "").replace("\n", " ").strip()
    return (
        f"{MARKER}\n"
        f"anchor_event_id:{anchor_id}\n"
        f"task_key:{task_key}\n"
        f"anchor_summary:{safe}\n"
        f"anchor_start:{anchor_start.isoformat()}\n"
    )


def parse_deadline_description(desc: str | None) -> dict[str, str] | None:
    if not desc or MARKER not in desc:
        return None
    out: dict[str, str] = {}
    for line in desc.splitlines():
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        k, v = k.strip(), v.strip()
        if k in ("anchor_event_id", "task_key", "anchor_summary", "anchor_start"):
            out[k] = v
    if "anchor_event_id" not in out or "task_key" not in out:
        return None
    return out


def parse_event_start(ev: dict[str, Any]) -> datetime | None:
    s = ev.get("start") or {}
    if "dateTime" in s:
        return date_parser.isoparse(s["dateTime"])
    if "date" in s:
        d = s["date"]
        return datetime.fromisoformat(d).replace(tzinfo=_TZ)
    return None


def _fmt_cal(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=_TZ)
    return dt.isoformat()


def _reminders(minutes: list[int]) -> dict[str, Any]:
    return {
        "useDefault": False,
        "overrides": [{"method": "popup", "minutes": int(m)} for m in minutes],
    }


def _sanitize_event_body(body: dict[str, Any]) -> dict[str, Any]:
    drop = {
        "htmlLink",
        "hangoutLink",
        "etag",
        "iCalUID",
        "created",
        "updated",
        "creator",
        "organizer",
        "conferenceData",
    }
    return {k: v for k, v in body.items() if k not in drop}


def run(
    *,
    config_path: Path | None = None,
    horizon_days: int = 45,
    calendar_id: str = "primary",
    dry_run: bool = False,
) -> dict[str, int]:
    path = config_path or default_rules_path()
    if not path.is_file():
        raise FileNotFoundError(f"ルールファイルがありません: {path}")

    defaults, rules = load_rules(path)
    default_reminders: list[int] = list(
        defaults.get("reminder_minutes_before") or [1440, 180, 0]
    )

    from datetime import timezone

    now = datetime.now(timezone.utc)
    time_min = calendar_ops.utc_z(now - timedelta(days=1))
    time_max = calendar_ops.utc_z(now + timedelta(days=horizon_days))
    items = calendar_ops.list_events_range(
        time_min=time_min,
        time_max=time_max,
        calendar_id=calendar_id,
        max_results=500,
    )

    deadline_events: list[dict[str, Any]] = []
    anchor_events: list[dict[str, Any]] = []
    for ev in items:
        if parse_deadline_description(ev.get("description")):
            deadline_events.append(ev)
        else:
            anchor_events.append(ev)

    deadline_map: dict[tuple[str, str], dict[str, Any]] = {}
    for d in deadline_events:
        meta = parse_deadline_description(d.get("description"))
        if meta:
            deadline_map[(meta["anchor_event_id"], meta["task_key"])] = d

    stats = {"created": 0, "updated": 0, "deleted": 0, "skipped_done": 0, "skipped_past": 0}
    deleted_ids: set[str] = set()

    now_local = datetime.now(_TZ)

    for anchor in anchor_events:
        summary = anchor.get("summary") or ""
        if summary.startswith("【締切】"):
            continue

        st = parse_event_start(anchor)
        if st is None:
            continue
        if st.tzinfo is None:
            st = st.replace(tzinfo=_TZ)
        if st < now_local:
            continue

        aid = anchor.get("id") or ""
        if not aid:
            continue

        for rule in rules:
            if rule.match_title_contains not in summary:
                continue

            task_key = rule.task_title
            linked = tasks_ops.task_for_deadline_link(aid, task_key)
            done = linked is not None and linked.get("status") == "completed"
            key = (aid, task_key)

            if done:
                stats["skipped_done"] += 1
                if key in deadline_map:
                    eid = deadline_map[key]["id"]
                    if not dry_run:
                        calendar_ops.delete_event(eid, calendar_id=calendar_id)
                        stats["deleted"] += 1
                        deleted_ids.add(eid)
                continue

            deadline_dt = st - timedelta(hours=rule.before_event_hours)
            end_dt = deadline_dt + timedelta(minutes=30)
            rem = rule.reminder_minutes_before or default_reminders
            desc = build_deadline_description(aid, task_key, summary, st)
            cal_summary = f"【締切】{rule.task_title}"

            if not dry_run:
                tasks_ops.ensure_open_prep_task(
                    rule.task_title,
                    anchor_event_id=aid,
                    task_key=task_key,
                    anchor_summary=summary,
                )

            if key in deadline_map:
                eid = deadline_map[key]["id"]
                if not dry_run:
                    full = calendar_ops.get_event(eid, calendar_id=calendar_id)
                    full["summary"] = cal_summary
                    full["description"] = desc
                    full["start"] = {"dateTime": _fmt_cal(deadline_dt), "timeZone": "Asia/Tokyo"}
                    full["end"] = {"dateTime": _fmt_cal(end_dt), "timeZone": "Asia/Tokyo"}
                    full["reminders"] = _reminders(rem)
                    body = _sanitize_event_body(full)
                    calendar_ops.update_event(eid, body, calendar_id=calendar_id)
                stats["updated"] += 1
            else:
                if not dry_run:
                    calendar_ops.create_event(
                        cal_summary,
                        start=deadline_dt,
                        end=end_dt,
                        duration_minutes=30,
                        description=desc,
                        calendar_id=calendar_id,
                        reminder_minutes_before=rem,
                    )
                stats["created"] += 1

    for d in deadline_events:
        eid = d.get("id") or ""
        if not eid or eid in deleted_ids:
            continue
        meta = parse_deadline_description(d.get("description"))
        if not meta:
            continue
        aid = meta["anchor_event_id"]
        tk = meta["task_key"]
        try:
            anchor = calendar_ops.get_event(aid, calendar_id=calendar_id)
        except HttpError as err:
            st = getattr(err.resp, "status", None) if err.resp is not None else None
            if st == 404 and not dry_run:
                calendar_ops.delete_event(eid, calendar_id=calendar_id)
                stats["deleted"] += 1
                deleted_ids.add(eid)
            continue
        except Exception:
            continue

        ast = parse_event_start(anchor)
        if ast is None:
            continue
        if ast.tzinfo is None:
            ast = ast.replace(tzinfo=_TZ)
        if ast < now_local:
            if not dry_run:
                calendar_ops.delete_event(eid, calendar_id=calendar_id)
                stats["deleted"] += 1
                deleted_ids.add(eid)
            continue

        linked = tasks_ops.task_for_deadline_link(aid, tk)
        if linked and linked.get("status") == "completed" and not dry_run:
            calendar_ops.delete_event(eid, calendar_id=calendar_id)
            stats["deleted"] += 1
            deleted_ids.add(eid)
            continue

        sm = anchor.get("summary") or ""
        rule_still = any(r.task_title == tk and r.match_title_contains in sm for r in rules)
        if not rule_still and not dry_run:
            calendar_ops.delete_event(eid, calendar_id=calendar_id)
            stats["deleted"] += 1
            deleted_ids.add(eid)

    return stats
