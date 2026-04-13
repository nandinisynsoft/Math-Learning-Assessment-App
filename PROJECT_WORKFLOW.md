# Math Learning & Assessment App MVP Workflow

## 1) Product Goal
Build an AI-assisted math learning app MVP that:
- Accepts student math input (typed text and image upload).
- Detects step-level mistakes and likely misconceptions.
- Returns guided hints (not final answers).
- Tracks attempts for student progress and teacher dashboards.

## 2) MVP Scope (6–12 Weeks)

### In Scope
- Student problem workspace (text input + image upload).
- OCR + math expression extraction pipeline.
- Step parser + validation engine.
- LLM hint generation with guardrails.
- Attempt/event logging.
- Basic teacher dashboard (class-level + student-level trends).

### Out of Scope (for v1 speed)
- Full curriculum authoring suite.
- Real-time multiplayer/classroom collaboration.
- Complex adaptive testing engine.
- Native mobile apps (web-first MVP).
- Deep analytics/BI layer.

## 3) System Architecture (High-Level)

### Frontend
- **Student App**: submit solution steps (text/image), receive hints, retry.
- **Teacher App**: view repeated errors, misconception clusters, student trajectories.

### Backend Services
1. **API Gateway / App Server**
   - Auth, request validation, routing.
2. **Submission Service**
   - Stores raw student work, metadata (problem_id, step_index, timestamp).
3. **OCR + Normalization Service**
   - Converts image to structured text/math representation.
4. **Analysis Service**
   - Step-level correctness checks.
   - Error type classification (arithmetic/sign/algebraic-rule/etc.).
5. **Hint Service (LLM)**
   - Produces bounded hints with policy checks.
6. **Progress & Analytics Service**
   - Aggregates repeated mistakes and trends for dashboards.

### Data Stores
- **PostgreSQL**: users, classes, problems, attempts, hint history.
- **Object Storage**: uploaded images.
- **Redis (optional)**: caching and rate-limit support.

## 4) End-to-End Student Flow
1. Student opens a problem.
2. Student submits a step (text or image).
3. If image:
   - OCR extracts content.
   - Normalizer converts to canonical math text.
4. Step analyzer compares current step against expected transformations/rules.
5. Error classifier labels mistake + confidence.
6. Hint policy engine decides response level:
   - Socratic question → targeted hint → stronger hint (if repeated attempts).
   - Never return full final answer in MVP hint mode.
7. Response returned with:
   - correctness flag,
   - mistake category,
   - next hint,
   - encouragement + retry prompt.
8. Attempt logged for longitudinal tracking.

## 5) Hint Safety & Quality Controls
- Prompt templates enforce “hint-only” responses.
- Output validator blocks direct full-solution patterns.
- Escalation ladder (max hint depth per attempt count).
- Deterministic checks for common algebra/arithmetic operations before LLM call.
- Fallback response if model output is invalid (“Let’s focus on the previous step…”).

## 6) Data Model (Minimal)
- `users` (student/teacher)
- `classes`
- `problems`
- `submissions` (raw text/image ref)
- `attempts` (step, correctness, error_type, hint_level)
- `misconception_events` (student_id, concept_tag, frequency)
- `teacher_views` (materialized or queried aggregates)

## 7) API Surface (MVP)
- `POST /api/v1/submissions` (text/image upload)
- `POST /api/v1/attempts/analyze` (step-level analysis)
- `POST /api/v1/hints/generate` (guardrailed hint generation)
- `GET /api/v1/students/{id}/progress`
- `GET /api/v1/teachers/{id}/dashboard`

## 8) Repeated-Mistake Detection Strategy
- Rule: if same `concept_tag` occurs N times within M attempts/time window, flag as repeated misconception.
- Trigger interventions:
  - easier scaffold hint,
  - micro-remediation problem,
  - teacher notification on dashboard.
- Keep per-student concept profile to adapt future hints.

## 9) Delivery Plan by Week

### Weeks 1–2
- Finalize data model and API contracts.
- Build auth + submission endpoints.
- Implement text-first workflow.

### Weeks 3–4
- Add image upload + OCR pipeline.
- Build step analyzer for top 5 problem types.

### Weeks 5–6
- Integrate LLM hint service + guardrails.
- Add attempt logging and misconception tagging.

### Weeks 7–8
- Teacher dashboard MVP.
- QA on edge cases (incomplete/incorrect steps).

### Weeks 9–10 (optional extension)
- Improve accuracy and latency.
- Add more concept coverage and evaluations.

### Weeks 11–12 (optional extension)
- Pilot hardening, observability, and deployment refinements.

## 10) Engineering Workflow
- Trunk-based development with feature flags.
- CI checks: lint, tests, type checks, API contract tests.
- Environment separation: dev/staging/prod.
- Observability: structured logs + request tracing + model-response audits.

## 11) Interview Response Workflow (How to Use This for Application)
For each asynchronous interview question, answer with:
1. **Context**: problem and users.
2. **Your direct contribution**: architecture, backend, AI integration, deployment.
3. **Technical decisions**: model choice, OCR, validation, tradeoffs.
4. **Outcomes**: measurable impact (accuracy, latency, engagement, retention).
5. **MVP prioritization**: what you intentionally skipped and why.

This keeps your response practical, credible, and implementation-focused.
