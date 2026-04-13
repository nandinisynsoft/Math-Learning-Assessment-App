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
