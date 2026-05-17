export type Role = 'employee' | 'manager' | 'admin'

export interface User {
  id: number
  name: string
  email: string
  role: Role
  department_id: number | null
  manager_id: number | null
}

export type UoMType = 'min' | 'max' | 'timeline' | 'zero'
export type GoalStatus =
  | 'draft' | 'submitted' | 'returned' | 'resubmitted'
  | 'approved' | 'locked' | 'rejected'
export type ProgressStatus = 'not_started' | 'on_track' | 'completed'

export interface ThrustArea {
  id: number
  name: string
  department_id: number | null
}

export interface Goal {
  id: number
  employee_id: number
  thrust_area_id: number
  thrust_area: ThrustArea | null
  title: string
  description: string | null
  uom_type: UoMType
  target: number | null
  target_date: string | null
  weightage: number
  status: GoalStatus
  is_shared: boolean
  primary_owner_id: number | null
  primary_owner_name: string | null
  linked_employee_count: number | null
  rework_comment: string | null
  created_at: string
  updated_at: string
}

export interface Achievement {
  id: number
  goal_id: number
  cycle_id: number
  actual_value: number | null
  actual_date: string | null
  tracking_score: number | null
  goal_status: ProgressStatus
  updated_at: string
}

export interface GoalCycle {
  id: number
  name: string
  phase: 'goal_setting' | 'q1' | 'q2' | 'q3' | 'q4'
  window_open: string | null
  window_close: string | null
  is_active: boolean
  penalty_factor: number
}

export interface Checkin {
  id: number
  manager_id: number
  employee_id: number
  cycle_id: number
  comment_type: string | null
  comment_text: string | null
  is_completed: boolean
  completed_at: string | null
  created_at: string
}

export interface EscalationItem {
  escalation_id: number
  employee_id: number
  employee_name: string
  rule_type: string
  rule_name: string
  days_overdue: number
  level_reached: number
  triggered_at: string
  status: string
}

export interface WindowStatus {
  open_quarter: string | null
  open_cycle_id: number | null
  window_open: string | null
  window_close: string | null
  next_phase: string | null
  next_window_opens: string | null
}
