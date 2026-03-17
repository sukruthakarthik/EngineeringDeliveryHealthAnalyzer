export interface Issue {
  issue_id: string
  title: string
  status: 'Open' | 'In Progress' | 'Blocked' | 'Done'
  priority: 'Low' | 'Medium' | 'High' | 'Critical'
  days_open: number
  assignee: string
  fix_version: string
  fix_version_released: boolean
  space: string
  type: 'Bug' | 'Feature' | 'Task' | 'Improvement'
}

export interface IssueWithScore extends Issue {
  health_score: number
  rag: 'Red' | 'Amber' | 'Green'
  bottleneck: boolean
  bottleneck_reason: string | null
}

export interface HealthSummary {
  team_score: number
  rag: 'Red' | 'Amber' | 'Green'
  total_issues: number
  issues: IssueWithScore[]
}

export interface ReleaseHealth {
  fix_version: string
  released: boolean
  space: string
  score: number
  rag: 'Red' | 'Amber' | 'Green'
  total_issues: number
  open_issues: number
  in_progress_issues: number
  blocked_issues: number
  done_issues: number
  bottleneck_count: number
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
