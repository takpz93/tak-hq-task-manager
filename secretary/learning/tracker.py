from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

_DEFAULT_PATH = Path(__file__).resolve().parents[3] / "data" / "task_history.json"


class TaskTracker:
    def __init__(self, data_path: Path = _DEFAULT_PATH) -> None:
        self.data_path = data_path
        self.data_path.parent.mkdir(parents=True, exist_ok=True)

    def record_completion(
        self,
        task_title: str,
        category: str,
        estimated_minutes: int,
        actual_minutes: int,
        goal_id: str = "",
    ) -> None:
        history = self.load_history()
        history.append(
            {
                "recorded_at": datetime.now(timezone.utc).isoformat(),
                "task_title": task_title,
                "category": category,
                "estimated_minutes": estimated_minutes,
                "actual_minutes": actual_minutes,
                "goal_id": goal_id,
            }
        )
        self.data_path.write_text(
            json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def load_history(self) -> list[dict]:
        if not self.data_path.exists():
            return []
        try:
            return json.loads(self.data_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []
