import { get, post, put, del } from '@/utils/request'
import type {
  Q2Task,
  Q2Schedule,
  Q2QueueStatus,
  TaskListParams,
  CreateScheduleParams,
  UpdateScheduleParams,
} from '@/types/q2'
import type { PaginatedResponse } from '@/types/api'

// ==================== 任务 API ====================

export function getTaskListApi(params?: TaskListParams) {
  return get<PaginatedResponse<Q2Task>>('/q2/tasks/', { params })
}

export function getTaskDetailApi(id: string) {
  return get<Q2Task>(`/q2/tasks/${id}/`)
}

export function deleteTaskApi(id: string) {
  return del(`/q2/tasks/${id}/`)
}

// ==================== 失败任务 API ====================

export function getFailureListApi(params?: { page?: number; page_size?: number; search?: string }) {
  return get<PaginatedResponse<Q2Task>>('/q2/failures/', { params })
}

export function deleteFailureApi(id: string) {
  return del(`/q2/failures/${id}/`)
}

export function retryFailureApi(id: string) {
  return post<{ task_id: string; name: string }>(`/q2/failures/${id}/retry/`)
}

// ==================== 定时任务 API ====================

export function getScheduleListApi(params?: { page?: number; page_size?: number; search?: string }) {
  return get<PaginatedResponse<Q2Schedule>>('/q2/schedules/', { params })
}

export function createScheduleApi(data: CreateScheduleParams) {
  return post<Q2Schedule>('/q2/schedules/', data)
}

export function updateScheduleApi(id: number, data: UpdateScheduleParams) {
  return put<Q2Schedule>(`/q2/schedules/${id}/`, data)
}

export function deleteScheduleApi(id: number) {
  return del(`/q2/schedules/${id}/`)
}

// ==================== 队列 API ====================

export function getQueueStatusApi() {
  return get<Q2QueueStatus>('/q2/queue/status/')
}

export function toggleQueueApi(action: 'pause' | 'resume') {
  return post<{ action: string }>('/q2/queue/pause/', { action })
}
