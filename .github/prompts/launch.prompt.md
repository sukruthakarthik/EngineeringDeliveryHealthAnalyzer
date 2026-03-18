# Launch: Engineering Delivery Health Analyzer

Start both services from the repo root. Each runs in its own terminal.

> **Prerequisite:** Environment must be set up first. See `.github/prompts/init.prompt.md`.

---

## Terminal 1 — Backend (FastAPI)

```bash
.\venv\Scripts\activate
cd backend
uvicorn main:app --reload --port 8000
```

> **Mac/Linux:** use `source venv/bin/activate` instead.

Expected output:
```
INFO:     Will watch for changes in these directories: [...]
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process ...
INFO:     Started server process ...
INFO:     Application startup complete.
```

---

## Terminal 2 — Frontend (Vite)

```bash
cd frontend
npm run dev
```

Expected output:
```
  VITE v6.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

---

## Verify Both Are Running

| URL | Expected |
|-----|----------|
| `http://localhost:8000/docs` | FastAPI Swagger UI |
| `http://localhost:8000/api/v1/issues` | JSON with `data` + `meta` keys |
| `http://localhost:8000/api/v1/health-score` | Team score + per-issue RAG |
| `http://localhost:8000/api/v1/bottlenecks` | Sorted at-risk issues |
| `http://localhost:8000/api/v1/workload` | Priority bucket counts |
| `http://localhost:5173` | Dashboard UI |

---

## Stop Both Services

Press `Ctrl+C` in each terminal.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `port 8000 already in use` | Another uvicorn process is running. Run `netstat -ano \| findstr :8000` and kill the PID. |
| `data/issues.json not found` | The data file is missing. Connect your real data source or create the file at `data/issues.json` matching the `Issue` schema. |
| `Cannot find native binding` (frontend) | Node.js v18 is installed but v20+ is required. Upgrade Node and re-run `npm install`. |
| Backend changes not reflected | `load_issues()` is LRU-cached. Restart the backend (`Ctrl+C`, then `uvicorn` again). |
| CORS error in browser | Frontend must run on port 5173. Do not change the Vite port without updating `allow_origins` in `backend/main.py`. |
