<template>
  <div class="llm-management">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="page-header-left">
        <h1>大模型配置</h1>
        <p>管理 LLM 供应商和模型配置</p>
      </div>
    </div>

    <!-- 选项卡 -->
    <div class="tab-container">
      <el-tabs v-model="activeTab" class="glass-tabs">
        <!-- 供应商管理 -->
        <el-tab-pane label="供应商管理" name="providers">
          <div class="tab-content">
            <div class="filter-bar">
              <div class="search-input">
                <el-icon><Search /></el-icon>
                <el-input v-model="providerSearch" placeholder="搜索名称或编码..." clearable @clear="loadProviders" @keyup.enter="loadProviders" />
              </div>
              <el-select v-model="providerFilterEnabled" placeholder="状态" clearable class="filter-select" @change="loadProviders">
                <el-option label="启用" :value="true" />
                <el-option label="停用" :value="false" />
              </el-select>
              <el-button type="primary" class="btn-action" @click="handleCreateProvider">
                <el-icon><Plus /></el-icon>
                添加供应商
              </el-button>
            </div>

            <div class="table-container">
              <el-table :data="providerTableData" v-loading="providerLoading" :show-header="true">
                <el-table-column prop="code" label="编码" width="140" />
                <el-table-column prop="name" label="名称" width="160" />
                <el-table-column prop="resolved_base_url" label="API 地址" min-width="250" show-overflow-tooltip />
                <el-table-column label="状态" width="100">
                  <template #default="{ row }">
                    <span class="status-badge" :class="row.enabled ? 'status-active' : 'status-inactive'">
                      <span class="dot"></span>
                      {{ row.enabled ? '启用' : '停用' }}
                    </span>
                  </template>
                </el-table-column>
                <el-table-column prop="description" label="描述" min-width="150" show-overflow-tooltip />
                <el-table-column label="操作" width="120" fixed="right">
                  <template #default="{ row }">
                    <div class="action-group">
                      <button class="action-btn edit" title="编辑" @click="handleEditProvider(row)">
                        <el-icon><Edit /></el-icon>
                      </button>
                      <button class="action-btn delete" title="删除" @click="handleDeleteProvider(row)">
                        <el-icon><Delete /></el-icon>
                      </button>
                    </div>
                  </template>
                </el-table-column>
              </el-table>

              <div class="pagination-bar">
                <span class="pagination-info">共 {{ providerTotal }} 条记录，第 {{ providerPage }} / {{ Math.ceil(providerTotal / providerPageSize) }} 页</span>
                <el-pagination
                  v-model:current-page="providerPage"
                  v-model:page-size="providerPageSize"
                  :total="providerTotal"
                  :page-sizes="[10, 20]"
                  layout="prev, pager, next"
                  size="small"
                  @current-change="loadProviders"
                  @size-change="loadProviders"
                />
              </div>
            </div>
          </div>
        </el-tab-pane>

        <!-- 模型管理 -->
        <el-tab-pane label="模型管理" name="models">
          <div class="tab-content">
            <div class="filter-bar">
              <div class="search-input">
                <el-icon><Search /></el-icon>
                <el-input v-model="modelSearch" placeholder="搜索模型名称或编码..." clearable @clear="loadModels" @keyup.enter="loadModels" />
              </div>
              <el-select v-model="modelFilterProvider" placeholder="供应商" clearable class="filter-select" @change="loadModels">
                <el-option v-for="p in providerOptions" :key="p.id" :label="p.name" :value="p.id" />
              </el-select>
              <el-button type="primary" class="btn-action" @click="handleCreateModel">
                <el-icon><Plus /></el-icon>
                添加模型
              </el-button>
            </div>

            <div class="table-container">
              <el-table :data="modelTableData" v-loading="modelLoading" :show-header="true">
                <el-table-column prop="provider_name" label="供应商" width="130" />
                <el-table-column prop="model_code" label="模型编码" width="180" />
                <el-table-column prop="display_name" label="显示名称" width="180" />
                <el-table-column prop="context_window" label="上下文窗口" width="130">
                  <template #default="{ row }">
                    <span class="mono-num">{{ row.context_window }}</span>
                  </template>
                </el-table-column>
                <el-table-column prop="max_output_tokens" label="最大输出" width="120">
                  <template #default="{ row }">
                    <span class="mono-num">{{ row.max_output_tokens }}</span>
                  </template>
                </el-table-column>
                <el-table-column label="状态" width="100">
                  <template #default="{ row }">
                    <span class="status-badge" :class="row.enabled ? 'status-active' : 'status-inactive'">
                      <span class="dot"></span>
                      {{ row.enabled ? '可用' : '停用' }}
                    </span>
                  </template>
                </el-table-column>
                <el-table-column prop="sort_order" label="排序" width="80">
                  <template #default="{ row }">
                    <span class="mono-num">{{ row.sort_order }}</span>
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="120" fixed="right">
                  <template #default="{ row }">
                    <div class="action-group">
                      <button class="action-btn edit" title="编辑" @click="handleEditModel(row)">
                        <el-icon><Edit /></el-icon>
                      </button>
                      <button class="action-btn delete" title="删除" @click="handleDeleteModel(row)">
                        <el-icon><Delete /></el-icon>
                      </button>
                    </div>
                  </template>
                </el-table-column>
              </el-table>

              <div class="pagination-bar">
                <span class="pagination-info">共 {{ modelTotal }} 条记录，第 {{ modelPage }} / {{ Math.ceil(modelTotal / modelPageSize) }} 页</span>
                <el-pagination
                  v-model:current-page="modelPage"
                  v-model:page-size="modelPageSize"
                  :total="modelTotal"
                  :page-sizes="[10, 20, 50]"
                  layout="prev, pager, next"
                  size="small"
                  @current-change="loadModels"
                  @size-change="loadModels"
                />
              </div>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>

    <!-- 供应商表单对话框 -->
    <el-dialog v-model="providerFormVisible" :title="providerFormTitle" width="500px" class="modern-dialog" @closed="resetProviderForm">
      <el-form :model="providerForm" label-width="100px">
        <el-form-item label="编码" required>
          <el-input v-model="providerForm.code" :disabled="!!editingProviderId" placeholder="如 openai, anthropic" />
        </el-form-item>
        <el-form-item label="名称" required>
          <el-input v-model="providerForm.name" placeholder="供应商显示名称" />
        </el-form-item>
        <el-form-item label="API 地址">
          <el-input v-model="providerForm.base_url" placeholder="预置供应商可留空" />
        </el-form-item>
        <el-form-item label="API 密钥">
          <el-input v-model="providerForm.api_key_encrypted" type="password" show-password placeholder="加密存储" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="providerForm.description" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="启用">
          <el-switch v-model="providerForm.enabled" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="providerFormVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveProvider">保存</el-button>
      </template>
    </el-dialog>

    <!-- 模型表单对话框 -->
    <el-dialog v-model="modelFormVisible" :title="modelFormTitle" width="500px" class="modern-dialog" @closed="resetModelForm">
      <el-form :model="modelForm" label-width="140px">
        <el-form-item label="供应商" required>
          <el-select v-model="modelForm.provider" style="width: 100%">
            <el-option v-for="p in providerOptions" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="模型编码" required>
          <el-input v-model="modelForm.model_code" placeholder="如 gpt-4o, claude-sonnet-4-6" />
        </el-form-item>
        <el-form-item label="显示名称">
          <el-input v-model="modelForm.display_name" placeholder="如 GPT-4o" />
        </el-form-item>
        <el-form-item label="上下文窗口">
          <el-input-number v-model="modelForm.context_window" :min="0" style="width: 100%" />
        </el-form-item>
        <el-form-item label="最大输出 Tokens">
          <el-input-number v-model="modelForm.max_output_tokens" :min="0" style="width: 100%" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="modelForm.sort_order" :min="0" style="width: 100%" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="modelForm.description" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="可用">
          <el-switch v-model="modelForm.enabled" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="modelFormVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveModel">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Edit, Delete } from '@element-plus/icons-vue'
import {
  getLLMProviderListApi,
  createLLMProviderApi,
  updateLLMProviderApi,
  deleteLLMProviderApi,
  getLLMModelListApi,
  createLLMModelApi,
  updateLLMModelApi,
  deleteLLMModelApi,
} from '@/api/llm'
import type { LLMProvider, LLMModel, CreateLLMProviderParams, CreateLLMModelParams } from '@/types/llm'

const activeTab = ref('providers')

// ===== 供应商 =====
const providerLoading = ref(false)
const providerTableData = ref<LLMProvider[]>([])
const providerPage = ref(1)
const providerPageSize = ref(10)
const providerTotal = ref(0)
const providerSearch = ref('')
const providerFilterEnabled = ref<boolean | undefined>(undefined)

async function loadProviders() {
  providerLoading.value = true
  try {
    const params: Record<string, unknown> = {
      page: providerPage.value,
      page_size: providerPageSize.value,
    }
    if (providerSearch.value) params.search = providerSearch.value
    if (providerFilterEnabled.value !== undefined) params.enabled = providerFilterEnabled.value

    const resp = await getLLMProviderListApi(params)
    providerTableData.value = resp.data.content?.results || []
    providerTotal.value = resp.data.content?.count || 0
  } catch {
    ElMessage.error('加载供应商列表失败')
  } finally {
    providerLoading.value = false
  }
}

// 供应商表单
const providerFormVisible = ref(false)
const providerFormTitle = ref('添加供应商')
const editingProviderId = ref<string | null>(null)
const providerForm = ref<CreateLLMProviderParams>({
  code: '',
  name: '',
  base_url: '',
  api_key_encrypted: '',
  enabled: true,
  description: '',
})

function handleCreateProvider() {
  editingProviderId.value = null
  providerFormTitle.value = '添加供应商'
  providerForm.value = { code: '', name: '', base_url: '', api_key_encrypted: '', enabled: true, description: '' }
  providerFormVisible.value = true
}

function handleEditProvider(row: LLMProvider) {
  editingProviderId.value = row.id
  providerFormTitle.value = '编辑供应商'
  providerForm.value = {
    code: row.code,
    name: row.name,
    base_url: row.base_url,
    api_key_encrypted: '',
    enabled: row.enabled,
    description: row.description,
  }
  providerFormVisible.value = true
}

async function handleSaveProvider() {
  if (!providerForm.value.code || !providerForm.value.name) {
    ElMessage.warning('编码和名称为必填')
    return
  }
  try {
    if (editingProviderId.value) {
      await updateLLMProviderApi(editingProviderId.value, providerForm.value)
      ElMessage.success('更新成功')
    } else {
      await createLLMProviderApi(providerForm.value)
      ElMessage.success('创建成功')
    }
    providerFormVisible.value = false
    loadProviders()
  } catch {
    ElMessage.error('保存失败')
  }
}

function resetProviderForm() {
  providerForm.value = { code: '', name: '', base_url: '', api_key_encrypted: '', enabled: true, description: '' }
  editingProviderId.value = null
}

async function handleDeleteProvider(row: LLMProvider) {
  try {
    await ElMessageBox.confirm(`确定要删除供应商「${row.name}」吗？此操作不可撤销。`, '确认删除')
    await deleteLLMProviderApi(row.id)
    ElMessage.success('删除成功')
    loadProviders()
  } catch {
    // 用户取消
  }
}

// ===== 模型 =====
const modelLoading = ref(false)
const modelTableData = ref<LLMModel[]>([])
const modelPage = ref(1)
const modelPageSize = ref(10)
const modelTotal = ref(0)
const modelSearch = ref('')
const modelFilterProvider = ref<string | undefined>(undefined)

// 供应商选项（用于模型表单的供应商下拉）
const providerOptions = ref<Array<{ id: string; name: string }>>([])

async function loadProviderOptions() {
  try {
    const resp = await getLLMProviderListApi({ page: 1, page_size: 50 })
    providerOptions.value = (resp.data.content?.results || []).map((p: LLMProvider) => ({
      id: p.id,
      name: p.name,
    }))
  } catch { /* 忽略 */ }
}

async function loadModels() {
  modelLoading.value = true
  try {
    const params: Record<string, unknown> = {
      page: modelPage.value,
      page_size: modelPageSize.value,
    }
    if (modelSearch.value) params.search = modelSearch.value
    if (modelFilterProvider.value) params.provider = modelFilterProvider.value

    const resp = await getLLMModelListApi(params)
    modelTableData.value = resp.data.content?.results || []
    modelTotal.value = resp.data.content?.count || 0
  } catch {
    ElMessage.error('加载模型列表失败')
  } finally {
    modelLoading.value = false
  }
}

// 模型表单
const modelFormVisible = ref(false)
const modelFormTitle = ref('添加模型')
const editingModelId = ref<string | null>(null)
const modelForm = ref<CreateLLMModelParams>({
  provider: '',
  model_code: '',
  display_name: '',
  context_window: 0,
  max_output_tokens: 0,
  enabled: true,
  sort_order: 0,
  description: '',
})

function handleCreateModel() {
  editingModelId.value = null
  modelFormTitle.value = '添加模型'
  modelForm.value = { provider: '', model_code: '', display_name: '', context_window: 0, max_output_tokens: 0, enabled: true, sort_order: 0, description: '' }
  modelFormVisible.value = true
}

function handleEditModel(row: LLMModel) {
  editingModelId.value = row.id
  modelFormTitle.value = '编辑模型'
  modelForm.value = {
    provider: row.provider,
    model_code: row.model_code,
    display_name: row.display_name,
    context_window: row.context_window,
    max_output_tokens: row.max_output_tokens,
    enabled: row.enabled,
    sort_order: row.sort_order,
    description: row.description,
  }
  modelFormVisible.value = true
}

async function handleSaveModel() {
  if (!modelForm.value.provider || !modelForm.value.model_code) {
    ElMessage.warning('供应商和模型编码为必填')
    return
  }
  try {
    if (editingModelId.value) {
      await updateLLMModelApi(editingModelId.value, modelForm.value)
      ElMessage.success('更新成功')
    } else {
      await createLLMModelApi(modelForm.value)
      ElMessage.success('创建成功')
    }
    modelFormVisible.value = false
    loadModels()
  } catch {
    ElMessage.error('保存失败')
  }
}

function resetModelForm() {
  modelForm.value = { provider: '', model_code: '', display_name: '', context_window: 0, max_output_tokens: 0, enabled: true, sort_order: 0, description: '' }
  editingModelId.value = null
}

async function handleDeleteModel(row: LLMModel) {
  try {
    await ElMessageBox.confirm(`确定要删除模型「${row.display_name}」吗？此操作不可撤销。`, '确认删除')
    await deleteLLMModelApi(row.id)
    ElMessage.success('删除成功')
    loadModels()
  } catch {
    // 用户取消
  }
}

onMounted(() => {
  loadProviders()
  loadModels()
  loadProviderOptions()
})
</script>

<style scoped lang="scss">
.llm-management {
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

/* 选项卡容器 */
.tab-container {
  background: var(--surface-glass);
  backdrop-filter: blur(16px);
  border: 1px solid var(--border-light);
  border-radius: 12px;
  overflow: hidden;
  animation: fadeUp 0.5s cubic-bezier(0.16, 1, 0.3, 1) 0.1s both;
}

:deep(.glass-tabs) {
  .el-tabs__header {
    margin: 0;
    padding: 0 24px;
    background: rgba(248, 250, 252, 0.6);
    border-bottom: 1px solid var(--border-light);
  }

  .el-tabs__nav-wrap::after {
    display: none;
  }

  .el-tabs__item {
    font-weight: 600;
    color: var(--text-secondary);
    transition: color 220ms ease;

    &.is-active {
      color: var(--primary);
    }

    &:hover {
      color: var(--primary);
    }
  }

  .el-tabs__active-bar {
    background: var(--primary);
    height: 2px;
  }

  .el-tabs__content {
    padding: 0;
  }
}

.tab-content {
  padding: 20px;
}

/* 筛选栏 */
.filter-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.search-input {
  display: flex;
  align-items: center;
  gap: 8px;
  background: white;
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

.btn-action {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin-left: auto;
}

/* 表格容器 */
.table-container {
  border: 1px solid var(--border-light);
  border-radius: 12px;
  overflow: hidden;
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

/* 数字 */
.mono-num {
  font-family: 'JetBrains Mono', monospace;
  font-size: 13px;
  color: var(--text-primary);
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
