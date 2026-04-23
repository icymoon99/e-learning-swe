import { get, post, put, del } from '@/utils/request'
import type { PaginatedResponse } from '@/types/api'
import type {
  GitSource,
  GitSourceListParams,
  CreateGitSourceParams,
  UpdateGitSourceParams,
  RemoteRepo,
  RemoteBranchesResponse,
} from '@/types/gitSource'

const BASE_URL = '/git-source/sources/'

// 仓库源 CRUD
export function getGitSourceListApi(params?: GitSourceListParams) {
  return get<PaginatedResponse<GitSource>>(BASE_URL, { params })
}

export function getGitSourceDetailApi(id: string) {
  return get<GitSource>(`${BASE_URL}${id}/`)
}

export function createGitSourceApi(data: CreateGitSourceParams) {
  return post<GitSource>(BASE_URL, data)
}

export function updateGitSourceApi(id: string, data: UpdateGitSourceParams) {
  return put<GitSource>(`${BASE_URL}${id}/`, data)
}

export function deleteGitSourceApi(id: string) {
  return del(`${BASE_URL}${id}/`)
}

// 下拉选项（创建任务时选择仓库源）
export function getGitSourceDropdownApi() {
  return get<Array<{ id: string; name: string; platform: string }>>(`${BASE_URL}dropdown/`)
}

// 远程仓库查询（根据 Token 从 Git 平台获取）
export function getRemoteReposApi(params: { platform: string; token: string; api_url?: string }) {
  return get<{ repos: RemoteRepo[] }>(`${BASE_URL}repos/`, { params })
}

// 远程分支查询（根据 Token 从 Git 平台获取）
export function getRemoteBranchesApi(params: {
  platform: string
  token: string
  repo_full_name: string
  api_url?: string
}) {
  return get<RemoteBranchesResponse>(`${BASE_URL}branches/`, { params })
}
