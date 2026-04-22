export type TaskStatus = 'open' | 'closed'
export type ExecutionStatus = 'running' | 'completed' | 'failed'
export type CommentType = 'user' | 'ai' | 'system'

export interface GitSourceNested {
  id: string
  name: string
  platform: string
  platform_display: string
  repo_url: string
}

export interface TaskItem {
  id: string
  title: string
  git_source_name: string
  platform: string
  status: TaskStatus
  status_display: string
  source_branch: string
  latest_execution_status: ExecutionStatus | null
  latest_execution_agent: string | null
  created_at: string
  updated_at: string
}

export interface TaskDetail {
  id: string
  title: string
  description: string
  git_source: GitSourceNested | null
  source_branch: string
  status: TaskStatus
  status_display: string
  latest_execution_status: ExecutionStatus | null
  created_at: string
  updated_at: string
}

export interface ConversationItem {
  id: string
  content: string
  comment_type: CommentType
  comment_type_display: string
  agent_code: string | null
  agent_name: string | null
  execution_log_id: string | null
  execution_status: ExecutionStatus | null
  created_at: string
}

export interface TaskListParams {
  status?: TaskStatus
  git_source?: string
  search?: string
  page?: number
  page_size?: number
  ordering?: string
}

export interface CreateTaskParams {
  title: string
  description?: string
  git_source_id?: string | null
  source_branch?: string
}

export interface UpdateTaskParams {
  title?: string
  description?: string
  source_branch?: string
}

export interface SendCommandParams {
  content: string
  agent_code: string
}
