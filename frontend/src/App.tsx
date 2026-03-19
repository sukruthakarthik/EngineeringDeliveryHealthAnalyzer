import { useHealthScore } from './hooks/useHealthScore'
import { useBottlenecks } from './hooks/useBottlenecks'
import { useFixVersions } from './hooks/useFixVersions'
import type { FixVersion } from './hooks/useFixVersions'
import { useActiveRelease } from './hooks/useActiveRelease'
import HealthScoreCard from './components/HealthScoreCard'
import BottleneckTable from './components/BottleneckTable'
import WorkloadDistribution from './components/WorkloadDistribution'
import Filters, { FilterOptions } from './components/Filters'
import LandingPage from './components/LandingPage'
import ExportPrintButtons from './components/ExportPrintButtons'
import { useEffect, useState, useMemo } from 'react'
import type { IssueWithScore, WorkloadDistribution as WorkloadData } from './types/api'

export default function App() {
  const [lastUpdated, setLastUpdated] = useState(new Date())
  const [selectedSpace, setSelectedSpace] = useState<string>('')
  const [showDashboard, setShowDashboard] = useState(false)
  const [filters, setFilters] = useState<FilterOptions>({
    status: [],
    priority: [],
    sprint: [],
    rag: []
  })

  // Pass selectedSpace to hooks — backend handles space filtering server-side
  const healthScore = useHealthScore(selectedSpace || undefined)
  const currentFixVersion = filters.sprint.length === 1 ? filters.sprint[0] : undefined
  const bottlenecks = useBottlenecks(selectedSpace || undefined, currentFixVersion)

  useEffect(() => {
    const interval = setInterval(() => {
      setLastUpdated(new Date())
    }, 5 * 60 * 1000)
    return () => clearInterval(interval)
  }, [])

  const handleViewDetails = (space: string, release?: string) => {
    setSelectedSpace(space)
    setFilters(f => ({
      ...f,
      sprint: release ? [release] : [],
    }))
    setShowDashboard(true)
  }

  const handleGoHome = () => {
    setShowDashboard(false)
    setSelectedSpace('')
    setFilters({ status: [], priority: [], sprint: [], rag: [] })
  }

  // Fetch fix versions for the selected space from JIRA API
  const fixVersions = useFixVersions(selectedSpace || undefined)
  const availableSprints = fixVersions.map(v => v.name)

  // Fetch the active (unreleased) release from the dedicated JIRA API
  const activeRelease = useActiveRelease(selectedSpace || undefined)

  // Auto-select the active release as the sprint filter when entering the dashboard
  // (only if no sprint was explicitly passed from the landing page)
  useEffect(() => {
    if (activeRelease && filters.sprint.length === 0) {
      setFilters(f => ({ ...f, sprint: [activeRelease.name] }))
    }
  }, [activeRelease]) // eslint-disable-line react-hooks/exhaustive-deps

  // Derive current release: prefer the active sprint filter, else the active release from API.
  const currentRelease = useMemo((): FixVersion | null => {
    if (filters.sprint.length === 1) {
      return (
        fixVersions.find(v => v.name === filters.sprint[0]) ??
        { name: filters.sprint[0], released: false, releaseDate: '' }
      )
    }
    // No sprint filter — show the active release from the dedicated API
    return activeRelease
  }, [fixVersions, filters.sprint, activeRelease])

  // Apply additional filters (status, priority, sprint, rag) client-side
  const filteredHealthScore = useMemo(() => {
    if (!healthScore.data) return healthScore

    const hasFilters =
      filters.status.length > 0 ||
      filters.priority.length > 0 ||
      filters.sprint.length > 0 ||
      filters.rag.length > 0

    if (!hasFilters) return healthScore

    const filteredIssues = healthScore.data.data.issues.filter((issue: IssueWithScore) => {
      if (filters.status.length > 0 && !filters.status.includes(issue.status)) return false
      if (filters.priority.length > 0 && !filters.priority.includes(issue.priority)) return false
      if (filters.sprint.length > 0 && !filters.sprint.includes(issue.fix_version || 'Unassigned')) return false
      if (filters.rag.length > 0 && !filters.rag.includes(issue.rag)) return false
      return true
    })

    const activeFiltered = filteredIssues.filter(i => i.status !== 'Done')
    const teamScore = activeFiltered.length === 0 ? 0
      : Math.round(activeFiltered.reduce((sum, i) => sum + i.health_score, 0) / activeFiltered.length)

    const classifyRAG = (score: number) => {
      if (filteredIssues.length === 0) return 'None'
      if (score >= 75) return 'Green'
      if (score >= 50) return 'Amber'
      return 'Red'
    }

    return {
      ...healthScore,
      data: {
        ...healthScore.data,
        data: {
          ...healthScore.data.data,
          team_score: teamScore,
          rag: classifyRAG(teamScore) as 'Red' | 'Amber' | 'Green' | 'None',
          total_issues: filteredIssues.length,
          issues: filteredIssues
        }
      }
    }
  }, [healthScore, filters])

  // Apply additional filters to bottlenecks (already filtered by space server-side)
  const filteredBottlenecks = useMemo(() => {
    if (!bottlenecks.data) return bottlenecks

    const hasFilters =
      filters.status.length > 0 ||
      filters.priority.length > 0 ||
      filters.sprint.length > 0 ||
      filters.rag.length > 0

    if (!hasFilters) return bottlenecks

    const filteredData = bottlenecks.data.data.filter((issue: IssueWithScore) => {
      if (filters.status.length > 0 && !filters.status.includes(issue.status)) return false
      if (filters.priority.length > 0 && !filters.priority.includes(issue.priority)) return false
      if (filters.sprint.length > 0 && !filters.sprint.includes(issue.fix_version || 'Unassigned')) return false
      if (filters.rag.length > 0 && !filters.rag.includes(issue.rag)) return false
      return true
    })

    return {
      ...bottlenecks,
      data: {
        ...bottlenecks.data,
        data: filteredData
      }
    }
  }, [bottlenecks, filters])

  // Derive workload from already-filtered health score issues (stays in sync)
  const filteredWorkload = useMemo((): WorkloadData => {
    const issues = (filteredHealthScore.data?.data.issues ?? []).filter(
      (i: IssueWithScore) => i.status !== 'Done',
    )
    const dist: WorkloadData = { Critical: 0, High: 0, Medium: 0, Low: 0 }
    issues.forEach((i: IssueWithScore) => { dist[i.priority]++ })
    return dist
  }, [filteredHealthScore])

  // Show landing page if dashboard is not open
  if (!showDashboard) {
    return <LandingPage onViewDetails={handleViewDetails} />
  }

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <header className="mb-8">
        <div className="flex items-start justify-between flex-wrap gap-4">
          <div>
            <div className="flex items-center gap-4 mb-2">
              <button
                onClick={handleGoHome}
                className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors flex items-center gap-2 print:hidden"
                title="Go to home"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                </svg>
                Home
              </button>
              <h1 className="text-3xl font-bold text-gray-800">Engineering Delivery Health Analyzer</h1>
            </div>
            <p className="text-gray-500 mt-1">Real-time delivery risk and workload visibility</p>
            <p className="text-sm text-blue-600 font-semibold mt-1">Current Space: {selectedSpace}</p>
            <div className="flex items-center gap-2 mt-0.5">
              <span className="text-sm text-gray-500">Release Version:</span>
              <select
                value={filters.sprint.length === 1 ? filters.sprint[0] : ''}
                onChange={e => {
                  const name = e.target.value
                  setFilters(f => ({ ...f, sprint: name ? [name] : [] }))
                }}
                className="text-sm font-semibold text-gray-700 border border-gray-300 rounded-md px-2 py-1 bg-white focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-blue-400 print:border-0"
              >
                {availableSprints.map(name => (
                  <option key={name} value={name}>{name}</option>
                ))}
                <option value="">All Releases</option>
              </select>
              {filters.sprint.length === 1 && currentRelease && (
                currentRelease.released && currentRelease.releaseDate && new Date(currentRelease.releaseDate) <= new Date() ? (
                  <span className="inline-flex items-center gap-1 text-xs font-medium bg-gray-100 text-gray-500 px-2 py-0.5 rounded-full">
                    <span className="w-1.5 h-1.5 rounded-full bg-gray-400"></span>
                    Completed{currentRelease.releaseDate ? ` · ${currentRelease.releaseDate}` : ''}
                  </span>
                ) : (
                  <span className="inline-flex items-center gap-1 text-xs font-medium bg-green-50 text-green-700 px-2 py-0.5 rounded-full">
                    <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse"></span>
                    Active
                  </span>
                )
              )}
            </div>
          </div>
          <div className="flex flex-col items-end gap-3">
            <div className="text-right text-sm">
              <div className="text-gray-400">
                <span className="inline-block w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></span>
                Live data
              </div>
              <div className="text-gray-500 mt-1">
                Auto-refresh: 5 min
              </div>
              <div className="text-xs text-gray-400 mt-1">
                Updated: {lastUpdated.toLocaleTimeString()}
              </div>
            </div>
            <ExportPrintButtons 
              data={filteredHealthScore.data?.data.issues || []} 
              filename={`dashboard-${selectedSpace.replace(/\s+/g, '-')}`}
            />
          </div>
        </div>
      </header>

      <Filters 
        filters={filters} 
        onChange={setFilters}
        totalIssues={healthScore.data?.data.issues.length}
        filteredIssues={filteredHealthScore.data?.data.issues.length}
      />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <HealthScoreCard {...filteredHealthScore} />
        <WorkloadDistribution workload={filteredWorkload} selectedPriorities={filters.priority} />
      </div>

      <BottleneckTable
        {...filteredBottlenecks}
        isCompletedRelease={
          !!(currentRelease?.released && currentRelease.releaseDate && new Date(currentRelease.releaseDate) <= new Date())
        }
      />
    </div>
  )
}
