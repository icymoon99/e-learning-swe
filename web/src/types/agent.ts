export type AgentStatus = 'active' | 'inactive' | 'deleted'
export type ExecutionStatus = 'running' | 'completed' | 'failed'

export interface AgentInstance {
  id: string
  code: string
  name: string
  description: string
  system_prompt: string
  model: string
  status: AgentStatus
  status_display: string
  metadata: Record<string, unknown>
  created_at: string
  updated_at: string
}

export interface AgentExecutionLog {
  id: string
  agent: string
  agent_code: string
  agent_name: string
  thread_id: string
  status: ExecutionStatus
  status_display: string
  events: unknown[]
  result: unknown
  error_message: string
  created_at: string
  updated_at: string
}

export interface AgentListParams {
  code?: string
  name?: string
  status?: AgentStatus
  page?: number
  page_size?: number
  ordering?: string
}

export interface ExecutionListParams {
  agent?: string
  status?: ExecutionStatus
  thread_id?: string
  page?: number
  page_size?: number
  ordering?: string
}

export interface CreateAgentParams {
  code: string
  name: string
  description?: string
  system_prompt?: string
  model?: string
  status?: AgentStatus
  metadata?: Record<string, unknown>
}
