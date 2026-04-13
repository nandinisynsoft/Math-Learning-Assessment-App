import httpx

from app.core.config import settings


class HintService:
    @staticmethod
    def _hint_level(attempt_count: int) -> int:
        if attempt_count <= 1:
            return 1
        if attempt_count <= 3:
            return 2
        return 3

    def _heuristic_hint(self, error_type: str | None, hint_level: int) -> str:
        if error_type == "sign_error":
            return "Check sign rules carefully. What does subtracting a negative become?"
        if error_type == "incomplete_step":
            return "Write both sides of the equation after applying the operation."
        if hint_level == 1:
            return "Which algebra rule are you applying in this step?"
        if hint_level == 2:
            return "Undo one operation at a time and keep both sides balanced."
        return "Go back one correct line and re-apply the transformation slowly."

    def _gemini_hint(self, step_text: str, error_type: str | None, concept_tag: str | None, hint_level: int) -> str:
        if not settings.gemini_api_key:
            raise RuntimeError("Missing GEMINI_API_KEY")

        prompt = (
            "You are a math tutor. Give only a hint, never final answer. "
            "Return 1-2 short sentences and ask a guiding question.\n"
            f"step_text={step_text}\nerror_type={error_type}\nconcept_tag={concept_tag}\nhint_level={hint_level}"
        )

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.gemini_model}:generateContent"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.3, "maxOutputTokens": 120},
        }
        with httpx.Client(timeout=15.0) as client:
            response = client.post(url, params={"key": settings.gemini_api_key}, json=payload)
            response.raise_for_status()
            data = response.json()

        text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
        if not text:
            raise RuntimeError("Empty Gemini response")
        if any(x in text.lower() for x in ["answer is", "therefore x =", "final answer"]):
            raise RuntimeError("Hint policy violation")
        return text

    def generate(self, step_text: str, error_type: str | None, concept_tag: str | None, attempt_count: int) -> tuple[str, int, str]:
        hint_level = self._hint_level(attempt_count)
        try:
            return self._gemini_hint(step_text, error_type, concept_tag, hint_level), hint_level, "gemini"
        except Exception:
            return self._heuristic_hint(error_type, hint_level), hint_level, "heuristic"


hint_service = HintService()
