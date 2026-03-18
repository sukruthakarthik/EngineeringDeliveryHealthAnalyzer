# Plan: Engineering Delivery Health Analyzer — Codathon Team Matrix

## TL;DR
Build a React + FastAPI dashboard analyzing JIRA-like work items for delivery health. Use GitHub Copilot customization primitives strategically to accelerate development: workspace instructions for always-on context, file instructions for scoped coding rules, prompts for focused one-shot tasks, and agents for isolated domain workflows.

---

## Phase 0: Copilot Customization Setup (Foundation)
*These files guide Copilot throughout the entire codathon.*

1. Create `.github/copilot-instructions.md` — workspace instructions with:
   - Tech stack: React + Python FastAPI
   - Assumption log format
   - Mock data is acceptable
   - File/folder conventions

2. Create `.github/instructions/frontend.instructions.md` (applyTo: `**/*.tsx,**/*.ts`) — React/UI conventions, Tailwind/Recharts usage, component structure

3. Create `.github/instructions/analytics.instructions.md` (applyTo: `**/analytics/**,**/*.py`) — Python conventions, health scoring rules, data model definitions

4. Create `.github/instructions/api.instructions.md` (applyTo: `**/api/**,**/routes/**`) — FastAPI patterns, response schemas, CORS setup

### Prompts (slash-command one-shot tasks)
5. Create `.github/prompts/generate-mock-data.prompt.md` — generates realistic JIRA-like mock CSV/JSON dataset
6. Create `.github/prompts/health-score-formula.prompt.md` — designs the scoring algorithm (weights for status, priority, days_open)
7. Create `.github/prompts/rag-status-component.prompt.md` — builds the Red/Amber/Green status visualization component
8. Create `.github/prompts/bottleneck-detection.prompt.md` — identifies blocked/stalled tickets logic

### Agents
9. Create `.github/agents/data-analyst.agent.md` — isolated agent for analytics engine: reads issue data, computes health scores, detects bottlenecks
10. Create `.github/agents/dashboard-builder.agent.md` — isolated agent for UI/frontend: builds charts, RAG widgets, workload distribution views

---

## Phase 1: Project Scaffold
*Depends on Phase 0.*

11. Scaffold Python FastAPI backend: `backend/` with `main.py`, `routes/`, `models/`, `analytics/`
12. Scaffold React frontend: `frontend/` with Vite + React + Tailwind + Recharts
13. Create mock dataset: `data/issues.json` (use generate-mock-data prompt)

---

## Phase 2: Analytics Engine (use data-analyst agent)
*Depends on Phase 1.*

14. Implement health scoring model (`analytics/scoring.py`) — weighted formula across status, priority, days_open
15. Implement bottleneck detection (`analytics/bottlenecks.py`) — identify Blocked/Critical/long-running items
16. Implement RAG classification (`analytics/rag.py`) — Red/Amber/Green thresholds
17. Expose FastAPI endpoints: `GET /health-score`, `GET /bottlenecks`, `GET /workload`, `GET /issues`

---

## Phase 3: Dashboard (use dashboard-builder agent)
*Depends on Phase 2 API being available.*

18. Build `HealthScoreCard` component — overall delivery score with trend
19. Build `RAGStatusChart` component — pie/bar chart with Red/Amber/Green distribution
20. Build `BottleneckTable` component — sorted list of at-risk issues
21. Build `WorkloadDistribution` component — chart of open items by assignee/priority
22. Wire up API calls + loading states

---

## Phase 4: Integration & Demo Polish
23. Add assumptions page/section documenting decisions
24. End-to-end test with mock data
25. README with setup instructions and architecture diagram

---

## Relevant Files to Create

| File | Role |
|------|------|
| `.github/copilot-instructions.md` | Workspace instruction — always-on project context |
| `.github/instructions/frontend.instructions.md` | File instruction — scoped to React/TS files |
| `.github/instructions/analytics.instructions.md` | File instruction — scoped to Python analytics |
| `.github/instructions/api.instructions.md` | File instruction — scoped to FastAPI routes |
| `.github/prompts/generate-mock-data.prompt.md` | Prompt — one-shot mock data generation |
| `.github/prompts/health-score-formula.prompt.md` | Prompt — scoring algorithm design |
| `.github/prompts/rag-status-component.prompt.md` | Prompt — RAG visualization component |
| `.github/prompts/bottleneck-detection.prompt.md` | Prompt — bottleneck logic |
| `.github/agents/data-analyst.agent.md` | Agent — analytics engine domain |
| `.github/agents/dashboard-builder.agent.md` | Agent — UI/visualization domain |

---

## Decisions
- Tech stack: React + FastAPI (Python)
- Mock data acceptable; will use JSON files
- Assumptions documented inline in copilot-instructions.md
- No auth/login required (codathon prototype)
- Recharts for visualization (React-native, no D3 complexity)

## Verification
1. Run `uvicorn main:app` — all 4 API endpoints return valid JSON
2. Run `npm run dev` — dashboard renders all 4 components with mock data
3. Health score changes when mock data is modified
4. RAG chart shows correct color distribution
5. Bottleneck table correctly surfaces Blocked/Critical items
