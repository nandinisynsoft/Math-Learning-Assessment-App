import unittest

from fastapi.testclient import TestClient

from app.main import app


class APITestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_health(self) -> None:
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_submission_analyze_and_hint_flow(self) -> None:
        submission = self.client.post(
            "/api/v1/submissions",
            json={
                "student_id": "stu_1",
                "problem_id": "prob_1",
                "input_type": "text",
                "content": "2x + 3 = 7",
            },
        )
        self.assertEqual(submission.status_code, 200)
        sid = submission.json()["id"]

        analysis = self.client.post(
            "/api/v1/attempts/analyze",
            json={
                "submission_id": sid,
                "step_index": 0,
                "step_text": "x=7-3",
                "expected_step_text": "2x=4",
            },
        )
        self.assertEqual(analysis.status_code, 200)

        hint = self.client.post(
            "/api/v1/hints/generate",
            json={
                "student_id": "stu_1",
                "problem_id": "prob_1",
                "step_text": "x=7-3",
                "error_type": analysis.json()["error_type"],
                "concept_tag": analysis.json()["concept_tag"],
                "attempt_count_for_problem": 1,
            },
        )
        self.assertEqual(hint.status_code, 200)
        self.assertTrue(hint.json()["hint"])


if __name__ == "__main__":
    unittest.main()
