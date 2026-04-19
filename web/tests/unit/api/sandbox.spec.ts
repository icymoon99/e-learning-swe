import { describe, it, expect, vi, beforeEach } from 'vitest'
import * as sandboxApi from '@/api/sandbox'
import * as request from '@/utils/request'

// Mock request utils
vi.mock('@/utils/request', () => ({
  get: vi.fn((url, config) => ({ url, params: config?.params })),
  post: vi.fn((url, data) => ({ url, data })),
  put: vi.fn((url, data) => ({ url, data })),
  del: vi.fn(url => ({ url })),
}))

describe('Sandbox API', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('getSandboxListApi', () => {
    it('should call GET with no params', () => {
      sandboxApi.getSandboxListApi()
      expect(request.get).toHaveBeenCalledWith('/sandbox/instances/', { params: undefined })
    })

    it('should call GET with filter params', () => {
      sandboxApi.getSandboxListApi({ type: 'localdocker', status: 'active', page: 2 })
      expect(request.get).toHaveBeenCalledWith('/sandbox/instances/', {
        params: { type: 'localdocker', status: 'active', page: 2 },
      })
    })

    it('should call GET with name search', () => {
      sandboxApi.getSandboxListApi({ name: 'test', page: 1, page_size: 10 })
      expect(request.get).toHaveBeenCalledWith('/sandbox/instances/', {
        params: { name: 'test', page: 1, page_size: 10 },
      })
    })
  })

  describe('getSandboxDetailApi', () => {
    it('should call GET with instance id', () => {
      sandboxApi.getSandboxDetailApi('01abc123')
      expect(request.get).toHaveBeenCalledWith('/sandbox/instances/01abc123/')
    })
  })

  describe('createSandboxApi', () => {
    it('should call POST with sandbox data', () => {
      const data = {
        name: 'new-sandbox',
        type: 'localdocker' as const,
        root_path: '/workspace',
        metadata: { image: 'sandbox:latest' },
      }
      sandboxApi.createSandboxApi(data)
      expect(request.post).toHaveBeenCalledWith('/sandbox/instances/', data)
    })
  })

  describe('updateSandboxApi', () => {
    it('should call PUT with id and partial data', () => {
      sandboxApi.updateSandboxApi('01abc123', { name: 'updated-name' })
      expect(request.put).toHaveBeenCalledWith('/sandbox/instances/01abc123/', { name: 'updated-name' })
    })
  })

  describe('deleteSandboxApi', () => {
    it('should call DELETE with id', () => {
      sandboxApi.deleteSandboxApi('01abc123')
      expect(request.del).toHaveBeenCalledWith('/sandbox/instances/01abc123/')
    })
  })

  describe('startSandboxApi', () => {
    it('should call POST start endpoint', () => {
      sandboxApi.startSandboxApi('01abc123')
      expect(request.post).toHaveBeenCalledWith('/sandbox/instances/01abc123/start/')
    })
  })

  describe('stopSandboxApi', () => {
    it('should call POST stop endpoint', () => {
      sandboxApi.stopSandboxApi('01abc123')
      expect(request.post).toHaveBeenCalledWith('/sandbox/instances/01abc123/stop/')
    })
  })

  describe('resetSandboxApi', () => {
    it('should call POST reset endpoint', () => {
      sandboxApi.resetSandboxApi('01abc123')
      expect(request.post).toHaveBeenCalledWith('/sandbox/instances/01abc123/reset/')
    })
  })

  describe('executeCommandApi', () => {
    it('should call POST execute endpoint with command', () => {
      sandboxApi.executeCommandApi('01abc123', { command: 'echo hello' })
      expect(request.post).toHaveBeenCalledWith('/sandbox/instances/01abc123/execute/', { command: 'echo hello' })
    })

    it('should call POST execute endpoint with timeout', () => {
      sandboxApi.executeCommandApi('01abc123', { command: 'sleep 10', timeout: 30 })
      expect(request.post).toHaveBeenCalledWith('/sandbox/instances/01abc123/execute/', {
        command: 'sleep 10',
        timeout: 30,
      })
    })
  })
})
