from __future__ import annotations

import json
import logging
import re
from typing import Any

from secretary.goal_planner.models import Goal, SubTask
from secretary.learning.estimator import TimeEstimator

logger = logging.getLogger(__name__)

_FALLBACK_TEMPLATES: dict[str, list[dict[str, Any]]] = {
    "default": [
        {"title": "要件・目標の整理", "estimated_minutes": 30, "category": "research"},
        {"title": "情報収集・リサーチ", "estimated_minutes": 60, "category": "research"},
        {"title": "計画・アウトライン作成", "estimated_minutes": 45, "category": "writing"},
        {"title": "実作業（メイン）", "estimated_minutes": 90, "category": "writing"},
        {"title": "中間レビュー・修正", "estimated_minutes": 30, "category": "review"},
        {"title": "最終確認・仕上げ", "estimated_minutes": 30, "category": "review"},
    ]
}


class TaskDecomposer:
    def __init__(self, estimator: TimeEstimator | None = None) -> None:
        self.estimator = estimator or TimeEstimator()

    def decompose(self, goal: Goal) -> list[SubTask]:
        try:
            import anthropic
            tasks = self._decompose_with_claude(goal)
        except Exception as e:
            logger.warning("Claude API失敗、フォールバックを使用: %s", e)
            tasks = self._fallback_tasks(goal)

        return self._apply_learning_estimates(tasks)

    def _decompose_with_claude(self, goal: Goal) -> list[SubTask]:
        import anthropic

        prompt = self._build_prompt(goal)
        client = anthropic.Anthropic()
        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )
        return self._parse_response(response.content[0].text)

    def _build_prompt(self, goal: Goal) -> str:
        parallel = "、".join(goal.parallel_projects) if goal.parallel_projects else "なし"
        return f"""以下の目標を達成するためのサブタスクをできるだけ細かく分解してください。

目標: {goal.title}
期限: {goal.deadline}
1日に使える時間: {goal.daily_minutes}分
優先度: {goal.priority}（1=最高）
並行プロジェクト: {parallel}

以下のJSON形式のみで返してください（説明文は不要）：

```json
[
  {{
    "title": "タスク名（具体的で行動できる内容）",
    "estimated_minutes": 60,
    "category": "research|writing|review|preparation|other のいずれか",
    "order": 1
  }}
]
```

ルール：
- タスクは実際に行動できる粒度まで細かく分解する（1タスクは15〜120分が目安）
- orderは実行順序（1から始まる整数）
- 期限と1日の利用可能時間を考慮してタスク数を調整する
"""

    def _parse_response(self, text: str) -> list[SubTask]:
        match = re.search(r"```(?:json)?\n([\s\S]*?)\n```", text)
        raw = match.group(1) if match else text
        data: list[dict] = json.loads(raw)
        return [
            SubTask(
                title=item["title"],
                estimated_minutes=int(item.get("estimated_minutes", 60)),
                category=item.get("category", "other"),
                order=int(item.get("order", i + 1)),
            )
            for i, item in enumerate(data)
        ]

    def _fallback_tasks(self, goal: Goal) -> list[SubTask]:
        templates = _FALLBACK_TEMPLATES["default"]
        return [
            SubTask(
                title=t["title"],
                estimated_minutes=t["estimated_minutes"],
                category=t["category"],
                order=i + 1,
            )
            for i, t in enumerate(templates)
        ]

    def _apply_learning_estimates(self, tasks: list[SubTask]) -> list[SubTask]:
        for task in tasks:
            task.estimated_minutes = self.estimator.estimate(
                task.category, task.estimated_minutes
            )
        return tasks
