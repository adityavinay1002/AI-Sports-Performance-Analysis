# AI-Based Sports Performance Analysis

This workspace contains ML scripts and a full-stack demo app (FastAPI backend + React/Tailwind frontend) to upload videos and run analyses.

Backend:
- `backend/main.py` - FastAPI server. Run with:

```bash
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload --port 8000
```

Frontend (development):

```bash
cd frontend
npm install
npm run dev
```

API endpoints:
- `POST /upload` - multipart file upload
- `POST /process` - JSON { filename: string, analyses: ["tracking","heatmap","pose"] }
- `GET /outputs` - list output files
- Static serving: `/uploads/*` and `/output/*`

Notes:
- The backend calls existing local scripts: `main.py`, `heatmap.py`, `pose.py` via subprocess. Ensure these scripts are in the repo root and produce outputs in `/output`.
- The frontend expects the backend to be proxied at `/api` — configure your dev server or proxy accordingly.
