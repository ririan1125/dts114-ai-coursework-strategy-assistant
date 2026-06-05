# AI Coursework Strategy Assistant

This is the software component for DTS114TC coursework. It implements an AI-assisted meta-software development system where a student enters coursework tasks, deadlines, importance, complexity, and estimated effort. The system returns a priority score, action strategy, risk flags, milestones, acceptance criteria, generated SDLC documentation, UML artifacts, and a Flask website.

## Run Locally

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5005`.

## Test

```bash
pytest
```

## Optional LLM Setup

Copy `.env.example` to `.env`, add `DEEPSEEK_API_KEY`, and run the app. If the API key is missing or unavailable, the deterministic strategy engine is used so the app still works.

## API Examples

```bash
curl http://127.0.0.1:5005/health
```

```bash
curl -X POST http://127.0.0.1:5005/api/strategy ^
  -H "Content-Type: application/json" ^
  -d "{\"title\":\"Report\",\"deadline\":\"2026-06-07T23:59\",\"importance\":5,\"complexity\":4,\"estimated_hours\":8}"
```

## Deployment

For Render, use:

- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app`

The included `render.yaml`, `Procfile`, Dockerfile, tests, and GitHub Actions workflow support deployment and CI/CD evidence.

