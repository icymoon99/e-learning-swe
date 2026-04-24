import { get, post, put, del } from '@/utils/request'
import type { PaginatedResponse } from '@/types/api'
import type {
  SandboxInstance,
  SandboxListParams,
  CreateSandboxParams,
  ExecuteCommandParams,
  ExecuteResult,
  SandboxTypesResponse,
} from '@/types/sandbox'

const BASE = '/sandbox/instances/'

export function getSandboxListApi(params?: SandboxListParams) {
  return get<PaginatedResponse<SandboxInstance>>(BASE, { params })
}

export function getSandboxDetailApi(id: string) {
  return get<SandboxInstance>(`${BASE}${id}/`)
}

export function createSandboxApi(data: CreateSandboxParams) {
  return post<SandboxInstance>(BASE, data)
}

export function updateSandboxApi(id: string, data: Partial<CreateSandboxParams>) {
  return put<SandboxInstance>(`${BASE}${id}/`, data)
}

export function deleteSandboxApi(id: string) {
  return del(`${BASE}${id}/`)
}

export function startSandboxApi(id: string) {
  return post<{ status: string }>(`${BASE}${id}/start/`)
}

export function stopSandboxApi(id: string) {
  return post<{ status: string }>(`${BASE}${id}/stop/`)
}

export function resetSandboxApi(id: string) {
  return post<{ message: string }>(`${BASE}${id}/reset/`)
}

export function executeCommandApi(id: string, data: ExecuteCommandParams) {
  return post<ExecuteResult>(`${BASE}${id}/execute/`, data)
}

// 沙箱类型 Schema

export function getSandboxTypesApi() {
  return get<SandboxTypesResponse>('/sandbox/types/')
}
