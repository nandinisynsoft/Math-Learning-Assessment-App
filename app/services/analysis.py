from dataclasses import dataclass


@dataclass
class AnalysisOutput:
    is_correct: bool
    error_type: str | None
    concept_tag: str | None
    confidence: float


class StepAnalyzer:
    @staticmethod
    def _normalize(text: str) -> str:
        return "".join(text.lower().split())

    def analyze(self, step_text: str, expected_step_text: str | None = None) -> AnalysisOutput:
        normalized = self._normalize(step_text)

        if expected_step_text and normalized == self._normalize(expected_step_text):
            return AnalysisOutput(True, None, None, 0.98)

        if "--" in normalized or "+-" in normalized:
            return AnalysisOutput(False, "sign_error", "integer_sign_rules", 0.84)
        if "/0" in normalized:
            return AnalysisOutput(False, "invalid_operation", "division_by_zero", 0.96)
        if "=" not in step_text:
            return AnalysisOutput(False, "incomplete_step", "equation_structure", 0.8)
        if "x=" in normalized and any(tok in normalized for tok in ["+", "-", "*", "/"]):
            return AnalysisOutput(False, "premature_final", "multi_step_solving", 0.74)

        return AnalysisOutput(True, None, None, 0.6)


analyzer = StepAnalyzer()
