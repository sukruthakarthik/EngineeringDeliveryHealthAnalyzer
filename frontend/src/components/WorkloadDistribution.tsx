import React from 'react'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Cell,
  ResponsiveContainer,
} from 'recharts'
import type { UseWorkloadResult } from '../hooks/useWorkload'

interface WorkloadDistributionProps extends UseWorkloadResult {
  selectedPriorities?: string[]
}

const PRIORITY_COLORS: Record<string, string> = {
  Critical: '#ef4444',
  High: '#f97316',
  Medium: '#f59e0b',
  Low: '#22c55e',
}

const GREYED_OUT = '#d1d5db'

const WorkloadDistribution: React.FC<WorkloadDistributionProps> = ({ data, loading, error, selectedPriorities }) => {
  if (loading) {
    return <div className="rounded-2xl shadow-md p-6 bg-white animate-pulse h-64" />
  }
  if (error) {
    return (
      <div className="rounded-2xl shadow-md p-6 bg-white">
        <p className="text-red-500 text-sm">Error: {error}</p>
      </div>
    )
  }
  if (!data) return null

  const chartData = (['Critical', 'High', 'Medium', 'Low'] as const).map(priority => ({
    priority,
    count: data.data[priority],
  }))
  const total = chartData.reduce((sum, d) => sum + d.count, 0)

  const hasFilter = selectedPriorities !== undefined && selectedPriorities.length > 0

  return (
    <div className="rounded-2xl shadow-md p-6 bg-white">
      <h2 className="text-lg font-semibold text-gray-700 mb-1">Active Workload by Priority</h2>
      <p className="text-sm text-gray-400 mb-4">{total} active issues (excludes Done)</p>
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={chartData} margin={{ top: 4, right: 16, bottom: 4, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" vertical={false} />
          <XAxis
            dataKey="priority"
            tick={{ fontSize: 12, fill: '#6b7280' }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            allowDecimals={false}
            tick={{ fontSize: 12, fill: '#6b7280' }}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip cursor={{ fill: '#f9fafb' }} />
          <Bar dataKey="count" radius={[6, 6, 0, 0]}>
            {chartData.map(entry => (
              <Cell
                key={entry.priority}
                fill={
                  hasFilter && !selectedPriorities!.includes(entry.priority)
                    ? GREYED_OUT
                    : PRIORITY_COLORS[entry.priority]
                }
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

export default WorkloadDistribution
