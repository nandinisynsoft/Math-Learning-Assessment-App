# Math Learning & Assessment App - Production-Grade Backend (FastAPI + PostgreSQL)

This backend now uses a production-oriented architecture with:
- Modular routers (`/api/v1/auth`, `/api/v1/learning`)
- Service layer separation
- JWT auth + role-based authorization (student/teacher)
- PostgreSQL persistence via SQLAlchemy ORM
- EasyOCR integration (free/local OCR)
- Gemini hinting with safe heuristic fallback

## Tech Stack
- FastAPI
- PostgreSQL + SQLAlchemy
- JWT (python-jose)
- Passlib bcrypt password hashing
- EasyOCR (free OCR)

## Project Structure
```
app/
  api/
    deps.py
    v1/
      auth.py
      learning.py
      router.py
  core/
    config.py
    security.py
  db/
    base.py
    session.py
  models/
    user.py
    submission.py
    attempt.py
  schemas/
    auth.py
    learning.py
  services/
    auth_service.py
    learning_service.py
    analysis.py
    hints.py
    ocr.py
  main.py
```

## Environment Variables
Create `.env`:
```env
APP_ENV=development
DEBUG=true
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/math_app
JWT_SECRET_KEY=replace-with-strong-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.5-flash
```
# Math Learning & Assessment App (MVP Backend)

This repository now contains a working Python backend scaffold for an AI-powered math learning and assessment MVP.

## Stack
- Python + FastAPI backend
- Gemini API for hint generation (with heuristic fallback)
- EasyOCR for free OCR (local, no paid OCR API needed)
- Lightweight heuristic/ML-ready step analyzer
- In-memory storage (easy to replace with PostgreSQL)

## Features Implemented
- Accept student submissions (`text` or `image` payload mode)
- OCR extraction via EasyOCR from file path/base64/data-url payloads
- Step-by-step attempt analysis with misconception tags
- Hint generation policy (hint-only, no full solution)
- Student progress endpoint
- Teacher dashboard endpoint with repeated-mistake summaries

## Run Locally
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## API Endpoints
### Auth
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`

### Learning (authenticated)
- `POST /api/v1/learning/submissions`
- `POST /api/v1/learning/attempts/analyze`
- `POST /api/v1/learning/hints/generate`
- `GET /api/v1/learning/students/me/progress`
- `GET /api/v1/learning/teachers/me/dashboard`

## Notes for Production
- `Base.metadata.create_all` is included for quick bootstrap; replace with Alembic migrations in deployment pipelines.
- Add Redis caching + background workers for OCR/hinting tasks under high load.
- Add rate limiting, audit logs, and observability (OpenTelemetry + Sentry) for hardened production use.
Open API docs at: `http://127.0.0.1:8000/docs`

## Environment Variables
- `GEMINI_API_KEY` (optional): if omitted, heuristic hints are used.
- `GEMINI_MODEL` (optional, default: `gemini-2.5-flash`)

## API Endpoints
- `GET /health`
- `POST /api/v1/submissions`
- `POST /api/v1/attempts/analyze`
- `POST /api/v1/hints/generate`
- `GET /api/v1/students/{student_id}/progress`
- `GET /api/v1/teachers/{teacher_id}/dashboard`

## OCR Options (Free)
1. **EasyOCR (implemented here)**
   - Fully free/local (CPU mode enabled)
   - No external API keys
2. **Tesseract OCR**
   - Also free/local but weaker for handwritten math without tuning
3. **OCR.space API**
   - Free tier API if you prefer hosted OCR

## Example Flow
1. Create submission.
2. Analyze one or more steps.
3. Request hint.
4. Read student progress or teacher dashboard.

## Notes
- Current storage is in-memory for MVP speed.
- EasyOCR is integrated for OCR in this MVP.
- Replace analyzer heuristics with trained misconception classifier when dataset grows.
