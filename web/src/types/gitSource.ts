export type GitPlatform = 'github' | 'gitee' | 'gitlab'

export interface GitSource {
  id: string
  name: string
  platform: GitPlatform
  platform_display: string
  repo_url: string
  default_branch: string
  description: string
  created_at: string
  updated_at: string
}

export interface GitSourceListParams {
  platform?: GitPlatform
  name?: string
  page?: number
  page_size?: number
  ordering?: string
  search?: string
}

export interface CreateGitSourceParams {
  name: string
  platform: GitPlatform
  repo_url: string
  token: string
  default_branch?: string
  description?: string
}

export interface UpdateGitSourceParams {
  name?: string
  platform?: GitPlatform
  repo_url?: string
  token?: string
  default_branch?: string
  description?: string
}
