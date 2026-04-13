from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class InputType(str, Enum):
    text = "text"
    image = "image"


class SubmissionCreate(BaseModel):
    student_id: str
    problem_id: str
    input_type: InputType
    content: str = Field(..., description="Typed math step or OCR text from image")


class AttemptAnalyzeRequest(BaseModel):
    submission_id: str
    step_index: int = Field(..., ge=0)
    step_text: str
    expected_step_text: Optional[str] = None


class AttemptResult(BaseModel):
    submission_id: str
    step_index: int
    is_correct: bool
    error_type: Optional[str] = None
    concept_tag: Optional[str] = None
    confidence: float = Field(..., ge=0.0, le=1.0)
    hint_level: int = Field(default=1, ge=1, le=3)
    created_at: datetime


class HintRequest(BaseModel):
    student_id: str
    problem_id: str
    step_text: str
    error_type: Optional[str] = None
    concept_tag: Optional[str] = None
    attempt_count_for_problem: int = Field(default=1, ge=1)


class HintResponse(BaseModel):
    hint: str
    hint_level: int
    source: str = Field(description="heuristic or gemini")


class StudentProgressResponse(BaseModel):
    student_id: str
    total_attempts: int
    correct_attempts: int
    repeated_misconceptions: dict[str, int]


class TeacherDashboardResponse(BaseModel):
    teacher_id: str
    class_summary: dict
    student_rows: list[dict]
