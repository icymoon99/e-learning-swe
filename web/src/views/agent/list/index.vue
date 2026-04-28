<template>
  <div class="agent-management">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="page-header-left">
        <h1>Agent 管理</h1>
        <p>配置和管理所有 AI Agent</p>
      </div>
      <el-button type="primary" class="btn-create" @click="handleCreate">
        <el-icon><Plus /></el-icon>
        创建 Agent
      </el-button>
    </div>

    <!-- 筛选栏 -->
    <div class="filter-bar">
      <div class="search-input">
        <el-icon><Search /></el-icon>
        <el-input v-model="searchName" placeholder="搜索名称..." clearable @clear="loadData" @keyup.enter="loadData" />
      </div>
      <el-select v-model="filterStatus" placeholder="全部状态" clearable class="filter-select" @change="onFilterChange">
        <el-option label="启用" value="active" />
        <el-option label="停用" value="inactive" />
        <el-option label="已删除" value="deleted" />
      </el-select>
    </div>

    <!-- 表格 -->
    <div class="table-container">
      <el-table :data="tableData" v-loading="loading" :show-header="true" :header-cell-style="{ textAlign: 'center' }">
        <el-table-column prop="code" label="编码" width="150" header-align="center" />
        <el-table-column prop="name" label="名称" min-width="200" show-overflow-tooltip header-align="center" />
        <el-table-column prop="llm_model_display" label="LLM 模型" width="150" show-overflow-tooltip header-align="center" />
        <el-table-column prop="executor_display" label="执行器" width="150" show-overflow-tooltip header-align="center" />
        <el-table-column prop="sandbox_instance_name" label="绑定沙箱" width="180" show-overflow-tooltip header-align="center" />
        <el-table-column label="状态" width="150" align="center" header-align="center">
          <template #default="{ row }">
            <span class="status-badge" :class="getStatusClass(row.status)">
              <span class="dot"></span>
              {{ row.status_display }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip header-align="center" />
        <el-table-column prop="created_at" label="创建时间" width="250" align="center" header-align="center" />
        <el-table-column label="操作" width="120" fixed="right" align="center" header-align="center">
          <template #default="{ row }">
            <div class="action-group">
              <button class="action-btn edit" title="编辑" @click="handleEdit(row)">
                <el-icon><Edit /></el-icon>
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
        <span class="pagination-info">共 {{ totalCount }} 条记录，第 {{ currentPage }} / {{ totalPages }} 页</span>
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
    <el-dialog v-model="formVisible" :title="formTitle" width="600px" class="modern-dialog" @closed="resetForm">
      <el-form :model="form" label-width="120px">
        <el-form-item label="编码" required>
          <el-input v-model="form.code" placeholder="agent_code" :disabled="!!editingId" />
        </el-form-item>
        <el-form-item label="名称" required>
          <el-input v-model="form.name" placeholder="Agent 名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="2" placeholder="功能描述" />
        </el-form-item>
        <el-form-item label="系统提示词">
          <el-input v-model="form.system_prompt" type="textarea" :rows="4" placeholder="系统提示词" />
        </el-form-item>
        <el-form-item label="LLM 模型">
          <el-select v-model="form.llm_model" placeholder="选择 LLM 模型" clearable style="width: 100%" @focus="loadModelOptions">
            <el-option
              v-for="m in llmModelOptions"
              :key="m.id"
              :label="`${m.provider_name} · ${m.display_name}`"
              :value="m.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="执行器">
          <el-select v-model="form.executor" placeholder="选择执行器" clearable style="width: 100%" @focus="loadExecutors">
            <el-option
              v-for="e in executorOptions"
              :key="e.id"
              :label="e.name"
              :value="e.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="绑定沙箱" required>
          <el-select v-model="form.sandbox_instance" placeholder="选择沙箱实例" clearable style="width: 100%" @focus="loadSandboxes">
            <el-option
              v-for="s in sandboxOptions"
              :key="s.id"
              :label="`${s.name}（${s.type_display}）- ${s.status_display}`"
              :value="s.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status" style="width: 100%">
            <el-option label="启用" value="active" />
            <el-option label="停用" value="inactive" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="formVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Edit, Delete } from '@element-plus/icons-vue'
import {
  getAgentListApi,
  createAgentApi,
  updateAgentApi,
  deleteAgentApi,
  getExecutorListApi,
} from '@/api/agent'
import { getLLMModelDropdownApi } from '@/api/llm'
import { getSandboxListApi } from '@/api/sandbox'
import type { AgentInstance, AgentStatus, ExecutorOption, SandboxOption } from '@/types/agent'
import type { LLMModelDropdown } from '@/types/llm'

// 状态
const loading = ref(false)
const tableData = ref<AgentInstance[]>([])
const currentPage = ref(1)
const pageSize = ref(10)
const totalCount = ref(0)
const searchName = ref('')
const filterStatus = ref<AgentStatus | ''>('')

const totalPages = computed(() => Math.ceil(totalCount.value / pageSize.value))

// 创建/编辑表单
const formVisible = ref(false)
const editingId = ref<string | null>(null)
const formTitle = ref('创建 Agent')
const form = ref({
  code: '',
  name: '',
  description: '',
  system_prompt: '',
  llm_model: null as string | null,
  executor: null as string | null,
  sandbox_instance: '' as string,
  status: 'active' as AgentStatus,
  metadata: {} as Record<string, unknown>,
})

// LLM 模型下拉
const llmModelOptions = ref<LLMModelDropdown[]>([])
const llmDropdownLoaded = ref(false)

async function loadModelOptions() {
  if (llmDropdownLoaded.value) return
  try {
    const resp = await getLLMModelDropdownApi()
    llmModelOptions.value = resp.data.content || []
    llmDropdownLoaded.value = true
  } catch { /* 忽略 */ }
}

// 执行器下拉
const executorOptions = ref<ExecutorOption[]>([])
const executorLoaded = ref(false)

async function loadExecutors() {
  if (executorLoaded.value) return
  try {
    const resp = await getExecutorListApi()
    executorOptions.value = resp.data.content?.results?.map((e: { id: string; code: string; name: string }) => ({ id: e.id, code: e.code, name: e.name })) || []
    executorLoaded.value = true
  } catch { /* 忽略 */ }
}

// 沙箱实例下拉
const sandboxOptions = ref<SandboxOption[]>([])
const sandboxLoaded = ref(false)

async function loadSandboxes() {
  if (sandboxLoaded.value) return
  try {
    const resp = await getSandboxListApi({ page: 1, page_size: 50 })
    sandboxOptions.value = resp.data.content?.results?.map((s: { id: string; name: string; type: string; type_display: string; status: string; status_display: string }) => ({
      id: s.id,
      name: s.name,
      type: s.type,
      type_display: s.type_display,
      status: s.status,
      status_display: s.status_display,
    })) || []
    sandboxLoaded.value = true
  } catch { /* 忽略 */ }
}

// 加载数据
async function loadData() {
  loading.value = true
  try {
    const params: Record<string, unknown> = { page: currentPage.value, page_size: pageSize.value }
    if (searchName.value) params.search = searchName.value
    if (filterStatus.value) params.status = filterStatus.value

    const resp = await getAgentListApi(params)
    tableData.value = resp.data.content?.results || []
    totalCount.value = resp.data.content?.count || 0
  } catch {
    ElMessage.error('加载 Agent 列表失败')
  } finally {
    loading.value = false
  }
}

function onFilterChange() { currentPage.value = 1; loadData() }
function onPageSizeChange() { currentPage.value = 1; loadData() }

// 创建
function handleCreate() {
  editingId.value = null
  formTitle.value = '创建 Agent'
  form.value = { code: '', name: '', description: '', system_prompt: '', llm_model: null, executor: null, sandbox_instance: '', status: 'active', metadata: {} }
  formVisible.value = true
}

// 编辑
function handleEdit(row: AgentInstance) {
  editingId.value = row.id
  formTitle.value = '编辑 Agent'
  form.value = {
    code: row.code,
    name: row.name,
    description: row.description,
    system_prompt: row.system_prompt,
    llm_model: row.llm_model,
    executor: row.executor,
    sandbox_instance: row.sandbox_instance || '',
    status: row.status,
    metadata: { ...row.metadata },
  }
  formVisible.value = true
}

// 保存
async function handleSave() {
  if (!form.value.code) { ElMessage.warning('编码为必填字段'); return }
  if (!form.value.sandbox_instance) { ElMessage.warning('绑定沙箱为必填字段'); return }
  try {
    if (editingId.value) {
      await updateAgentApi(editingId.value, {
        name: form.value.name,
        description: form.value.description,
        system_prompt: form.value.system_prompt,
        llm_model: form.value.llm_model,
        executor: form.value.executor,
        sandbox_instance: form.value.sandbox_instance,
        status: form.value.status,
        metadata: form.value.metadata,
      })
      ElMessage.success('更新成功')
    } else {
      await createAgentApi({
        code: form.value.code,
        name: form.value.name,
        description: form.value.description,
        system_prompt: form.value.system_prompt,
        llm_model: form.value.llm_model,
        executor: form.value.executor,
        sandbox_instance: form.value.sandbox_instance,
        status: form.value.status,
        metadata: form.value.metadata,
      })
      ElMessage.success('创建成功')
    }
    formVisible.value = false
    loadData()
  } catch { ElMessage.error('保存失败') }
}

function resetForm() {
  form.value = { code: '', name: '', description: '', system_prompt: '', llm_model: null, executor: null, sandbox_instance: '', status: 'active', metadata: {} }
  editingId.value = null
}

// 删除
async function handleDelete(row: AgentInstance) {
  try {
    await ElMessageBox.confirm(`确定要删除 Agent "${row.name}" 吗？此操作不可撤销。`, '确认删除')
    await deleteAgentApi(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch { /* 用户取消 */ }
}

function getStatusClass(status: string): string {
  const map: Record<string, string> = { active: 'status-active', inactive: 'status-inactive', deleted: 'status-deleted' }
  return map[status] || 'status-inactive'
}

onMounted(() => loadData())
</script>

<style scoped lang="scss">
.agent-management {
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

.status-deleted {
  background: #fef2f2;
  color: #ef4444;
  .dot { background: #ef4444; }
}

/* 操作按钮 */
.action-group {
  display: flex;
  align-items: center;
  gap: 4px;
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

  &.edit:hover { color: #f59e0b; background: #fffbeb; }
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
</style>
