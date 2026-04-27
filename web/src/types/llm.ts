export type LLMProviderCode = 'openai' | 'anthropic' | 'tongyi' | 'zhipu' | 'kimi' | string

export interface LLMProvider {
  id: string
  code: string
  name: string
  base_url: string
  resolved_base_url: string
  enabled: boolean
  description: string
  created_at: string
  updated_at: string
  api_key_configured: boolean
}

export interface CreateLLMProviderParams {
  code: string
  name: string
  base_url?: string
  api_key_encrypted?: string
  enabled?: boolean
  description?: string
}

export interface LLMModel {
  id: string
  provider: string
  provider_name: string
  provider_code: string
  model_code: string
  display_name: string
  context_window: number
  max_output_tokens: number
  enabled: boolean
  sort_order: number
  description: string
  created_at: string
  updated_at: string
}

export interface CreateLLMModelParams {
  provider: string
  model_code: string
  display_name?: string
  context_window?: number
  max_output_tokens?: number
  enabled?: boolean
  sort_order?: number
  description?: string
}

export interface LLMModelDropdown {
  id: string
  model_code: string
  display_name: string
  provider_name: string
  provider_code: string
  enabled: boolean
}

export interface LLMProviderListParams {
  enabled?: boolean
  search?: string
  page?: number
  page_size?: number
  ordering?: string
}

export interface LLMModelListParams {
  provider?: string
  enabled?: boolean
  search?: string
  page?: number
  page_size?: number
  ordering?: string
}
