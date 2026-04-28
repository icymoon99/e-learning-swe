/** 执行器字段定义（来自后端 schema） */
export interface ExecutorFieldDef {
  type: 'string' | 'password' | 'number' | 'textarea'
  required: boolean
  label: string
  hint: string
  value: string | number
}

/** 执行器分组 Schema（env_vars / cli_args） */
export interface ExecutorGroupSchema {
  [fieldKey: string]: ExecutorFieldDef
}

/** 执行器完整 Schema */
export interface ExecutorSchema {
  env_vars: ExecutorGroupSchema
  cli_args: ExecutorGroupSchema
  [groupKey: string]: ExecutorGroupSchema
}

/** 执行器实例 */
export interface Executor {
  id: string
  code: string
  name: string
  enabled: boolean
  timeout: number
  metadata_schema: ExecutorSchema
  /** 前端使用的临时状态 */
  _saving?: boolean
}

/** 更新执行器参数 */
export interface UpdateExecutorParams {
  enabled: boolean
  metadata_schema_input: ExecutorSchema
}
