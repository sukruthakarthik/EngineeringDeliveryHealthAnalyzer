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
import type { WorkloadDistribution as WorkloadData } from '../types/api'

interface WorkloadDistributionProps {
  workload: WorkloadData
  selectedPriorities?: string[]
  isCompletedRelease?: boolean
}

const PRIORITY_COLORS: Record<string, string> = {
  Critical: '#ef4444',
  High: '#f97316',
  Medium: '#f59e0b',
  Low: '#22c55e',
}

const GREYED_OUT = '#d1d5db'

const WorkloadDistribution: React.FC<WorkloadDistributionProps> = ({ workload, selectedPriorities, isCompletedRelease }) => {
  if (isCompletedRelease) {
    return (
      <div className="rounded-2xl shadow-md p-6 bg-white flex flex-col">
        <h2 className="text-lg font-semibold text-gray-700 mb-1">Active Workload by Priority</h2>
        <div className="flex-1 flex flex-col items-center justify-center text-center py-8">
          <div className="w-12 h-12 rounded-full bg-gray-100 flex items-center justify-center mb-3">
            <svg className="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <p className="text-gray-500 font-medium text-sm">Release completed</p>
          <p className="text-gray-400 text-xs mt-1">No active workload for completed releases</p>
        </div>
      </div>
    )
  }

  const chartData = (['Critical', 'High', 'Medium', 'Low'] as const).map(priority => ({
    priority,
    count: workload[priority],
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
