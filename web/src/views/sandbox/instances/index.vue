<template>
  <div class="sandbox-instance-management">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="page-header-left">
        <h1>沙箱实例管理</h1>
        <p>管理和配置沙箱实例</p>
      </div>
      <div class="header-actions">
        <el-button class="btn-refresh" @click="refreshAll">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
        <el-button type="primary" class="btn-create" @click="handleCreate">
          <el-icon><Plus /></el-icon>
          创建实例
        </el-button>
      </div>
    </div>

    <!-- 筛选栏 -->
    <div class="filter-bar">
      <div class="search-input">
        <el-icon><Search /></el-icon>
        <el-input v-model="searchName" placeholder="搜索名称..." clearable @clear="loadData" @keyup.enter="loadData" />
      </div>
      <el-select v-model="filterType" placeholder="全部类型" clearable class="filter-select" @change="onFilterChange">
        <el-option v-for="(schema, key) in sandboxTypes" :key="key" :label="schema.label" :value="key" />
      </el-select>
      <el-select v-model="filterStatus" placeholder="全部状态" clearable class="filter-select" @change="onFilterChange">
        <el-option label="活跃" value="active" />
        <el-option label="未激活" value="inactive" />
        <el-option label="错误" value="error" />
      </el-select>
    </div>

    <!-- 表格 -->
    <div class="table-container">
      <el-table :data="tableData" v-loading="loading" :show-header="true">
        <el-table-column prop="name" label="名称" min-width="150" show-overflow-tooltip />
        <el-table-column label="类型" width="120">
          <template #default="{ row }">
            <span class="type-badge">
              <el-icon><Monitor /></el-icon>
              {{ row.type_display }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <span class="status-badge" :class="getStatusClass(row.status)">
              <span class="dot"></span>
              {{ row.status_display }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <div class="action-group">
              <button class="action-btn view" title="详情" @click="handleDetail(row)">
                <el-icon><View /></el-icon>
              </button>
              <button class="action-btn edit" title="编辑" @click="handleEdit(row)">
                <el-icon><Edit /></el-icon>
              </button>
              <button class="action-btn start" title="启动" @click="handleStart(row)">
                <el-icon><CaretRight /></el-icon>
              </button>
              <button class="action-btn stop" title="停止" @click="handleStop(row)">
                <el-icon><VideoPause /></el-icon>
              </button>
              <button class="action-btn reset" title="重置" @click="handleReset(row)">
                <el-icon><RefreshLeft /></el-icon>
              </button>
              <button class="action-btn execute" title="执行" @click="handleExecute(row)">
                <el-icon><Promotion /></el-icon>
              </button>
              <button class="action-btn delete" title="删除" @click="handleDelete(row)">
                <el-icon><Delete /></el-icon>
              </button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-bar">
        <span class="pagination-info">共 {{ totalCount }} 条记录，第 {{ currentPage }} / {{ Math.ceil(totalCount / pageSize) }} 页</span>
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="totalCount"
          :page-sizes="[10, 20, 50]"
          layout="prev, pager, next"
          size="small"
          @current-change="loadData"
          @size-change="onPageSizeChange"
        />
      </div>
    </div>

    <!-- 创建/编辑对话框 -->
    <el-dialog v-model="formVisible" :title="formTitle" width="500px" class="modern-dialog" @closed="resetForm">
      <el-form :model="form" label-width="100px">
        <el-form-item label="名称" required>
          <el-input v-model="form.name" placeholder="沙箱名称" />
        </el-form-item>
        <el-form-item label="类型" required>
          <el-select v-model="form.type" style="width: 100%" @change="onTypeChange">
            <el-option v-for="(schema, key) in sandboxTypes" :key="key" :label="schema.label" :value="key" />
          </el-select>
        </el-form-item>

        <!-- 动态元信息字段 -->
        <el-form-item
          v-for="(fieldMeta, fieldName) in currentFields"
          :key="fieldName"
          :label="fieldMeta.label"
          :required="fieldMeta.required"
        >
          <el-input
            v-if="fieldMeta.type === 'string'"
            v-model="form.metadata[fieldName]"
            :placeholder="fieldMeta.hint || ''"
          />
          <el-input-number
            v-else-if="fieldMeta.type === 'number'"
            v-model="form.metadata[fieldName]"
            :min="1"
            :max="65535"
          />
          <el-switch
            v-else-if="fieldMeta.type === 'boolean'"
            v-model="form.metadata[fieldName]"
          />
          <div v-if="fieldMeta.hint" class="field-hint">
            {{ fieldMeta.hint }}
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="formVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>

    <!-- 详情抽屉 -->
    <el-drawer v-model="detailVisible" title="沙箱实例详情" size="450px" class="modern-drawer">
      <div v-if="selectedInstance" class="drawer-content">
        <div class="detail-header">
          <h2>{{ selectedInstance.name }}</h2>
          <span class="status-badge" :class="getStatusClass(selectedInstance.status)">
            <span class="dot"></span>
            {{ selectedInstance.status_display }}
          </span>
        </div>

        <div class="detail-grid">
          <div class="detail-item">
            <span class="detail-label">ID</span>
            <span class="detail-value mono">{{ selectedInstance.id }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">类型</span>
            <span class="detail-value">{{ selectedInstance.type_display }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">创建时间</span>
            <span class="detail-value">{{ selectedInstance.created_at }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">更新时间</span>
            <span class="detail-value">{{ selectedInstance.updated_at }}</span>
          </div>
          <div class="detail-item full-width">
            <span class="detail-label">元信息</span>
            <pre class="metadata-json">{{ JSON.stringify(selectedInstance.metadata, null, 2) }}</pre>
          </div>
        </div>
      </div>
    </el-drawer>

    <!-- 执行命令对话框 -->
    <el-dialog v-model="executeVisible" :title="`执行命令 — ${executeTarget?.name || ''}`" width="600px" class="modern-dialog">
      <div class="execute-panel">
        <div class="execute-input-row">
          <el-input
            v-model="executeCommand"
            placeholder="输入命令，例如: echo hello"
            @keyup.enter="handleRunCommand"
            class="execute-input"
          />
          <el-button type="primary" @click="handleRunCommand" :loading="executeLoading">
            执行
          </el-button>
        </div>
        <div class="execute-output">
          <pre>{{ executeOutput || '(无输出)' }}</pre>
        </div>
        <div class="execute-footer" v-if="executeResult">
          <span>退出码: <code>{{ executeResult.exit_code }}</code></span>
          <span>输出已截断: <code>{{ executeResult.truncated ? '是' : '否' }}</code></span>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Refresh, Plus, Search, View, Edit, CaretRight, VideoPause, RefreshLeft, Promotion, Delete, Monitor } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getSandboxListApi,
  deleteSandboxApi,
  startSandboxApi,
  stopSandboxApi,
  resetSandboxApi,
  getSandboxTypesApi,
} from '@/api/sandbox'
import type { SandboxInstance, SandboxType, SandboxStatus, SandboxTypeSchema } from '@/types/sandbox'
import { getTypeTagType, getStatusTagType } from '@/utils/sandbox'

// 状态
const loading = ref(false)
const tableData = ref<SandboxInstance[]>([])
const currentPage = ref(1)
const pageSize = ref(10)
const totalCount = ref(0)
const searchName = ref('')
const filterType = ref<SandboxType | ''>('')
const filterStatus = ref<SandboxStatus | ''>('')

// 沙箱类型 schema
const sandboxTypes = ref<Record<string, SandboxTypeSchema>>({})

// 创建/编辑表单
const formVisible = ref(false)
const editingId = ref<string | null>(null)
const formTitle = ref('创建实例')
const form = ref({
  name: '',
  type: '' as SandboxType | '',
  metadata: {} as Record<string, unknown>,
})

// 当前类型对应的表单字段
const currentFields = computed(() => {
  if (!form.value.type || !sandboxTypes.value[form.value.type]) return {}
  return sandboxTypes.value[form.value.type].fields
})

// 详情抽屉
const detailVisible = ref(false)
const selectedInstance = ref<SandboxInstance | null>(null)

// 执行命令
const executeVisible = ref(false)
const executeTarget = ref<SandboxInstance | null>(null)
const executeCommand = ref('')
const executeOutput = ref('')
const executeLoading = ref(false)
const executeResult = ref<{ exit_code: number; truncated: boolean } | null>(null)

// 加载沙箱类型
async function loadSandboxTypes() {
  try {
    const resp = await getSandboxTypesApi()
    sandboxTypes.value = resp.data.content?.types || {}
  } catch {
    // 静默失败，使用空对象
  }
}

// 加载数据
async function loadData() {
  loading.value = true
  try {
    const params: Record<string, any> = {
      page: currentPage.value,
      page_size: pageSize.value,
    }
    if (searchName.value) params.name = searchName.value
    if (filterType.value) params.type = filterType.value
    if (filterStatus.value) params.status = filterStatus.value

    const resp = await getSandboxListApi(params)
    tableData.value = resp.data.content?.results || []
    totalCount.value = resp.data.content?.count || 0
  } catch {
    ElMessage.error('加载沙箱实例失败')
  } finally {
    loading.value = false
  }
}

function refreshAll() {
  loadData()
}

function onFilterChange() {
  currentPage.value = 1
  loadData()
}

function onPageSizeChange() {
  currentPage.value = 1
  loadData()
}

// 类型切换时重置 metadata 默认值
function onTypeChange() {
  const schema = sandboxTypes.value[form.value.type as SandboxType]
  if (!schema) return

  const newMetadata: Record<string, unknown> = {}
  for (const [key, field] of Object.entries(schema.fields)) {
    newMetadata[key] = field.default ?? ''
  }
  form.value.metadata = newMetadata
}

// 创建
function handleCreate() {
  editingId.value = null
  formTitle.value = '创建实例'
  form.value = { name: '', type: '', metadata: {} }
  formVisible.value = true
}

// 编辑
function handleEdit(row: SandboxInstance) {
  editingId.value = row.id
  formTitle.value = '编辑实例'
  form.value = { name: row.name, type: row.type, metadata: { ...row.metadata } }
  formVisible.value = true
}

// 保存
async function handleSave() {
  if (!form.value.name || !form.value.type) {
    ElMessage.warning('请填写必填字段')
    return
  }

  // 校验 schema 必填字段
  const schema = sandboxTypes.value[form.value.type]
  if (schema) {
    for (const [key, field] of Object.entries(schema.fields)) {
      if (field.required && (form.value.metadata[key] === undefined || form.value.metadata[key] === '')) {
        ElMessage.warning(`请填写必填字段: ${field.label}`)
        return
      }
    }
  }

  const { createSandboxApi, updateSandboxApi } = await import('@/api/sandbox')

  try {
    const payload = {
      name: form.value.name,
      type: form.value.type,
      metadata: form.value.metadata,
    }
    if (editingId.value) {
      await updateSandboxApi(editingId.value, payload)
      ElMessage.success('更新成功')
    } else {
      await createSandboxApi(payload)
      ElMessage.success('创建成功')
    }
    formVisible.value = false
    loadData()
  } catch {
    ElMessage.error('保存失败')
  }
}

function resetForm() {
  form.value = { name: '', type: '', metadata: {} }
  editingId.value = null
}

// 详情
async function handleDetail(row: SandboxInstance) {
  const { getSandboxDetailApi } = await import('@/api/sandbox')
  try {
    const resp = await getSandboxDetailApi(row.id)
    selectedInstance.value = resp.data.content
    detailVisible.value = true
  } catch {
    ElMessage.error('获取详情失败')
  }
}

// 执行命令
function handleExecute(row: SandboxInstance) {
  executeTarget.value = row
  executeCommand.value = ''
  executeOutput.value = ''
  executeResult.value = null
  executeVisible.value = true
}

async function handleRunCommand() {
  if (!executeCommand.value.trim()) {
    ElMessage.warning('请输入命令')
    return
  }
  if (!executeTarget.value) return

  executeLoading.value = true
  try {
    const { executeCommandApi } = await import('@/api/sandbox')
    const resp = await executeCommandApi(executeTarget.value.id, {
      command: executeCommand.value,
    })
    executeResult.value = resp.data.content
    executeOutput.value = resp.data.content?.output || '(无输出)'
  } catch {
    ElMessage.error('执行命令失败')
  } finally {
    executeLoading.value = false
  }
}

// 启动
async function handleStart(row: SandboxInstance) {
  try {
    await ElMessageBox.confirm(`确定要启动沙箱 "${row.name}" 吗？`, '确认启动')
    await startSandboxApi(row.id)
    ElMessage.success('启动成功')
    loadData()
  } catch {
    // 用户取消
  }
}

// 停止
async function handleStop(row: SandboxInstance) {
  try {
    await ElMessageBox.confirm(`确定要停止沙箱 "${row.name}" 吗？`, '确认停止')
    await stopSandboxApi(row.id)
    ElMessage.success('停止成功')
    loadData()
  } catch {
    // 用户取消
  }
}

// 重置
async function handleReset(row: SandboxInstance) {
  try {
    await ElMessageBox.confirm(`确定要重置沙箱 "${row.name}" 吗？`, '确认重置')
    await resetSandboxApi(row.id)
    ElMessage.success('重置成功')
    loadData()
  } catch {
    // 用户取消
  }
}

// 删除
async function handleDelete(row: SandboxInstance) {
  try {
    await ElMessageBox.confirm(`确定要删除沙箱 "${row.name}" 吗？此操作不可撤销。`, '确认删除')
    await deleteSandboxApi(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch {
    // 用户取消
  }
}

function getStatusClass(status: string): string {
  const map: Record<string, string> = { active: 'status-active', inactive: 'status-inactive', error: 'status-error' }
  return map[status] || 'status-inactive'
}

onMounted(() => {
  loadSandboxTypes()
  loadData()
})
</script>

<style scoped lang="scss">
.sandbox-instance-management {
  max-width: 1400px;
  position: relative;
  z-index: 1;
}

/* 页面头部 */
.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 24px;
  animation: fadeUp 0.5s cubic-bezier(0.16, 1, 0.3, 1) both;
}

.page-header-left h1 {
  font-size: 24px;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--text-primary);
}

.page-header-left p {
  color: var(--text-secondary);
  font-size: 14px;
  margin-top: 4px;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.btn-refresh {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: var(--surface-glass);
  border: 1px solid var(--border-light);
  padding: 10px 16px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  cursor: pointer;
  transition: all 220ms cubic-bezier(0.4, 0, 0.2, 1);

  &:hover {
    background: white;
    border-color: var(--primary);
    color: var(--primary);
  }
}

.btn-create {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: var(--primary);
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  color: white;
  cursor: pointer;
  transition: all 220ms cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 1px 2px var(--primary-glow);

  &:hover {
    background: var(--primary-hover);
    box-shadow: 0 4px 12px var(--primary-glow);
    transform: translateY(-1px);
  }
}

/* 筛选栏 */
.filter-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  animation: fadeUp 0.5s cubic-bezier(0.16, 1, 0.3, 1) 0.05s both;
}

.search-input {
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--surface-glass);
  backdrop-filter: blur(16px);
  border: 1px solid var(--border-light);
  border-radius: 8px;
  padding: 8px 14px;
  width: 240px;
  transition: all 220ms cubic-bezier(0.4, 0, 0.2, 1);

  &:focus-within {
    border-color: var(--primary);
    box-shadow: 0 0 0 3px var(--primary-light);
  }

  :deep(.el-input__wrapper) {
    box-shadow: none !important;
    padding: 0 !important;
    background: transparent !important;
  }
}

.filter-select {
  width: 140px;
}

/* 表格容器 */
.table-container {
  background: var(--surface-glass);
  backdrop-filter: blur(16px);
  border: 1px solid var(--border-light);
  border-radius: 12px;
  overflow: hidden;
  animation: fadeUp 0.5s cubic-bezier(0.16, 1, 0.3, 1) 0.1s both;
}

:deep(.el-table) {
  background: transparent;

  th.el-table__cell {
    background: rgba(248, 250, 252, 0.8);
    color: var(--text-tertiary);
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    border-bottom: 1px solid var(--border-light) !important;
  }

  td.el-table__cell {
    border-bottom: 1px solid var(--border-light) !important;
    padding: 16px;
  }

  .el-table__row {
    transition: background 220ms ease;
    &:hover { background: rgba(248, 250, 252, 0.6); }
  }
}

/* 类型标签 */
.type-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: #f5f3ff;
  color: #8b5cf6;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
}

/* 状态标签 */
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;

  .dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
  }
}

.status-active {
  background: #ecfdf5;
  color: #059669;
  .dot { background: #10b981; }
}

.status-inactive {
  background: #f1f5f9;
  color: #94a3b8;
  .dot { background: #94a3b8; }
}

.status-error {
  background: #fef2f2;
  color: #ef4444;
  .dot { background: #ef4444; }
}

/* 操作按钮 */
.action-group {
  display: flex;
  align-items: center;
  gap: 2px;
}

.action-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  border-radius: 6px;
  cursor: pointer;
  transition: all 220ms ease;
  color: var(--text-tertiary);

  &.view:hover { color: #3b82f6; background: #eff6ff; }
  &.edit:hover { color: #f59e0b; background: #fffbeb; }
  &.start:hover { color: #10b981; background: #ecfdf5; }
  &.stop:hover { color: #f59e0b; background: #fffbeb; }
  &.reset:hover { color: #8b5cf6; background: #f5f3ff; }
  &.execute:hover { color: #ef4444; background: #fef2f2; }
  &.delete:hover { color: #ef4444; background: #fef2f2; }
}

/* 分页 */
.pagination-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-top: 1px solid var(--border-light);
}

.pagination-info {
  font-size: 13px;
  color: var(--text-tertiary);
}

/* 对话框 */
:deep(.modern-dialog) {
  .el-dialog__header {
    padding: 20px 24px;
    border-bottom: 1px solid var(--border-light);
  }
  .el-dialog__body { padding: 24px; }
  .el-dialog__footer {
    padding: 16px 24px;
    border-top: 1px solid var(--border-light);
    background: #f8fafc;
  }
}

/* 抽屉 */
:deep(.modern-drawer) {
  .el-drawer__header {
    margin-bottom: 0;
    padding: 20px 24px;
    border-bottom: 1px solid var(--border-light);
  }
  .el-drawer__body { padding: 0; }
}

.drawer-content {
  padding: 24px;
}

.detail-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;

  h2 {
    font-size: 18px;
    font-weight: 700;
    color: var(--text-primary);
  }
}

.detail-grid {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 4px;

  &.full-width {
    grid-column: 1 / -1;
  }
}

.detail-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.detail-value {
  font-size: 14px;
  color: var(--text-primary);
}

.mono {
  font-family: 'JetBrains Mono', monospace;
  font-size: 13px;
}

.metadata-json {
  background: #f8fafc;
  border: 1px solid var(--border-light);
  border-radius: 8px;
  padding: 12px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  color: var(--text-primary);
  line-height: 1.5;
  overflow-x: auto;
}

/* 字段提示 */
.field-hint {
  font-size: 12px;
  color: var(--text-tertiary);
  margin-top: 4px;
}

/* 执行面板 */
.execute-panel {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.execute-input-row {
  display: flex;
  gap: 8px;
}

.execute-input {
  flex: 1;
}

.execute-output {
  background: #0f172a;
  border-radius: 8px;
  padding: 16px;
  min-height: 200px;
  max-height: 400px;
  overflow-y: auto;

  pre {
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
    color: #e2e8f0;
    line-height: 1.5;
    white-space: pre-wrap;
    word-break: break-all;
    margin: 0;
  }
}

.execute-footer {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: var(--text-tertiary);

  code {
    font-family: 'JetBrains Mono', monospace;
    background: #f1f5f9;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 12px;
  }
}
</style>
