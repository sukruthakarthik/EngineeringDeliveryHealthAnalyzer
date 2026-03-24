import React, { useMemo } from 'react'
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts'
import { useSpaces } from '../hooks/useSpaces'
import { useHealthSummary } from '../hooks/useHealthSummary'
import { useActiveRelease } from '../hooks/useActiveRelease'

/** Hardcoded team lead per space shown on the landing page card. */
const SPACE_TEAM_LEAD: Record<string, string> = {
  'TSA-SITE': 'Sukrutha Karthik',
  'Voice Policy Engine 2.0': 'Roja Rameti',
  'RCEM 3.0': 'Sumit Kumar',
  'AIP Risk Support': 'Bruno Ferraz',
  'Steering 9.0': 'Chandramouli B',
}


interface LandingPageProps {
  onViewDetails: (space: string, release?: string) => void
}

const RAG_COLORS: Record<string, string> = {
  Green: '#22c55e',
  Amber: '#f59e0b',
  Red: '#ef4444',
}

interface SpaceCardProps {
  space: string
  onViewDetails: (space: string, release?: string) => void
}

const SpaceCard: React.FC<SpaceCardProps> = ({ space, onViewDetails }) => {
  // Get the active (unreleased) release from the dedicated JIRA API
  const activeReleaseObj = useActiveRelease(space)
  const activeRelease = activeReleaseObj?.name ?? null

  // Lightweight summary: just RAG counts, no full issue list
  const { data, loading, error } = useHealthSummary(space, activeRelease ?? undefined)

  // Fallback: if no active release, label as "Internal" (show all issues)
  const displayRelease = activeRelease ?? 'Internal'
  const isActiveRelease = !!activeRelease

  const totalIssues = data?.data.total_issues ?? 0
  const ragCounts = useMemo(() => ({
    Red: data?.data.red ?? 0,
    Amber: data?.data.amber ?? 0,
    Green: data?.data.green ?? 0,
  }), [data])

  const ragData = useMemo(() => {
    if (totalIssues === 0) return [{ name: 'None', value: 1 }]
    return [
      { name: 'Red', value: ragCounts.Red },
      { name: 'Amber', value: ragCounts.Amber },
      { name: 'Green', value: ragCounts.Green },
    ]
  }, [totalIssues, ragCounts])

  // Hardcoded team lead for this space
  const teamLead = SPACE_TEAM_LEAD[space] ?? ''

  return (
    <div className="bg-white rounded-2xl shadow-lg p-6 hover:shadow-2xl transition-shadow border-2 border-gray-100 hover:border-blue-200 flex flex-col">
      <h3 className="text-xl font-bold text-gray-800 mb-1 truncate" title={space}>
        {space}
      </h3>

      {/* Release badge */}
      {displayRelease && !loading && !error && (
        <div className="flex items-center gap-1.5 mb-3">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"
            className={`w-3.5 h-3.5 shrink-0 ${isActiveRelease ? 'text-indigo-400' : 'text-gray-400'}`}>
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
              d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A2 2 0 013 12V7a2 2 0 012-2z" />
          </svg>
          <span className={`text-xs font-semibold px-2 py-0.5 rounded-full truncate ${
            isActiveRelease
              ? 'text-indigo-600 bg-indigo-50'
              : 'text-gray-500 bg-gray-100'
          }`}>
            {displayRelease}
          </span>
        </div>
      )}

      {loading && (
        <div className="flex flex-col items-center justify-center h-48">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-500"></div>
          <p className="mt-3 text-sm text-gray-400">Loading...</p>
        </div>
      )}

      {error && (
        <div className="flex flex-col items-center justify-center h-48">
          <p className="text-red-500 text-sm text-center">Error: {error}</p>
        </div>
      )}

      {!loading && !error && (
        <div className="mb-2 flex-1">
          <p className="text-xs text-gray-400 mb-2">
            {displayRelease ? `${totalIssues} issues in release` : `${totalIssues} total issues`}
          </p>

          <ResponsiveContainer width="100%" height={160}>
            <PieChart>
              <Pie
                data={ragData}
                dataKey="value"
                nameKey="name"
                cx="50%"
                cy="50%"
                outerRadius={65}
                label={false}
              >
                {ragData.map(entry => (
                  <Cell key={entry.name} fill={entry.name === 'None' ? '#d1d5db' : RAG_COLORS[entry.name]} />
                ))}
              </Pie>
            </PieChart>
          </ResponsiveContainer>

          {totalIssues > 0 ? (
            <div className="flex justify-around mt-2 text-sm">
              <div className="text-center">
                <div className="flex items-center justify-center gap-1">
                  <div className="w-3 h-3 rounded-full bg-red-500"></div>
                  <span className="font-semibold">{ragCounts.Red}</span>
                </div>
                <p className="text-gray-500 text-xs mt-0.5">Red</p>
              </div>
              <div className="text-center">
                <div className="flex items-center justify-center gap-1">
                  <div className="w-3 h-3 rounded-full bg-amber-400"></div>
                  <span className="font-semibold">{ragCounts.Amber}</span>
                </div>
                <p className="text-gray-500 text-xs mt-0.5">Amber</p>
              </div>
              <div className="text-center">
                <div className="flex items-center justify-center gap-1">
                  <div className="w-3 h-3 rounded-full bg-green-500"></div>
                  <span className="font-semibold">{ragCounts.Green}</span>
                </div>
                <p className="text-gray-500 text-xs mt-0.5">Green</p>
              </div>
            </div>
          ) : (
            <div className="text-center mt-2 text-sm space-y-0.5">
              <p className="text-gray-500 font-medium">No issues in this release</p>
            </div>
          )}

          {/* Team — hardcoded lead + "more" */}
          {teamLead && (
            <div className="mt-4 pt-3 border-t border-gray-100">
              <p className="text-xs font-semibold text-gray-500 mb-1.5 flex items-center gap-1">
                <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                    d="M17 20h5v-2a4 4 0 00-5-3.87M9 20H4v-2a4 4 0 015-3.87m6-4a4 4 0 11-8 0 4 4 0 018 0z" />
                </svg>
                Team
              </p>
              <div className="flex flex-wrap gap-1">
                <span
                  title={teamLead}
                  className="inline-block max-w-[130px] truncate text-xs rounded-full px-2 py-0.5 font-medium bg-blue-100 text-blue-700 ring-1 ring-blue-300"
                >
                  {teamLead}
                </span>
                <span className="text-xs text-gray-400 self-center pl-0.5">+more</span>
              </div>
            </div>
          )}
        </div>
      )}

      <button
        onClick={() => onViewDetails(space, activeRelease ?? undefined)}
        className="w-full mt-4 px-4 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors shadow-md hover:shadow-lg"
      >
        View Details
      </button>
    </div>
  )
}

const LandingPage: React.FC<LandingPageProps> = ({ onViewDetails }) => {
  const spaces = useSpaces()

  const spaceOptions = useMemo(() => {
    if (!spaces.data?.data) return []
    return Object.keys(spaces.data.data)
  }, [spaces.data])

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
      <div className="max-w-7xl mx-auto">
        <header className="mb-12 text-center">
          <h1 className="text-5xl font-bold text-gray-800 mb-4">
            Engineering Delivery Health Analyzer
          </h1>
          <p className="text-xl text-gray-600">
            Real-time delivery risk and workload visibility
          </p>
        </header>

        <div className="mb-8">
          <h2 className="text-3xl font-semibold text-gray-700 mb-6 text-center">Project Spaces - RAG Status Distribution</h2>

          {spaces.loading && (
            <div className="text-center py-16">
              <div className="inline-block animate-spin rounded-full h-16 w-16 border-b-2 border-blue-500"></div>
              <p className="mt-4 text-gray-600 text-lg">Loading spaces...</p>
            </div>
          )}

          {spaces.error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
              <p className="text-red-600 text-lg">Error loading spaces: {spaces.error}</p>
            </div>
          )}

          {!spaces.loading && !spaces.error && spaceOptions.length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 animate-fade-in">
              {spaceOptions.map(space => (
                <SpaceCard
                  key={space}
                  space={space}
                  onViewDetails={onViewDetails}
                />
              ))}
            </div>
          )}

          {!spaces.loading && !spaces.error && spaceOptions.length === 0 && (
            <div className="text-center py-16">
              <p className="text-gray-500 text-lg">No spaces available</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default LandingPage
