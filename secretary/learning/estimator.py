from __future__ import annotations

import statistics
from pathlib import Path

from secretary.learning.tracker import TaskTracker

_MIN_SAMPLES = 5


class TimeEstimator:
    def __init__(self, tracker: TaskTracker | None = None) -> None:
        self.tracker = tracker or TaskTracker()

    def correction_factor(self, category: str) -> float:
        history = self.tracker.load_history()
        ratios = [
            r["actual_minutes"] / r["estimated_minutes"]
            for r in history
            if r.get("category") == category
            and r.get("estimated_minutes", 0) > 0
            and r.get("actual_minutes", 0) > 0
        ]
        if len(ratios) < _MIN_SAMPLES:
            return 1.0
        return statistics.median(ratios)

    def estimate(self, category: str, base_minutes: int) -> int:
        return max(1, round(base_minutes * self.correction_factor(category)))
