from datetime import datetime

from pydantic import BaseModel, Field

from app.models.submission import InputType


class SubmissionCreate(BaseModel):
    problem_id: str
    input_type: InputType
    content: str = Field(..., description="Typed math step or image payload/path")


class SubmissionResponse(BaseModel):
    id: str
    student_id: str
    problem_id: str
    input_type: InputType
    content: str
    created_at: datetime


class AttemptAnalyzeRequest(BaseModel):
    submission_id: str
    step_index: int = Field(..., ge=0)
    step_text: str
    expected_step_text: str | None = None


class AttemptResponse(BaseModel):
    id: str
    submission_id: str
    step_index: int
    is_correct: bool
    error_type: str | None
    concept_tag: str | None
    confidence: float
    hint_level: int
    created_at: datetime


class HintRequest(BaseModel):
    problem_id: str
    step_text: str
    error_type: str | None = None
    concept_tag: str | None = None
    attempt_count_for_problem: int = Field(default=1, ge=1)


class HintResponse(BaseModel):
    hint: str
    hint_level: int
    source: str


class StudentProgressResponse(BaseModel):
    student_id: str
    total_attempts: int
    correct_attempts: int
    repeated_misconceptions: dict[str, int]


class TeacherDashboardResponse(BaseModel):
    teacher_id: str
    class_summary: dict
    student_rows: list[dict]
