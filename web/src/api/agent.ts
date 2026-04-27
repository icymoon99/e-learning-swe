import { get, post, put, del } from '@/utils/request'
import type { PaginatedResponse } from '@/types/api'
import type {
  AgentInstance,
  AgentExecutionLog,
  AgentListParams,
  ExecutionListParams,
  CreateAgentParams,
  ExecutorOption,
} from '@/types/agent'

const AGENT_BASE = '/agent/agents/'
const EXEC_BASE = '/agent/execution-logs/'
const EXECUTOR_BASE = '/agent/executors/'

// Agent CRUD
export function getAgentListApi(params?: AgentListParams) {
  return get<PaginatedResponse<AgentInstance>>(AGENT_BASE, { params })
}

export function getAgentDetailApi(id: string) {
  return get<AgentInstance>(`${AGENT_BASE}${id}/`)
}

export function createAgentApi(data: CreateAgentParams) {
  return post<AgentInstance>(AGENT_BASE, data)
}

export function updateAgentApi(id: string, data: Partial<CreateAgentParams>) {
  return put<AgentInstance>(`${AGENT_BASE}${id}/`, data)
}

export function deleteAgentApi(id: string) {
  return del(`${AGENT_BASE}${id}/`)
}

// Agent Execution Logs
export function getExecutionListApi(params?: ExecutionListParams) {
  return get<PaginatedResponse<AgentExecutionLog>>(EXEC_BASE, { params })
}

export function getExecutionDetailApi(id: string) {
  return get<AgentExecutionLog>(`${EXEC_BASE}${id}/`)
}

export function getAgentExecutionsApi(agentId: string, params?: ExecutionListParams) {
  return get<PaginatedResponse<AgentExecutionLog>>(EXEC_BASE, {
    params: { ...params, agent: agentId },
  })
}

// Executors
export function getExecutorListApi(params?: { page?: number; page_size?: number }) {
  return get<PaginatedResponse<ExecutorOption>>(EXECUTOR_BASE, { params })
}
