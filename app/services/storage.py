from collections import defaultdict
from datetime import datetime
from typing import Any


class InMemoryStore:
    """MVP storage to keep project runnable without external DB."""

    def __init__(self) -> None:
        self.submissions: dict[str, dict[str, Any]] = {}
        self.attempts: list[dict[str, Any]] = []
        self.student_concepts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    def save_submission(self, submission: dict[str, Any]) -> dict[str, Any]:
        self.submissions[submission["id"]] = submission
        return submission

    def save_attempt(self, attempt: dict[str, Any]) -> dict[str, Any]:
        self.attempts.append(attempt)
        concept = attempt.get("concept_tag")
        if concept:
            self.student_concepts[attempt["student_id"]][concept] += 1
        return attempt

    def attempts_for_student(self, student_id: str) -> list[dict[str, Any]]:
        return [a for a in self.attempts if a["student_id"] == student_id]

    def attempts_for_problem(self, student_id: str, problem_id: str) -> list[dict[str, Any]]:
        return [
            a
            for a in self.attempts
            if a["student_id"] == student_id and a["problem_id"] == problem_id
        ]

    def teacher_dashboard(self, teacher_id: str) -> dict[str, Any]:
        # In MVP, we return aggregate for all students.
        student_ids = sorted({a["student_id"] for a in self.attempts})
        rows = []
        for sid in student_ids:
            attempts = self.attempts_for_student(sid)
            total = len(attempts)
            correct = sum(1 for a in attempts if a["is_correct"])
            rows.append(
                {
                    "student_id": sid,
                    "attempts": total,
                    "accuracy": round(correct / total, 2) if total else 0,
                    "top_misconceptions": sorted(
                        self.student_concepts[sid].items(),
                        key=lambda x: x[1],
                        reverse=True,
                    )[:3],
                }
            )

        return {
            "teacher_id": teacher_id,
            "class_summary": {
                "students": len(student_ids),
                "total_attempts": len(self.attempts),
                "last_updated": datetime.utcnow().isoformat(),
            },
            "student_rows": rows,
        }


store = InMemoryStore()
