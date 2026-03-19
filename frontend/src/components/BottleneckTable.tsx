import React from 'react'
import type { IssueWithScore } from '../types/api'
import type { UseBottlenecksResult } from '../hooks/useBottlenecks'

type BottleneckTableProps = UseBottlenecksResult

const RAG_TEXT: Record<string, string> = {
  Red: 'text-red-500 font-semibold',
  Amber: 'text-amber-500 font-semibold',
  Green: 'text-green-500',
}

const PRIORITY_BADGE: Record<string, string> = {
  Critical: 'bg-red-100 text-red-700',
  High: 'bg-orange-100 text-orange-700',
  Medium: 'bg-yellow-100 text-yellow-700',
  Low: 'bg-gray-100 text-gray-600',
}

const STATUS_BADGE: Record<string, string> = {
  Open: 'bg-blue-100 text-blue-700',
  'In Progress': 'bg-yellow-100 text-yellow-700',
  Blocked: 'bg-red-100 text-red-700',
  Done: 'bg-green-100 text-green-700',
}

const BottleneckTable: React.FC<BottleneckTableProps> = ({ data, loading, error }) => {
  if (loading) {
    return <div className="rounded-2xl shadow-md p-6 bg-white animate-pulse h-48" />
  }
  if (error) {
    return (
      <div className="rounded-2xl shadow-md p-6 bg-white">
        <p className="text-red-500 text-sm">Error: {error}</p>
      </div>
    )
  }

  const bottlenecks = data?.data ?? []

  return (
    <div className="rounded-2xl shadow-md p-6 bg-white">
      <h2 className="text-lg font-semibold text-gray-700 mb-4">
        Bottlenecks
        {bottlenecks.length > 0 && (
          <span className="ml-2 text-sm bg-red-100 text-red-600 px-2 py-0.5 rounded-full">
            {bottlenecks.length}
          </span>
        )}
      </h2>
      {bottlenecks.length === 0 ? (
        <p className="text-gray-500 text-sm">No bottlenecks detected.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead>
              <tr className="text-gray-400 border-b text-xs uppercase tracking-wide">
                <th className="pb-2 pr-4">ID</th>
                <th className="pb-2 pr-4">Title</th>
                <th className="pb-2 pr-4">Status</th>
                <th className="pb-2 pr-4">Priority</th>
                <th className="pb-2 pr-4">Days Open</th>
                <th className="pb-2 pr-4">Score</th>
                <th className="pb-2 pr-4">RAG</th>
                <th className="pb-2">Reason</th>
              </tr>
            </thead>
            <tbody>
              {bottlenecks.map((issue: IssueWithScore) => (
                <tr
                  key={issue.issue_id}
                  className="border-b last:border-0 hover:bg-gray-50 transition-colors"
                >
                  <td className="py-2 pr-4 font-mono text-gray-400 text-xs">{issue.issue_id}</td>
                  <td
                    className="py-2 pr-4 font-medium text-gray-800 max-w-xs truncate"
                    title={issue.title}
                  >
                    {issue.title}
                  </td>
                  <td className="py-2 pr-4">
                    <span
                      className={`px-2 py-0.5 rounded text-xs font-medium ${STATUS_BADGE[issue.status] ?? 'bg-gray-100 text-gray-600'}`}
                    >
                      {issue.status}
                    </span>
                  </td>
                  <td className="py-2 pr-4">
                    <span
                      className={`px-2 py-0.5 rounded text-xs font-medium ${PRIORITY_BADGE[issue.priority]}`}
                    >
                      {issue.priority}
                    </span>
                  </td>
                  <td className="py-2 pr-4 text-gray-600">{issue.days_open}d</td>
                  <td className="py-2 pr-4 text-gray-700 font-medium">{issue.health_score}</td>
                  <td className={`py-2 pr-4 ${RAG_TEXT[issue.rag]}`}>{issue.rag}</td>
                  <td className="py-2 text-gray-400 text-xs">{issue.bottleneck_reason ?? '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

export default BottleneckTable
