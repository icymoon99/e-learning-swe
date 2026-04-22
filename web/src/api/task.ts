import { get, post, put, del } from '@/utils/request'
import type { PaginatedResponse } from '@/types/api'
import type {
  TaskItem,
  TaskDetail,
  ConversationItem,
  TaskListParams,
  CreateTaskParams,
  UpdateTaskParams,
  SendCommandParams,
} from '@/types/task'

const TASK_BASE = '/task/tasks/'

// 任务 CRUD
export function getTaskListApi(params?: TaskListParams) {
  return get<PaginatedResponse<TaskItem>>(TASK_BASE, { params })
}

export function getTaskDetailApi(id: string) {
  return get<TaskDetail>(`${TASK_BASE}${id}/`)
}

export function createTaskApi(data: CreateTaskParams) {
  return post<TaskDetail>(TASK_BASE, data)
}

export function updateTaskApi(id: string, data: UpdateTaskParams) {
  return put<TaskDetail>(`${TASK_BASE}${id}/`, data)
}

export function deleteTaskApi(id: string) {
  return del(`${TASK_BASE}${id}/`)
}

export function closeTaskApi(id: string) {
  return post<TaskDetail>(`${TASK_BASE}${id}/close/`)
}

// 对话流
export function getConversationListApi(taskId: string, params?: { page?: number; page_size?: number }) {
  return get<PaginatedResponse<ConversationItem>>(`${TASK_BASE}${taskId}/conversations/`, { params })
}

export function sendCommandApi(taskId: string, data: SendCommandParams) {
  return post<ConversationItem>(`${TASK_BASE}${taskId}/conversations/`, data)
}
