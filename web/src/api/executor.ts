import { get, put } from '@/utils/request'
import type { PaginatedResponse } from '@/types/api'
import type { Executor, UpdateExecutorParams } from '@/types/executor'

const EXECUTOR_BASE = '/agent/executors/'

/** 获取执行器列表 */
export function getExecutorListApi(params?: { page?: number; page_size?: number }) {
  return get<PaginatedResponse<Executor>>(EXECUTOR_BASE, { params })
}

/** 获取执行器详情 */
export function getExecutorDetailApi(id: string) {
  return get<Executor>(`${EXECUTOR_BASE}${id}/`)
}

/** 更新执行器 */
export function updateExecutorApi(id: string, data: UpdateExecutorParams) {
  return put<Executor>(`${EXECUTOR_BASE}${id}/`, data)
}

/** 获取所有执行器类型 schema */
export function getExecutorTypesApi() {
  return get<Record<string, unknown>>(`${EXECUTOR_BASE}types/`)
}
