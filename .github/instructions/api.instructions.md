---
applyTo: "backend/routes/**,backend/models/**,backend/main.py"
description: "FastAPI route and model conventions for the Engineering Delivery Health Analyzer backend API."
---

# API Instructions

## FastAPI Conventions
- All routes defined in `backend/routes/` as separate router modules
- Import and mount each router in `backend/main.py` with a prefix
- Use `APIRouter(prefix="/api/v1", tags=["..."])` in each route file

## Response Envelope
Every endpoint returns:
```python
{
  "data": <payload>,
  "meta": { "generated_at": "<ISO timestamp>" }
}
```
Helper function in `backend/models/response.py`:
```python
def make_response(data):
    return {"data": data, "meta": {"generated_at": datetime.utcnow().isoformat()}}
```

## Error Handling
```python
from fastapi import HTTPException
raise HTTPException(status_code=404, detail="Issues not found")
```

## CORS
Always configure CORS in `main.py` to allow the frontend origin:
```python
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], allow_methods=["*"], allow_headers=["*"])
```

## Endpoints
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/issues` | Return all issues |
| GET | `/api/v1/health-score` | Overall team health score + per-issue scores |
| GET | `/api/v1/bottlenecks` | Issues flagged as bottlenecks |
| GET | `/api/v1/workload` | Priority bucket distribution |

## Pydantic Models
Define in `backend/models/`:
- `Issue` — input shape from data file
- `IssueWithScore` — Issue + `health_score: int` + `rag: str`
- `HealthSummary` — `team_score: int`, `rag: str`, `issues: list[IssueWithScore]`
