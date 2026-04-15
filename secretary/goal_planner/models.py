from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from uuid import uuid4


@dataclass
class SubTask:
    title: str
    estimated_minutes: int
    category: str  # "research" / "writing" / "review" / "preparation" / "other"
    order: int
    calendar_event_id: str | None = None


@dataclass
class Goal:
    title: str
    deadline: date
    daily_minutes: int
    parallel_projects: list[str]
    priority: int  # 1=最高優先
    sub_tasks: list[SubTask] = field(default_factory=list)
    goal_id: str = field(default_factory=lambda: str(uuid4()))
