import { describe, it, expect } from 'vitest'
import type {
  SandboxInstance,
  SandboxListParams,
  CreateSandboxParams,
  ExecuteCommandParams,
  ExecuteResult,
  SandboxType,
  SandboxStatus,
} from '@/types/sandbox'

describe('Sandbox Types', () => {
  describe('SandboxType', () => {
    it('should accept valid type values', () => {
      const types: SandboxType[] = ['localdocker', 'remotedocker', 'localsystem', 'remotesystem']
      expect(types).toHaveLength(4)
    })
  })

  describe('SandboxStatus', () => {
    it('should accept valid status values', () => {
      const statuses: SandboxStatus[] = ['active', 'inactive', 'error']
      expect(statuses).toHaveLength(3)
    })
  })

  describe('SandboxInstance', () => {
    it('should create a valid instance object', () => {
      const instance: SandboxInstance = {
        id: '01abc123',
        name: 'test-sandbox',
        type: 'localdocker',
        type_display: '本地 Docker',
        root_path: '/workspace',
        status: 'active',
        status_display: '活跃',
        metadata: { image: 'sandbox:latest' },
        created_at: '2026-04-19 10:00:00',
        updated_at: '2026-04-19 10:00:00',
      }
      expect(instance.name).toBe('test-sandbox')
      expect(instance.type).toBe('localdocker')
      expect(instance.status).toBe('active')
    })

    it('should have metadata as object', () => {
      const instance: SandboxInstance = {
        id: '01abc123',
        name: 'test',
        type: 'localsystem',
        type_display: '本地系统',
        root_path: '/tmp',
        status: 'inactive',
        status_display: '未激活',
        metadata: {},
        created_at: '2026-04-19 10:00:00',
        updated_at: '2026-04-19 10:00:00',
      }
      expect(typeof instance.metadata).toBe('object')
      expect(Array.isArray(instance.metadata)).toBe(false)
    })
  })

  describe('CreateSandboxParams', () => {
    it('should create valid params for localdocker', () => {
      const params: CreateSandboxParams = {
        name: 'new-sandbox',
        type: 'localdocker',
        root_path: '/workspace',
        metadata: { image: 'sandbox:latest', work_dir: '/workspace' },
      }
      expect(params.name).toBe('new-sandbox')
      expect(params.metadata.image).toBe('sandbox:latest')
    })

    it('should create valid params for remotedocker with ssh_host', () => {
      const params: CreateSandboxParams = {
        name: 'remote-sandbox',
        type: 'remotedocker',
        root_path: '/home/sandbox',
        metadata: { ssh_host: '192.168.1.100', ssh_port: 22, image: 'sandbox:latest' },
      }
      expect(params.metadata.ssh_host).toBe('192.168.1.100')
    })
  })

  describe('ExecuteCommandParams', () => {
    it('should create valid command params', () => {
      const params: ExecuteCommandParams = {
        command: 'echo hello',
        timeout: 30,
      }
      expect(params.command).toBe('echo hello')
      expect(params.timeout).toBe(30)
    })

    it('should allow optional timeout', () => {
      const params: ExecuteCommandParams = {
        command: 'ls -la',
      }
      expect(params.timeout).toBeUndefined()
    })
  })

  describe('ExecuteResult', () => {
    it('should create valid result', () => {
      const result: ExecuteResult = {
        output: 'hello\nworld\n',
        exit_code: 0,
        truncated: false,
      }
      expect(result.exit_code).toBe(0)
      expect(result.truncated).toBe(false)
    })
  })

  describe('SandboxListParams', () => {
    it('should create valid filter params', () => {
      const params: SandboxListParams = {
        type: 'localdocker',
        status: 'active',
        name: 'test',
        page: 1,
        page_size: 20,
        ordering: '-created_at',
      }
      expect(params.type).toBe('localdocker')
      expect(params.page).toBe(1)
    })
  })
})
