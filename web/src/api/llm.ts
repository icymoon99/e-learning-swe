import { get, post, put, patch, del } from '@/utils/request'
import type { PaginatedResponse } from '@/types/api'
import type {
  LLMProvider,
  LLMModel,
  LLMModelDropdown,
  CreateLLMProviderParams,
  CreateLLMModelParams,
  LLMProviderListParams,
  LLMModelListParams,
} from '@/types/llm'

const PROVIDER_BASE = '/llm/providers/'
const MODEL_BASE = '/llm/models/'

// LLM Provider CRUD
export function getLLMProviderListApi(params?: LLMProviderListParams) {
  return get<PaginatedResponse<LLMProvider>>(PROVIDER_BASE, { params })
}

export function getLLMProviderDetailApi(id: string) {
  return get<LLMProvider>(`${PROVIDER_BASE}${id}/`)
}

export function createLLMProviderApi(data: CreateLLMProviderParams) {
  return post<LLMProvider>(PROVIDER_BASE, data)
}

export function updateLLMProviderApi(id: string, data: Partial<CreateLLMProviderParams>) {
  return patch<LLMProvider>(`${PROVIDER_BASE}${id}/`, data)
}

export function deleteLLMProviderApi(id: string) {
  return del(`${PROVIDER_BASE}${id}/`)
}

// LLM Model CRUD
export function getLLMModelListApi(params?: LLMModelListParams) {
  return get<PaginatedResponse<LLMModel>>(MODEL_BASE, { params })
}

export function getLLMModelDetailApi(id: string) {
  return get<LLMModel>(`${MODEL_BASE}${id}/`)
}

export function createLLMModelApi(data: CreateLLMModelParams) {
  return post<LLMModel>(MODEL_BASE, data)
}

export function updateLLMModelApi(id: string, data: Partial<CreateLLMModelParams>) {
  return patch<LLMModel>(`${MODEL_BASE}${id}/`, data)
}

export function deleteLLMModelApi(id: string) {
  return del(`${MODEL_BASE}${id}/`)
}

// LLM Model Dropdown
export function getLLMModelDropdownApi() {
  return get<LLMModelDropdown[]>(`${MODEL_BASE}dropdown/`)
}
