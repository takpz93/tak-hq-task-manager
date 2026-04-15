from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo

from googleapiclient.discovery import build

from secretary.auth import get_credentials

_TZ = ZoneInfo("Asia/Tokyo")


def _service():
    return build("calendar", "v3", credentials=get_credentials(), cache_discovery=False)


def utc_z(dt: datetime) -> str:
    from datetime import timezone

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def list_events(
    *,
    days: int = 7,
    days_past: int = 0,
    calendar_id: str = "primary",
    max_results: int = 50,
) -> list[dict[str, Any]]:
    from datetime import timezone

    now = datetime.now(timezone.utc)
    time_min = utc_z(now - timedelta(days=days_past))
    time_max = utc_z(now + timedelta(days=days))
    return list_events_range(
        time_min=time_min,
        time_max=time_max,
        calendar_id=calendar_id,
        max_results=max_results,
    )


def list_events_range(
    *,
    time_min: str,
    time_max: str,
    calendar_id: str = "primary",
    max_results: int = 500,
) -> list[dict[str, Any]]:
    svc = _service()
    out = (
        svc.events()
        .list(
            calendarId=calendar_id,
            timeMin=time_min,
            timeMax=time_max,
            maxResults=max_results,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    return out.get("items", [])


def create_event(
    summary: str,
    *,
    start: datetime,
    end: datetime | None = None,
    duration_minutes: int = 60,
    description: str | None = None,
    calendar_id: str = "primary",
    timezone_name: str = "Asia/Tokyo",
    reminder_minutes_before: list[int] | None = None,
    recurrence: str | None = None,
    all_day: bool = False,
) -> dict[str, Any]:
    """
    recurrence に RRULE 文字列を渡すと繰り返しイベントになる。
    all_day=True のとき終日イベントとして登録する。
    """
    from datetime import date as _date

    if all_day:
        date_str = start.strftime("%Y-%m-%d") if isinstance(start, datetime) else str(start)
        # 終日イベントは翌日がend
        from datetime import date as _date2
        import datetime as _dt_mod
        d = _date2(start.year, start.month, start.day) if isinstance(start, datetime) else start
        next_d = d + timedelta(days=1)
        body: dict[str, Any] = {
            "summary": summary,
            "start": {"date": date_str},
            "end": {"date": next_d.strftime("%Y-%m-%d")},
        }
    else:
        if end is None:
            end = start + timedelta(minutes=duration_minutes)

        def fmt(dt: datetime) -> str:
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=_TZ)
            return dt.isoformat()

        body = {
            "summary": summary,
            "start": {"dateTime": fmt(start), "timeZone": timezone_name},
            "end": {"dateTime": fmt(end), "timeZone": timezone_name},
        }

    if description:
        body["description"] = description
    if not all_day and reminder_minutes_before is not None:
        body["reminders"] = {
            "useDefault": False,
            "overrides": [{"method": "popup", "minutes": int(m)} for m in reminder_minutes_before],
        }
    if recurrence:
        body["recurrence"] = [recurrence]

    svc = _service()
    return svc.events().insert(calendarId=calendar_id, body=body).execute()


def update_event(
    event_id: str,
    body: dict[str, Any],
    *,
    calendar_id: str = "primary",
) -> dict[str, Any]:
    svc = _service()
    return svc.events().update(calendarId=calendar_id, eventId=event_id, body=body).execute()


def get_event(event_id: str, *, calendar_id: str = "primary") -> dict[str, Any]:
    svc = _service()
    return svc.events().get(calendarId=calendar_id, eventId=event_id).execute()


def delete_event(event_id: str, *, calendar_id: str = "primary") -> None:
    svc = _service()
    svc.events().delete(calendarId=calendar_id, eventId=event_id).execute()
