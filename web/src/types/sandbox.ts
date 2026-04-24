// 沙箱类型

export type SandboxType = 'localdocker' | 'remotedocker' | 'localsystem' | 'remotesystem'
export type SandboxStatus = 'active' | 'inactive' | 'error'

export interface SandboxInstance {
  id: string
  name: string
  type: SandboxType
  type_display: string
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

// 沙箱类型 Schema（用于动态表单生成）

export interface SandboxTypeSchema {
  label: string
  fields: Record<string, {
    type: string
    required: boolean
    default?: unknown
    label: string
    hint: string
  }>
}

export interface SandboxTypesResponse {
  types: Record<string, SandboxTypeSchema>
}
