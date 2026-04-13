import os
import unittest

os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["JWT_SECRET_KEY"] = "test-secret"

import unittest

from fastapi.testclient import TestClient

from app.main import app


class APITestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_auth_and_learning_flow(self) -> None:
        # Register student
        reg = self.client.post(
            "/api/v1/auth/register",
            json={
                "email": "student@example.com",
                "full_name": "Student One",
                "password": "password123",
                "role": "student",
            },
        )
        self.assertIn(reg.status_code, [201, 400])

        login = self.client.post(
            "/api/v1/auth/login",
            json={"email": "student@example.com", "password": "password123"},
        )
        self.assertEqual(login.status_code, 200)
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        sub = self.client.post(
            "/api/v1/learning/submissions",
            headers=headers,
            json={
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
        self.assertEqual(sub.status_code, 201)

        sub_id = sub.json()["id"]
        attempt = self.client.post(
            "/api/v1/learning/attempts/analyze",
            headers=headers,
            json={
                "submission_id": sub_id,
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
        self.assertEqual(attempt.status_code, 200)

        hint = self.client.post(
            "/api/v1/learning/hints/generate",
            headers=headers,
            json={
                "problem_id": "prob_1",
                "step_text": "x=7-3",
                "error_type": attempt.json()["error_type"],
                "concept_tag": attempt.json()["concept_tag"],
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
