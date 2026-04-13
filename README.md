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
