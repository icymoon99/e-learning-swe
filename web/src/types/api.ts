// API 通用响应格式（对应后端 ApiResponse）
export interface ApiResponse<T = unknown> {
  code: number
  message: string
  content: T
}

// 分页响应结构
export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

// 分页参数
export interface PaginationParams {
  page?: number
  page_size?: number
}

// 通用列表参数
export interface ListParams extends PaginationParams {
  search?: string
  ordering?: string
}
