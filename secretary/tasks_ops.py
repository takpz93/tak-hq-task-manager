from __future__ import annotations

from typing import Any

from googleapiclient.discovery import build

from secretary.auth import get_credentials


def _service():
    return build("tasks", "v1", credentials=get_credentials(), cache_discovery=False)


def list_all_tasks(*, tasklist_id: str | None = None) -> list[dict[str, Any]]:
    tl = tasklist_id or ensure_default_list_id()
    svc = _service()
    items: list[dict[str, Any]] = []
    page_token: str | None = None
    while True:
        kwargs: dict[str, Any] = {
            "tasklist": tl,
            "showCompleted": True,
            "showHidden": True,
            "maxResults": 100,
        }
        if page_token:
            kwargs["pageToken"] = page_token
        out = svc.tasks().list(**kwargs).execute()
        items.extend(out.get("items", []))
        page_token = out.get("nextPageToken")
        if not page_token:
            break
    return items


def task_for_deadline_link(anchor_event_id: str, task_key: str) -> dict[str, Any] | None:
    a = f"secretary_anchor:{anchor_event_id}"
    k = f"task_key:{task_key}"
    for t in list_all_tasks():
        notes = t.get("notes") or ""
        if a in notes and k in notes:
            return t
    return None


def ensure_open_prep_task(
    title: str,
    *,
    anchor_event_id: str,
    task_key: str,
    anchor_summary: str,
    tasklist_id: str | None = None,
) -> dict[str, Any]:
    existing = task_for_deadline_link(anchor_event_id, task_key)
    if existing is not None:
        return existing
    tl = tasklist_id or ensure_default_list_id()
    notes = (
        f"secretary_anchor:{anchor_event_id}\n"
        f"task_key:{task_key}\n"
        f"紐づく予定: {anchor_summary}"
    )
    body: dict[str, Any] = {"title": title, "notes": notes}
    return _service().tasks().insert(tasklist=tl, body=body).execute()


def list_tasklists() -> list[dict[str, Any]]:
    out = _service().tasklists().list().execute()
    return out.get("items", [])


def ensure_default_list_id() -> str:
    lists = list_tasklists()
    if not lists:
        raise RuntimeError("タスクリストがありません。Google Tasks でリストを作成してください。")
    for t in lists:
        if t.get("title") == "My Tasks" or t.get("id") == "@default":
            return t["id"]
    return lists[0]["id"]


def list_tasks(*, tasklist_id: str | None = None, show_completed: bool = False) -> list[dict[str, Any]]:
    tl = tasklist_id or ensure_default_list_id()
    out = (
        _service()
        .tasks()
        .list(tasklist=tl, showCompleted=show_completed, showHidden=show_completed)
        .execute()
    )
    return out.get("items", [])


def get_task(task_id: str, *, tasklist_id: str | None = None) -> dict[str, Any]:
    tl = tasklist_id or ensure_default_list_id()
    return _service().tasks().get(tasklist=tl, task=task_id).execute()


def add_task(
    title: str,
    *,
    notes: str | None = None,
    due: str | None = None,
    tasklist_id: str | None = None,
) -> dict[str, Any]:
    """due は "2026-04-13T00:00:00.000Z" 形式の RFC 3339 文字列（時刻は無視）。"""
    tl = tasklist_id or ensure_default_list_id()
    body: dict[str, Any] = {"title": title}
    if notes:
        body["notes"] = notes
    if due:
        body["due"] = due
    return _service().tasks().insert(tasklist=tl, body=body).execute()


def update_task(
    task_id: str,
    *,
    title: str | None = None,
    notes: str | None = None,
    due: str | None = None,
    status: str | None = None,
    tasklist_id: str | None = None,
) -> dict[str, Any]:
    """指定フィールドのみ更新する（patch）。"""
    tl = tasklist_id or ensure_default_list_id()
    body: dict[str, Any] = {}
    if title  is not None: body["title"]  = title
    if notes  is not None: body["notes"]  = notes
    if due    is not None: body["due"]    = due
    if status is not None: body["status"] = status
    return _service().tasks().patch(tasklist=tl, task=task_id, body=body).execute()


def complete_task(task_id: str, *, tasklist_id: str | None = None) -> dict[str, Any]:
    tl = tasklist_id or ensure_default_list_id()
    return (
        _service()
        .tasks()
        .patch(tasklist=tl, task=task_id, body={"status": "completed"})
        .execute()
    )


def delete_task(task_id: str, *, tasklist_id: str | None = None) -> None:
    tl = tasklist_id or ensure_default_list_id()
    _service().tasks().delete(tasklist=tl, task=task_id).execute()
