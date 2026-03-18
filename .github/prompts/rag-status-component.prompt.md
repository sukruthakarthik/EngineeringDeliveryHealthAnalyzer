---
description: "Build or update the RAGStatusChart React component for the Engineering Delivery Health Analyzer. Renders a pie chart showing Red/Amber/Green issue distribution using Recharts."
---

# RAG Status Component

Build the `RAGStatusChart` component at `frontend/src/components/RAGStatusChart.tsx`.

## What it renders
A responsive pie chart showing the distribution of issues by RAG status (Red / Amber / Green), plus a legend with counts and percentages.

## Props
```typescript
interface RAGStatusChartProps {
  data: {
    red: number;
    amber: number;
    green: number;
  };
}
```

## Recharts implementation
- Use `PieChart` inside `ResponsiveContainer` (height: 300px)
- Colors: Red = `#ef4444`, Amber = `#f59e0b`, Green = `#22c55e`
- Show `label` on each slice: `"Red (12)"`, `"Amber (8)"`, `"Green (30)"`
- Add a `Tooltip` showing count and percentage

## Layout
- Card wrapper: `rounded-2xl shadow-md p-6 bg-white`
- Title: `"RAG Distribution"` in `text-lg font-semibold text-gray-700`
- Chart below title
- Below chart: row of 3 colored badges with counts

## RAG Badge
```tsx
<span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-white text-sm font-medium bg-red-500">
  Red: {data.red}
</span>
```

## Output
Write the complete `RAGStatusChart.tsx` file. No explanation needed.
