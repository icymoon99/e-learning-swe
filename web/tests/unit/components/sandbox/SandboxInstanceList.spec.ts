import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import SandboxInstanceList from '@/views/sandbox/instances/index.vue'

// Mock API
vi.mock('@/api/sandbox', () => ({
  getSandboxListApi: vi.fn(() =>
    Promise.resolve({
      data: {
        content: {
          count: 2,
          next: null,
          previous: null,
          results: [
            {
              id: '01',
              name: 'docker-1',
              type: 'localdocker',
              type_display: '本地 Docker',
              root_path: '/workspace',
              status: 'active',
              status_display: '活跃',
              metadata: {},
              created_at: '2026-04-19 10:00:00',
              updated_at: '2026-04-19 10:00:00',
            },
          ],
        },
      },
    }),
  ),
  getSandboxDetailApi: vi.fn(() =>
    Promise.resolve({
      data: {
        content: {
          id: '01',
          name: 'detail-test',
          type: 'localdocker',
          type_display: '本地 Docker',
          root_path: '/workspace',
          status: 'active',
          status_display: '活跃',
          metadata: { image: 'sandbox:latest' },
          created_at: '2026-04-19 10:00:00',
          updated_at: '2026-04-19 10:00:00',
        },
      },
    }),
  ),
  deleteSandboxApi: vi.fn(() => Promise.resolve()),
  startSandboxApi: vi.fn(() => Promise.resolve()),
  stopSandboxApi: vi.fn(() => Promise.resolve()),
  resetSandboxApi: vi.fn(() => Promise.resolve()),
  createSandboxApi: vi.fn(() => Promise.resolve({ data: { content: { id: '03' } } })),
  updateSandboxApi: vi.fn(() => Promise.resolve({ data: { content: { id: '01' } } })),
  executeCommandApi: vi.fn(() =>
    Promise.resolve({
      data: { content: { output: 'hello\n', exit_code: 0, truncated: false } },
    }),
  ),
}))

// Mock Element Plus
vi.mock('element-plus', async () => {
  const actual = await vi.importActual('element-plus')
  return {
    ...actual,
    ElMessage: {
      error: vi.fn(),
      success: vi.fn(),
      warning: vi.fn(),
      info: vi.fn(),
    },
    ElMessageBox: {
      confirm: vi.fn(() => Promise.resolve('confirm')),
    },
  }
})

// Stub for Element Plus table column (scoped slots cause issues with stubs)
const StubTableColumn = { template: '<div></div>', props: ['label', 'prop', 'width', 'minWidth', 'fixed'] }

describe('SandboxInstanceList', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  describe('page rendering', () => {
    it('should render page title', async () => {
      const wrapper = mount(SandboxInstanceList, {
        global: {
          stubs: {
            ElTable: { template: '<div class="el-table"><slot /></div>' },
            ElTableColumn: StubTableColumn,
            ElInput: { template: '<input />' },
            ElSelect: { template: '<select />' },
            ElOption: { template: '<option />' },
            ElButton: { template: '<button><slot /></button>' },
            ElIcon: { template: '<span />' },
            ElTag: { template: '<span><slot /></span>' },
            ElPagination: { template: '<div />' },
            ElDialog: { template: '<div />' },
            ElDrawer: { template: '<div />' },
            ElForm: { template: '<form />' },
            ElFormItem: { template: '<div />' },
            ElInputNumber: { template: '<input type="number" />' },
            ElDescriptions: { template: '<div />' },
            ElDescriptionsItem: { template: '<div />' },
          },
        },
      })
      expect(wrapper.text()).toContain('沙箱实例管理')
    })

    it('should render create and refresh buttons', async () => {
      const wrapper = mount(SandboxInstanceList, {
        global: {
          stubs: {
            ElTable: { template: '<div class="el-table"><slot /></div>' },
            ElTableColumn: StubTableColumn,
            ElInput: { template: '<input />' },
            ElSelect: { template: '<select />' },
            ElOption: { template: '<option />' },
            ElButton: { template: '<button><slot /></button>' },
            ElIcon: { template: '<span />' },
            ElTag: { template: '<span><slot /></span>' },
            ElPagination: { template: '<div />' },
            ElDialog: { template: '<div />' },
            ElDrawer: { template: '<div />' },
            ElForm: { template: '<form />' },
            ElFormItem: { template: '<div />' },
            ElInputNumber: { template: '<input type="number" />' },
            ElDescriptions: { template: '<div />' },
            ElDescriptionsItem: { template: '<div />' },
          },
        },
      })
      expect(wrapper.text()).toContain('刷新')
      expect(wrapper.text()).toContain('创建实例')
    })
  })

  describe('data loading', () => {
    it('should call loadData on mount', async () => {
      mount(SandboxInstanceList, {
        global: {
          stubs: {
            ElTable: { template: '<div class="el-table"><slot /></div>' },
            ElTableColumn: StubTableColumn,
            ElInput: { template: '<input />' },
            ElSelect: { template: '<select />' },
            ElOption: { template: '<option />' },
            ElButton: { template: '<button><slot /></button>' },
            ElIcon: { template: '<span />' },
            ElTag: { template: '<span><slot /></span>' },
            ElPagination: { template: '<div />' },
            ElDialog: { template: '<div />' },
            ElDrawer: { template: '<div />' },
            ElForm: { template: '<form />' },
            ElFormItem: { template: '<div />' },
            ElInputNumber: { template: '<input type="number" />' },
            ElDescriptions: { template: '<div />' },
            ElDescriptionsItem: { template: '<div />' },
          },
        },
      })
      await new Promise(r => setTimeout(r, 10))
      const { getSandboxListApi } = await import('@/api/sandbox')
      expect(getSandboxListApi).toHaveBeenCalled()
    })

    it('should populate tableData after load', async () => {
      const wrapper = mount(SandboxInstanceList, {
        global: {
          stubs: {
            ElTable: { template: '<div class="el-table"><slot /></div>' },
            ElTableColumn: StubTableColumn,
            ElInput: { template: '<input />' },
            ElSelect: { template: '<select />' },
            ElOption: { template: '<option />' },
            ElButton: { template: '<button><slot /></button>' },
            ElIcon: { template: '<span />' },
            ElTag: { template: '<span><slot /></span>' },
            ElPagination: { template: '<div />' },
            ElDialog: { template: '<div />' },
            ElDrawer: { template: '<div />' },
            ElForm: { template: '<form />' },
            ElFormItem: { template: '<div />' },
            ElInputNumber: { template: '<input type="number" />' },
            ElDescriptions: { template: '<div />' },
            ElDescriptionsItem: { template: '<div />' },
          },
        },
      })
      await new Promise(r => setTimeout(r, 50))
      const vm = wrapper.vm as any
      expect(vm.tableData).toHaveLength(1)
      expect(vm.totalCount).toBe(2)
    })
  })

  describe('create/edit form', () => {
    it('should open create dialog with correct state', async () => {
      const wrapper = mount(SandboxInstanceList, {
        global: {
          stubs: {
            ElTable: { template: '<div class="el-table"><slot /></div>' },
            ElTableColumn: StubTableColumn,
            ElInput: { template: '<input />' },
            ElSelect: { template: '<select />' },
            ElOption: { template: '<option />' },
            ElButton: { template: '<button><slot /></button>' },
            ElIcon: { template: '<span />' },
            ElTag: { template: '<span><slot /></span>' },
            ElPagination: { template: '<div />' },
            ElDialog: { template: '<div />' },
            ElDrawer: { template: '<div />' },
            ElForm: { template: '<form />' },
            ElFormItem: { template: '<div />' },
            ElInputNumber: { template: '<input type="number" />' },
            ElDescriptions: { template: '<div />' },
            ElDescriptionsItem: { template: '<div />' },
          },
        },
      })
      await (wrapper.vm as any).handleCreate()
      const vm = wrapper.vm as any
      expect(vm.formVisible).toBe(true)
      expect(vm.formTitle).toBe('创建实例')
      expect(vm.editingId).toBeNull()
    })

    it('should open edit dialog with instance data', async () => {
      const wrapper = mount(SandboxInstanceList, {
        global: {
          stubs: {
            ElTable: { template: '<div class="el-table"><slot /></div>' },
            ElTableColumn: StubTableColumn,
            ElInput: { template: '<input />' },
            ElSelect: { template: '<select />' },
            ElOption: { template: '<option />' },
            ElButton: { template: '<button><slot /></button>' },
            ElIcon: { template: '<span />' },
            ElTag: { template: '<span><slot /></span>' },
            ElPagination: { template: '<div />' },
            ElDialog: { template: '<div />' },
            ElDrawer: { template: '<div />' },
            ElForm: { template: '<form />' },
            ElFormItem: { template: '<div />' },
            ElInputNumber: { template: '<input type="number" />' },
            ElDescriptions: { template: '<div />' },
            ElDescriptionsItem: { template: '<div />' },
          },
        },
      })
      const instance = {
        id: '01',
        name: 'test-sandbox',
        type: 'localdocker' as const,
        type_display: '本地 Docker',
        root_path: '/workspace',
        status: 'active' as const,
        status_display: '活跃',
        metadata: { image: 'sandbox:latest' },
        created_at: '2026-04-19 10:00:00',
        updated_at: '2026-04-19 10:00:00',
      }
      await (wrapper.vm as any).handleEdit(instance)
      const vm = wrapper.vm as any
      expect(vm.formVisible).toBe(true)
      expect(vm.form.name).toBe('test-sandbox')
      expect(vm.form.type).toBe('localdocker')
      expect(vm.editingId).toBe('01')
    })

    it('should validate required fields before save', async () => {
      const { ElMessage } = await import('element-plus')
      const wrapper = mount(SandboxInstanceList, {
        global: {
          stubs: {
            ElTable: { template: '<div class="el-table"><slot /></div>' },
            ElTableColumn: StubTableColumn,
            ElInput: { template: '<input />' },
            ElSelect: { template: '<select />' },
            ElOption: { template: '<option />' },
            ElButton: { template: '<button><slot /></button>' },
            ElIcon: { template: '<span />' },
            ElTag: { template: '<span><slot /></span>' },
            ElPagination: { template: '<div />' },
            ElDialog: { template: '<div />' },
            ElDrawer: { template: '<div />' },
            ElForm: { template: '<form />' },
            ElFormItem: { template: '<div />' },
            ElInputNumber: { template: '<input type="number" />' },
            ElDescriptions: { template: '<div />' },
            ElDescriptionsItem: { template: '<div />' },
          },
        },
      })
      await (wrapper.vm as any).handleCreate()
      await (wrapper.vm as any).handleSave()
      expect(ElMessage.warning).toHaveBeenCalled()
    })

    it('should validate ssh_host for remote types', async () => {
      const { ElMessage } = await import('element-plus')
      const wrapper = mount(SandboxInstanceList, {
        global: {
          stubs: {
            ElTable: { template: '<div class="el-table"><slot /></div>' },
            ElTableColumn: StubTableColumn,
            ElInput: { template: '<input />' },
            ElSelect: { template: '<select />' },
            ElOption: { template: '<option />' },
            ElButton: { template: '<button><slot /></button>' },
            ElIcon: { template: '<span />' },
            ElTag: { template: '<span><slot /></span>' },
            ElPagination: { template: '<div />' },
            ElDialog: { template: '<div />' },
            ElDrawer: { template: '<div />' },
            ElForm: { template: '<form />' },
            ElFormItem: { template: '<div />' },
            ElInputNumber: { template: '<input type="number" />' },
            ElDescriptions: { template: '<div />' },
            ElDescriptionsItem: { template: '<div />' },
          },
        },
      })
      await (wrapper.vm as any).handleCreate()
      const vm = wrapper.vm as any
      vm.form.name = 'remote-test'
      vm.form.type = 'remotesystem'
      vm.form.root_path = '/home/sandbox'
      vm.form.metadata = {}
      await vm.handleSave()
      expect(ElMessage.warning).toHaveBeenCalledWith('远程模式需要提供 SSH 主机')
    })

    it('should call create API for new instance', async () => {
      const wrapper = mount(SandboxInstanceList, {
        global: {
          stubs: {
            ElTable: { template: '<div class="el-table"><slot /></div>' },
            ElTableColumn: StubTableColumn,
            ElInput: { template: '<input />' },
            ElSelect: { template: '<select />' },
            ElOption: { template: '<option />' },
            ElButton: { template: '<button><slot /></button>' },
            ElIcon: { template: '<span />' },
            ElTag: { template: '<span><slot /></span>' },
            ElPagination: { template: '<div />' },
            ElDialog: { template: '<div />' },
            ElDrawer: { template: '<div />' },
            ElForm: { template: '<form />' },
            ElFormItem: { template: '<div />' },
            ElInputNumber: { template: '<input type="number" />' },
            ElDescriptions: { template: '<div />' },
            ElDescriptionsItem: { template: '<div />' },
          },
        },
      })
      await (wrapper.vm as any).handleCreate()
      const vm = wrapper.vm as any
      vm.form.name = 'new-sandbox'
      vm.form.type = 'localdocker'
      vm.form.root_path = '/workspace'
      vm.form.metadata = { image: 'sandbox:latest' }
      await vm.handleSave()
      const { createSandboxApi } = await import('@/api/sandbox')
      expect(createSandboxApi).toHaveBeenCalledWith({
        name: 'new-sandbox',
        type: 'localdocker',
        root_path: '/workspace',
        metadata: { image: 'sandbox:latest' },
      })
    })

    it('should call update API for existing instance', async () => {
      const wrapper = mount(SandboxInstanceList, {
        global: {
          stubs: {
            ElTable: { template: '<div class="el-table"><slot /></div>' },
            ElTableColumn: StubTableColumn,
            ElInput: { template: '<input />' },
            ElSelect: { template: '<select />' },
            ElOption: { template: '<option />' },
            ElButton: { template: '<button><slot /></button>' },
            ElIcon: { template: '<span />' },
            ElTag: { template: '<span><slot /></span>' },
            ElPagination: { template: '<div />' },
            ElDialog: { template: '<div />' },
            ElDrawer: { template: '<div />' },
            ElForm: { template: '<form />' },
            ElFormItem: { template: '<div />' },
            ElInputNumber: { template: '<input type="number" />' },
            ElDescriptions: { template: '<div />' },
            ElDescriptionsItem: { template: '<div />' },
          },
        },
      })
      const instance = {
        id: '01',
        name: 'old-name',
        type: 'localsystem' as const,
        type_display: '本地系统',
        root_path: '/tmp',
        status: 'active' as const,
        status_display: '活跃',
        metadata: {},
        created_at: '2026-04-19 10:00:00',
        updated_at: '2026-04-19 10:00:00',
      }
      await (wrapper.vm as any).handleEdit(instance)
      const vm = wrapper.vm as any
      vm.form.name = 'new-name'
      await vm.handleSave()
      const { updateSandboxApi } = await import('@/api/sandbox')
      expect(updateSandboxApi).toHaveBeenCalledWith('01', {
        name: 'new-name',
        type: 'localsystem',
        root_path: '/tmp',
        metadata: {},
      })
    })
  })

  describe('actions', () => {
    it('should load detail and open drawer', async () => {
      const wrapper = mount(SandboxInstanceList, {
        global: {
          stubs: {
            ElTable: { template: '<div class="el-table"><slot /></div>' },
            ElTableColumn: StubTableColumn,
            ElInput: { template: '<input />' },
            ElSelect: { template: '<select />' },
            ElOption: { template: '<option />' },
            ElButton: { template: '<button><slot /></button>' },
            ElIcon: { template: '<span />' },
            ElTag: { template: '<span><slot /></span>' },
            ElPagination: { template: '<div />' },
            ElDialog: { template: '<div />' },
            ElDrawer: { template: '<div />' },
            ElForm: { template: '<form />' },
            ElFormItem: { template: '<div />' },
            ElInputNumber: { template: '<input type="number" />' },
            ElDescriptions: { template: '<div />' },
            ElDescriptionsItem: { template: '<div />' },
          },
        },
      })
      const instance = {
        id: '01',
        name: 'detail-test',
        type: 'localdocker' as const,
        type_display: '本地 Docker',
        root_path: '/workspace',
        status: 'active' as const,
        status_display: '活跃',
        metadata: {},
        created_at: '2026-04-19 10:00:00',
        updated_at: '2026-04-19 10:00:00',
      }
      await (wrapper.vm as any).handleDetail(instance)
      expect((wrapper.vm as any).detailVisible).toBe(true)
      expect((wrapper.vm as any).selectedInstance).not.toBeNull()
    })

    it('should open execute dialog', async () => {
      const wrapper = mount(SandboxInstanceList, {
        global: {
          stubs: {
            ElTable: { template: '<div class="el-table"><slot /></div>' },
            ElTableColumn: StubTableColumn,
            ElInput: { template: '<input />' },
            ElSelect: { template: '<select />' },
            ElOption: { template: '<option />' },
            ElButton: { template: '<button><slot /></button>' },
            ElIcon: { template: '<span />' },
            ElTag: { template: '<span><slot /></span>' },
            ElPagination: { template: '<div />' },
            ElDialog: { template: '<div />' },
            ElDrawer: { template: '<div />' },
            ElForm: { template: '<form />' },
            ElFormItem: { template: '<div />' },
            ElInputNumber: { template: '<input type="number" />' },
            ElDescriptions: { template: '<div />' },
            ElDescriptionsItem: { template: '<div />' },
          },
        },
      })
      const instance = {
        id: '01',
        name: 'exec-test',
        type: 'localsystem' as const,
        type_display: '本地系统',
        root_path: '/tmp',
        status: 'active' as const,
        status_display: '活跃',
        metadata: {},
        created_at: '2026-04-19 10:00:00',
        updated_at: '2026-04-19 10:00:00',
      }
      await (wrapper.vm as any).handleExecute(instance)
      const vm = wrapper.vm as any
      expect(vm.executeVisible).toBe(true)
      expect(vm.executeTarget).toEqual(instance)
    })

    it('should warn when command is empty', async () => {
      const { ElMessage } = await import('element-plus')
      const wrapper = mount(SandboxInstanceList, {
        global: {
          stubs: {
            ElTable: { template: '<div class="el-table"><slot /></div>' },
            ElTableColumn: StubTableColumn,
            ElInput: { template: '<input />' },
            ElSelect: { template: '<select />' },
            ElOption: { template: '<option />' },
            ElButton: { template: '<button><slot /></button>' },
            ElIcon: { template: '<span />' },
            ElTag: { template: '<span><slot /></span>' },
            ElPagination: { template: '<div />' },
            ElDialog: { template: '<div />' },
            ElDrawer: { template: '<div />' },
            ElForm: { template: '<form />' },
            ElFormItem: { template: '<div />' },
            ElInputNumber: { template: '<input type="number" />' },
            ElDescriptions: { template: '<div />' },
            ElDescriptionsItem: { template: '<div />' },
          },
        },
      })
      await (wrapper.vm as any).handleRunCommand()
      expect(ElMessage.warning).toHaveBeenCalled()
    })

    it('should call execute API with command', async () => {
      const wrapper = mount(SandboxInstanceList, {
        global: {
          stubs: {
            ElTable: { template: '<div class="el-table"><slot /></div>' },
            ElTableColumn: StubTableColumn,
            ElInput: { template: '<input />' },
            ElSelect: { template: '<select />' },
            ElOption: { template: '<option />' },
            ElButton: { template: '<button><slot /></button>' },
            ElIcon: { template: '<span />' },
            ElTag: { template: '<span><slot /></span>' },
            ElPagination: { template: '<div />' },
            ElDialog: { template: '<div />' },
            ElDrawer: { template: '<div />' },
            ElForm: { template: '<form />' },
            ElFormItem: { template: '<div />' },
            ElInputNumber: { template: '<input type="number" />' },
            ElDescriptions: { template: '<div />' },
            ElDescriptionsItem: { template: '<div />' },
          },
        },
      })
      ;(wrapper.vm as any).executeTarget = { id: '01' }
      ;(wrapper.vm as any).executeCommand = 'echo hello'
      await (wrapper.vm as any).handleRunCommand()
      const { executeCommandApi } = await import('@/api/sandbox')
      expect(executeCommandApi).toHaveBeenCalledWith('01', { command: 'echo hello' })
    })

    it('should set output after successful execution', async () => {
      const wrapper = mount(SandboxInstanceList, {
        global: {
          stubs: {
            ElTable: { template: '<div class="el-table"><slot /></div>' },
            ElTableColumn: StubTableColumn,
            ElInput: { template: '<input />' },
            ElSelect: { template: '<select />' },
            ElOption: { template: '<option />' },
            ElButton: { template: '<button><slot /></button>' },
            ElIcon: { template: '<span />' },
            ElTag: { template: '<span><slot /></span>' },
            ElPagination: { template: '<div />' },
            ElDialog: { template: '<div />' },
            ElDrawer: { template: '<div />' },
            ElForm: { template: '<form />' },
            ElFormItem: { template: '<div />' },
            ElInputNumber: { template: '<input type="number" />' },
            ElDescriptions: { template: '<div />' },
            ElDescriptionsItem: { template: '<div />' },
          },
        },
      })
      ;(wrapper.vm as any).executeTarget = { id: '01' }
      ;(wrapper.vm as any).executeCommand = 'echo hello'
      await (wrapper.vm as any).handleRunCommand()
      const vm = wrapper.vm as any
      expect(vm.executeOutput).toBe('hello\n')
      expect(vm.executeResult).toEqual({
        output: 'hello\n',
        exit_code: 0,
        truncated: false,
      })
    })
  })

  describe('filter and pagination', () => {
    it('should reset page to 1 on filter change', async () => {
      const wrapper = mount(SandboxInstanceList, {
        global: {
          stubs: {
            ElTable: { template: '<div class="el-table"><slot /></div>' },
            ElTableColumn: StubTableColumn,
            ElInput: { template: '<input />' },
            ElSelect: { template: '<select />' },
            ElOption: { template: '<option />' },
            ElButton: { template: '<button><slot /></button>' },
            ElIcon: { template: '<span />' },
            ElTag: { template: '<span><slot /></span>' },
            ElPagination: { template: '<div />' },
            ElDialog: { template: '<div />' },
            ElDrawer: { template: '<div />' },
            ElForm: { template: '<form />' },
            ElFormItem: { template: '<div />' },
            ElInputNumber: { template: '<input type="number" />' },
            ElDescriptions: { template: '<div />' },
            ElDescriptionsItem: { template: '<div />' },
          },
        },
      })
      const vm = wrapper.vm as any
      vm.currentPage = 5
      await vm.onFilterChange()
      expect(vm.currentPage).toBe(1)
    })

    it('should reset page to 1 on page size change', async () => {
      const wrapper = mount(SandboxInstanceList, {
        global: {
          stubs: {
            ElTable: { template: '<div class="el-table"><slot /></div>' },
            ElTableColumn: StubTableColumn,
            ElInput: { template: '<input />' },
            ElSelect: { template: '<select />' },
            ElOption: { template: '<option />' },
            ElButton: { template: '<button><slot /></button>' },
            ElIcon: { template: '<span />' },
            ElTag: { template: '<span><slot /></span>' },
            ElPagination: { template: '<div />' },
            ElDialog: { template: '<div />' },
            ElDrawer: { template: '<div />' },
            ElForm: { template: '<form />' },
            ElFormItem: { template: '<div />' },
            ElInputNumber: { template: '<input type="number" />' },
            ElDescriptions: { template: '<div />' },
            ElDescriptionsItem: { template: '<div />' },
          },
        },
      })
      const vm = wrapper.vm as any
      vm.currentPage = 3
      await vm.onPageSizeChange()
      expect(vm.currentPage).toBe(1)
    })

    it('should refresh all data', async () => {
      const { getSandboxListApi } = await import('@/api/sandbox')
      const wrapper = mount(SandboxInstanceList, {
        global: {
          stubs: {
            ElTable: { template: '<div class="el-table"><slot /></div>' },
            ElTableColumn: StubTableColumn,
            ElInput: { template: '<input />' },
            ElSelect: { template: '<select />' },
            ElOption: { template: '<option />' },
            ElButton: { template: '<button><slot /></button>' },
            ElIcon: { template: '<span />' },
            ElTag: { template: '<span><slot /></span>' },
            ElPagination: { template: '<div />' },
            ElDialog: { template: '<div />' },
            ElDrawer: { template: '<div />' },
            ElForm: { template: '<form />' },
            ElFormItem: { template: '<div />' },
            ElInputNumber: { template: '<input type="number" />' },
            ElDescriptions: { template: '<div />' },
            ElDescriptionsItem: { template: '<div />' },
          },
        },
      })
      vi.clearAllMocks()
      ;(wrapper.vm as any).refreshAll()
      await new Promise(r => setTimeout(r, 10))
      expect(getSandboxListApi).toHaveBeenCalled()
    })
  })
})
