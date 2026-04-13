import os

import httpx


class HintService:
    def __init__(self) -> None:
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    @staticmethod
    def _hint_level(attempt_count: int) -> int:
        if attempt_count <= 1:
            return 1
        if attempt_count <= 3:
            return 2
        return 3

    def _heuristic_hint(self, step_text: str, error_type: str | None, concept_tag: str | None, hint_level: int) -> str:
        if error_type == "sign_error":
            return "Check how negative signs combine in this step. What does subtracting a negative become?"
        if error_type == "incomplete_step":
            return "Try writing the full equation transformation for this step, including both sides of '='."
        if error_type == "premature_final":
            return "You're close. Before finalizing x, isolate the variable by undoing remaining operations one at a time."

        if hint_level == 1:
            return "What rule are you applying in this step? State it, then re-check your transformation."
        if hint_level == 2:
            return "Focus on one operation at a time and verify both sides stay balanced after each move."
        return "Rewrite from the previous correct line and apply only one algebra rule in this step."

    def _gemini_hint(self, step_text: str, error_type: str | None, concept_tag: str | None, hint_level: int) -> str:
        if not self.gemini_api_key:
            raise RuntimeError("Missing GEMINI_API_KEY")

        system_instruction = (
            "You are a math tutor. Give only hints, never final answers. "
            "Respond in 1-2 short sentences and ask a guiding question."
        )
        prompt = (
            f"Student step: {step_text}\n"
            f"Detected error_type: {error_type or 'unknown'}\n"
            f"Concept: {concept_tag or 'general_algebra'}\n"
            f"Hint level (1 low to 3 stronger): {hint_level}\n"
            "Return a scaffolded hint only."
        )

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.gemini_model}:generateContent"
        payload = {
            "system_instruction": {"parts": [{"text": system_instruction}]},
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.3, "maxOutputTokens": 120},
        }

        with httpx.Client(timeout=15.0) as client:
            response = client.post(url, params={"key": self.gemini_api_key}, json=payload)
            response.raise_for_status()
            data = response.json()

        text = (
            data.get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text", "")
            .strip()
        )

        if not text:
            raise RuntimeError("Empty Gemini response")

        # Guardrail to keep hints-only behavior
        forbidden_patterns = ["final answer", "therefore x =", "answer is"]
        if any(token in text.lower() for token in forbidden_patterns):
            raise RuntimeError("Hint policy violation")
        return text

    def generate(self, step_text: str, error_type: str | None, concept_tag: str | None, attempt_count: int) -> tuple[str, int, str]:
        hint_level = self._hint_level(attempt_count)
        try:
            hint = self._gemini_hint(step_text, error_type, concept_tag, hint_level)
            return hint, hint_level, "gemini"
        except Exception:
            return (
                self._heuristic_hint(step_text, error_type, concept_tag, hint_level),
                hint_level,
                "heuristic",
            )


hint_service = HintService()
