from dataclasses import dataclass


@dataclass
class AnalysisOutput:
    is_correct: bool
    error_type: str | None
    concept_tag: str | None
    confidence: float


class StepAnalyzer:
    """
    Lightweight MVP analyzer:
    - If expected step provided, exact-normalized match check.
    - Heuristic misconception classification for common math mistakes.
    """

    @staticmethod
    def _normalize(text: str) -> str:
        return "".join(text.lower().split())

    def analyze(self, step_text: str, expected_step_text: str | None = None) -> AnalysisOutput:
        normalized = self._normalize(step_text)

        if expected_step_text and normalized == self._normalize(expected_step_text):
            return AnalysisOutput(True, None, None, 0.98)

        if expected_step_text:
            expected = self._normalize(expected_step_text)
            if normalized == expected:
                return AnalysisOutput(True, None, None, 0.98)

        # Heuristics for concept tagging (seed for future ML model)
        if "--" in normalized or "+-" in normalized:
            return AnalysisOutput(False, "sign_error", "integer_sign_rules", 0.84)
        if "/0" in normalized:
            return AnalysisOutput(False, "invalid_operation", "division_by_zero", 0.96)
        if "=" not in step_text:
            return AnalysisOutput(False, "incomplete_step", "equation_structure", 0.8)
        if "x=" in normalized and any(tok in normalized for tok in ["+", "-", "*", "/"]):
            return AnalysisOutput(False, "premature_final", "multi_step_solving", 0.74)

            # likely intermediate step claimed as final answer
            return AnalysisOutput(False, "premature_final", "multi_step_solving", 0.74)

        # If no signal, soft-correctness for MVP.
        return AnalysisOutput(True, None, None, 0.6)


analyzer = StepAnalyzer()
