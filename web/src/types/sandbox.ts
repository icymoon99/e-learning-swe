// 沙箱类型

export type SandboxType = 'localdocker' | 'remotedocker' | 'localsystem' | 'remotesystem'
export type SandboxStatus = 'active' | 'inactive' | 'error'

export interface SandboxInstance {
  id: string
  name: string
  type: SandboxType
  type_display: string
  root_path: string
  status: SandboxStatus
  status_display: string
  metadata: Record<string, unknown>
  created_at: string
  updated_at: string
}

export interface SandboxListParams {
  type?: SandboxType
  status?: SandboxStatus
  name?: string
  page?: number
  page_size?: number
  ordering?: string
}

export interface CreateSandboxParams {
  name: string
  type: SandboxType
  root_path: string
  metadata: Record<string, unknown>
}

export interface ExecuteCommandParams {
  command: string
  timeout?: number
}

export interface ExecuteResult {
  output: string
  exit_code: number
  truncated: boolean
}
