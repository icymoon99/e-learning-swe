// Django-Q2 任务
export interface Q2Task {
  id: string
  name: string
  func: string
  args: string | null
  kwargs: Record<string, unknown> | null
  result: unknown
  started: string | null
  stopped: string | null
  success: boolean | null
  attempt_count: number
}

// 定时任务
export interface Q2Schedule {
  id: number
  name: string
  func: string
  schedule_type: string
  minutes: number | null
  repeats: number
  next_run: string | null
  cron: string | null
  task: string | null
  args?: string
  kwargs?: Record<string, unknown>
}

// 队列状态
export interface Q2QueueStatus {
  worker_running: boolean
  queue_size: number
  tasks_running: number
  tasks_failed: number
}

// 任务列表参数
export interface TaskListParams {
  status?: 'running' | 'success' | 'failure'
  page?: number
  page_size?: number
  search?: string
}

// 定时任务创建参数
export interface CreateScheduleParams {
  name: string
  func: string
  schedule_type: string
  minutes?: number | null
  repeats?: number
  args?: string
  kwargs?: Record<string, unknown>
  cron?: string
}

// 定时任务更新参数
export type UpdateScheduleParams = Partial<CreateScheduleParams>
