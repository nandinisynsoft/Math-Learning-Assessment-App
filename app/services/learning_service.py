from collections import Counter
from datetime import datetime
from uuid import uuid4

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.attempt import Attempt
from app.models.submission import InputType, Submission
from app.services.analysis import analyzer
from app.services.hints import hint_service
from app.services.ocr import ocr_service


class LearningService:
    def create_submission(self, db: Session, student_id: str, problem_id: str, input_type: InputType, content: str) -> Submission:
        processed_content = content
        if input_type == InputType.image:
            processed_content = ocr_service.extract_text(content)

        submission = Submission(
            id=str(uuid4()),
            student_id=student_id,
            problem_id=problem_id,
            input_type=input_type,
            content=processed_content,
            created_at=datetime.utcnow(),
        )
        db.add(submission)
        db.commit()
        db.refresh(submission)
        return submission

    def analyze_attempt(self, db: Session, student_id: str, submission_id: str, step_index: int, step_text: str, expected_step_text: str | None) -> Attempt:
        submission = db.query(Submission).filter(Submission.id == submission_id, Submission.student_id == student_id).first()
        if not submission:
            raise ValueError("Submission not found")

        result = analyzer.analyze(step_text, expected_step_text)

        prior_attempts = (
            db.query(func.count(Attempt.id))
            .filter(Attempt.student_id == student_id, Attempt.problem_id == submission.problem_id)
            .scalar()
        ) or 0
        hint_level = min(prior_attempts + 1, 3)

        attempt = Attempt(
            id=str(uuid4()),
            submission_id=submission_id,
            student_id=student_id,
            problem_id=submission.problem_id,
            step_index=step_index,
            is_correct=result.is_correct,
            error_type=result.error_type,
            concept_tag=result.concept_tag,
            confidence=result.confidence,
            hint_level=hint_level,
            created_at=datetime.utcnow(),
        )
        db.add(attempt)
        db.commit()
        db.refresh(attempt)
        return attempt

    def generate_hint(self, db: Session, student_id: str, problem_id: str, step_text: str, error_type: str | None, concept_tag: str | None, attempt_count_for_problem: int) -> tuple[str, int, str]:
        attempts = (
            db.query(func.count(Attempt.id))
            .filter(Attempt.student_id == student_id, Attempt.problem_id == problem_id)
            .scalar()
        ) or 0
        attempt_count = max(attempt_count_for_problem, attempts)
        return hint_service.generate(step_text, error_type, concept_tag, attempt_count)

    def student_progress(self, db: Session, student_id: str) -> dict:
        attempts = db.query(Attempt).filter(Attempt.student_id == student_id).all()
        repeated = Counter(a.concept_tag for a in attempts if a.concept_tag)
        return {
            "student_id": student_id,
            "total_attempts": len(attempts),
            "correct_attempts": sum(1 for a in attempts if a.is_correct),
            "repeated_misconceptions": dict(repeated),
        }

    def teacher_dashboard(self, db: Session, teacher_id: str) -> dict:
        students = [row[0] for row in db.query(Attempt.student_id).distinct().all()]
        rows = []
        for sid in students:
            attempts = db.query(Attempt).filter(Attempt.student_id == sid).all()
            top = Counter(a.concept_tag for a in attempts if a.concept_tag).most_common(3)
            total = len(attempts)
            correct = sum(1 for a in attempts if a.is_correct)
            rows.append(
                {
                    "student_id": sid,
                    "attempts": total,
                    "accuracy": round(correct / total, 2) if total else 0.0,
                    "top_misconceptions": top,
                }
            )

        return {
            "teacher_id": teacher_id,
            "class_summary": {
                "students": len(students),
                "total_attempts": db.query(func.count(Attempt.id)).scalar() or 0,
                "generated_at": datetime.utcnow().isoformat(),
            },
            "student_rows": rows,
        }


learning_service = LearningService()
