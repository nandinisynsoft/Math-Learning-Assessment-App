from datetime import datetime
from uuid import uuid4

from fastapi import FastAPI, HTTPException

from app.models import (
    AttemptAnalyzeRequest,
    AttemptResult,
    HintRequest,
    HintResponse,
    StudentProgressResponse,
    SubmissionCreate,
    TeacherDashboardResponse,
)
from app.services.analysis import analyzer
from app.services.ocr import ocr_service
from app.services.hints import hint_service
from app.services.storage import store

app = FastAPI(title="Math Learning & Assessment API", version="0.1.0")


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok"}


@app.post("/api/v1/submissions")
def create_submission(payload: SubmissionCreate) -> dict:
    submission_id = str(uuid4())
    content = payload.content

    if payload.input_type.value == "image":
        content = ocr_service.extract_text(payload.content)

    submission = {
        "id": submission_id,
        "student_id": payload.student_id,
        "problem_id": payload.problem_id,
        "input_type": payload.input_type.value,
        "content": content,
        "created_at": datetime.utcnow().isoformat(),
    }
    return store.save_submission(submission)


@app.post("/api/v1/attempts/analyze", response_model=AttemptResult)
def analyze_attempt(payload: AttemptAnalyzeRequest) -> AttemptResult:
    submission = store.submissions.get(payload.submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="submission_id not found")

    result = analyzer.analyze(payload.step_text, payload.expected_step_text)

    attempts_for_problem = store.attempts_for_problem(submission["student_id"], submission["problem_id"])
    hint_level = min(len(attempts_for_problem) + 1, 3)

    attempt = {
        "submission_id": payload.submission_id,
        "student_id": submission["student_id"],
        "problem_id": submission["problem_id"],
        "step_index": payload.step_index,
        "is_correct": result.is_correct,
        "error_type": result.error_type,
        "concept_tag": result.concept_tag,
        "confidence": result.confidence,
        "hint_level": hint_level,
        "created_at": datetime.utcnow(),
    }
    store.save_attempt(attempt)
    return AttemptResult(**attempt)


@app.post("/api/v1/hints/generate", response_model=HintResponse)
def generate_hint(payload: HintRequest) -> HintResponse:
    attempts = store.attempts_for_problem(payload.student_id, payload.problem_id)
    attempt_count = max(payload.attempt_count_for_problem, len(attempts))
    hint, hint_level, source = hint_service.generate(
        payload.step_text,
        payload.error_type,
        payload.concept_tag,
        attempt_count,
    )
    return HintResponse(hint=hint, hint_level=hint_level, source=source)


@app.get("/api/v1/students/{student_id}/progress", response_model=StudentProgressResponse)
def student_progress(student_id: str) -> StudentProgressResponse:
    attempts = store.attempts_for_student(student_id)
    return StudentProgressResponse(
        student_id=student_id,
        total_attempts=len(attempts),
        correct_attempts=sum(1 for a in attempts if a["is_correct"]),
        repeated_misconceptions=dict(store.student_concepts.get(student_id, {})),
    )


@app.get("/api/v1/teachers/{teacher_id}/dashboard", response_model=TeacherDashboardResponse)
def teacher_dashboard(teacher_id: str) -> TeacherDashboardResponse:
    return TeacherDashboardResponse(**store.teacher_dashboard(teacher_id))
