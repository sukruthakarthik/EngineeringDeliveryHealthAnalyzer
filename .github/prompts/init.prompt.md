# Initial Setup

Step-by-step environment setup for the **Engineering Delivery Health Analyzer** codathon project.

## Prerequisites

| Tool | Required Version | Download |
|------|-----------------|----------|
| Python | 3.11+ | https://www.python.org/downloads/ |
| Node.js | 20+ (LTS) | https://nodejs.org/ |
| npm | 10+ (bundled with Node) | — |

Verify your installations:

```bash
python --version   # should print Python 3.11.x or higher
node --version     # should print v20.x.x or higher
npm --version      # should print 10.x.x or higher
```

---

## Backend Setup (Python / FastAPI)

### 1. Create a virtual environment

From the repo root:

```bash
python -m venv venv
```

### 2. Activate the virtual environment

**Windows**
```bash
venv\Scripts\activate
```

**Mac/Linux**
```bash
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

### 3. Install Python dependencies

```bash
pip install -r backend/requirements.txt
```

Key packages installed:
- `fastapi==0.115.11` — API framework
- `uvicorn[standard]==0.34.0` — ASGI server
- `pydantic==2.10.4` — data validation / schemas

### 4. Run the backend server

```bash
cd backend
uvicorn main:app --reload --port 8000
```

API will be available at `http://localhost:8000`.  
Interactive docs at `http://localhost:8000/docs`.

---

## Frontend Setup (React / Vite)

### 1. Install Node dependencies

```bash
cd frontend
npm install
```

Key packages installed:
- `react@18` + `react-dom@18` — UI framework
- `vite@6` + `@vitejs/plugin-react` — build tooling
- `typescript` — type safety
- `tailwindcss@3` + `postcss` + `autoprefixer` — utility-first CSS
- `recharts` — charting library

### 2. Run the frontend dev server

```bash
npm run dev
```

Dashboard will be available at `http://localhost:5173`.

> **Note:** The frontend calls the backend directly at `http://localhost:8000` (no proxy).  
> Start the backend server before the frontend for full functionality.

---

## Running Both Services Together

Open two terminals from the repo root:

**Terminal 1 — Backend**
```bash
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux
cd backend
uvicorn main:app --reload --port 8000
```

**Terminal 2 — Frontend**
```bash
cd frontend
npm run dev
```

---

## Quick Verification Checklist

- [ ] `http://localhost:8000/docs` — FastAPI Swagger UI loads
- [ ] `http://localhost:8000/health-score` — returns JSON with `data` and `meta` keys
- [ ] `http://localhost:8000/bottlenecks` — returns list of at-risk issues
- [ ] `http://localhost:8000/workload` — returns workload distribution
- [ ] `http://localhost:8000/issues` — returns full issue list
- [ ] `http://localhost:5173` — dashboard renders all four components

