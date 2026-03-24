export interface Issue {
  issue_id: string
  title: string
  project: string
  status: 'Open' | 'In Progress' | 'Blocked' | 'Done'
  priority: 'Low' | 'Medium' | 'High' | 'Critical'
  days_open: number
  assignee: string
  fix_version: string
  fix_version_released: boolean
  fix_version_date: string
  space: string
  type: 'Bug' | 'Feature' | 'Task' | 'Improvement'
  sprint?: string
}

export interface IssueWithScore extends Issue {
  health_score: number
  rag: 'Red' | 'Amber' | 'Green'
  bottleneck: boolean
  bottleneck_reason: string | null
}

export interface HealthSummary {
  team_score: number
  rag: 'Red' | 'Amber' | 'Green' | 'None'
  total_issues: number
  issues: IssueWithScore[]
}

export interface ApiResponse<T> {
  data: T
  meta: { generated_at: string }
}

export type WorkloadDistribution = {
  Critical: number
  High: number
  Medium: number
  Low: number
}

export interface SpaceInfo {
  [space: string]: string[]
}

export interface ProjectMapping {
  [name: string]: string
}

export interface SpaceHealthSummary {
  space: string
  team_score: number
  rag: 'Red' | 'Amber' | 'Green'
  total_issues: number
  red: number
  amber: number
  green: number
}
