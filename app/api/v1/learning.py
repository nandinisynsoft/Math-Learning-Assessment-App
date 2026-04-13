from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.learning import (
    AttemptAnalyzeRequest,
    AttemptResponse,
    HintRequest,
    HintResponse,
    StudentProgressResponse,
    SubmissionCreate,
    SubmissionResponse,
    TeacherDashboardResponse,
)
from app.services.learning_service import learning_service

router = APIRouter(prefix="/learning", tags=["learning"])


@router.post("/submissions", response_model=SubmissionResponse, status_code=status.HTTP_201_CREATED)
def create_submission(
    payload: SubmissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SubmissionResponse:
    if current_user.role != UserRole.student:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only students can create submissions")

    submission = learning_service.create_submission(
        db,
        student_id=current_user.id,
        problem_id=payload.problem_id,
        input_type=payload.input_type,
        content=payload.content,
    )
    return SubmissionResponse(
        id=submission.id,
        student_id=submission.student_id,
        problem_id=submission.problem_id,
        input_type=submission.input_type,
        content=submission.content,
        created_at=submission.created_at,
    )


@router.post("/attempts/analyze", response_model=AttemptResponse)
def analyze_attempt(
    payload: AttemptAnalyzeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AttemptResponse:
    if current_user.role != UserRole.student:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only students can analyze attempts")

    try:
        attempt = learning_service.analyze_attempt(
            db,
            student_id=current_user.id,
            submission_id=payload.submission_id,
            step_index=payload.step_index,
            step_text=payload.step_text,
            expected_step_text=payload.expected_step_text,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return AttemptResponse(
        id=attempt.id,
        submission_id=attempt.submission_id,
        step_index=attempt.step_index,
        is_correct=attempt.is_correct,
        error_type=attempt.error_type,
        concept_tag=attempt.concept_tag,
        confidence=attempt.confidence,
        hint_level=attempt.hint_level,
        created_at=attempt.created_at,
    )


@router.post("/hints/generate", response_model=HintResponse)
def generate_hint(
    payload: HintRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> HintResponse:
    if current_user.role != UserRole.student:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only students can request hints")

    hint, hint_level, source = learning_service.generate_hint(
        db,
        student_id=current_user.id,
        problem_id=payload.problem_id,
        step_text=payload.step_text,
        error_type=payload.error_type,
        concept_tag=payload.concept_tag,
        attempt_count_for_problem=payload.attempt_count_for_problem,
    )
    return HintResponse(hint=hint, hint_level=hint_level, source=source)


@router.get("/students/me/progress", response_model=StudentProgressResponse)
def student_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StudentProgressResponse:
    if current_user.role != UserRole.student:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only students can view student progress")

    return StudentProgressResponse(**learning_service.student_progress(db, current_user.id))


@router.get("/teachers/me/dashboard", response_model=TeacherDashboardResponse)
def teacher_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TeacherDashboardResponse:
    if current_user.role != UserRole.teacher:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only teachers can view dashboards")

    return TeacherDashboardResponse(**learning_service.teacher_dashboard(db, current_user.id))
