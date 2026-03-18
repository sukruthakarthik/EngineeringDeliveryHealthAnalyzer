---
applyTo: "**/*.tsx,**/*.ts,frontend/**"
description: "Frontend coding standards for React + TypeScript + Tailwind + Recharts components in the Engineering Delivery Health Analyzer."
---

# Frontend Instructions

## Component Rules
- Functional components only — no class components
- One component per file; filename matches component name (PascalCase)
- Props interfaces defined in the same file as `interface <ComponentName>Props`
- Use `React.FC<Props>` pattern

## Styling
- Use Tailwind CSS utility classes exclusively — no CSS modules, no inline styles
- Color conventions for RAG: `bg-red-500`, `bg-amber-400`, `bg-green-500`
- Dashboard cards: `rounded-2xl shadow-md p-6 bg-white`

## Data Fetching
- All API calls go through custom hooks in `src/hooks/`
- Use `useEffect` + `useState` for data loading; expose `{ data, loading, error }` from each hook
- API base URL from env: `import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'`

## Charts (Recharts)
- Use `ResponsiveContainer` wrapping all charts for responsive sizing
- PieChart for RAG distribution; BarChart for workload distribution; RadialBarChart for health score
- Color palette: `["#ef4444", "#f59e0b", "#22c55e", "#3b82f6", "#8b5cf6"]`

## TypeScript
- No `any` — use `unknown` and narrow types
- Define all API response shapes in `src/types/api.ts`
- Use `interface` for object shapes, `type` for unions/aliases

## File Structure
```
src/
├── components/
│   ├── HealthScoreCard.tsx
│   ├── RAGStatusChart.tsx
│   ├── BottleneckTable.tsx
│   └── WorkloadDistribution.tsx
├── hooks/
│   ├── useHealthScore.ts
│   ├── useBottlenecks.ts
│   └── useIssues.ts
└── types/
    └── api.ts
```
