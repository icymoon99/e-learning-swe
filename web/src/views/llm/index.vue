<template>
  <div class="llm-management p-4">
    <!-- 顶部操作栏 -->
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-xl font-semibold">大模型配置</h2>
    </div>

    <!-- 选项卡 -->
    <el-tabs v-model="activeTab">
      <!-- 供应商管理 -->
      <el-tab-pane label="供应商管理" name="providers">
        <div class="flex items-center justify-between mb-3">
          <div class="flex items-center gap-3">
            <el-input
              v-model="providerSearch"
              placeholder="搜索名称或编码"
              clearable
              style="width: 200px"
              @clear="loadProviders"
              @keyup.enter="loadProviders"
            />
            <el-select v-model="providerFilterEnabled" placeholder="状态" clearable style="width: 100px" @change="loadProviders">
              <el-option label="启用" :value="true" />
              <el-option label="停用" :value="false" />
            </el-select>
          </div>
          <el-button type="primary" @click="handleCreateProvider">添加供应商</el-button>
        </div>

        <el-table :data="providerTableData" v-loading="providerLoading" stripe border>
          <el-table-column prop="code" label="编码" width="140" />
          <el-table-column prop="name" label="名称" width="160" />
          <el-table-column prop="resolved_base_url" label="API 地址" min-width="250" show-overflow-tooltip />
          <el-table-column label="状态" width="80">
            <template #default="{ row }">
              <el-tag :type="row.enabled ? 'success' : 'info'" size="small">{{ row.enabled ? '启用' : '停用' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="description" label="描述" min-width="150" show-overflow-tooltip />
          <el-table-column label="操作" width="150" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" size="small" @click="handleEditProvider(row)">编辑</el-button>
              <el-button link type="danger" size="small" @click="handleDeleteProvider(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>

        <div class="flex justify-end mt-4">
          <el-pagination
            v-model:current-page="providerPage"
            v-model:page-size="providerPageSize"
            :total="providerTotal"
            :page-sizes="[10, 20]"
            layout="total, sizes, prev, pager, next"
            @current-change="loadProviders"
            @size-change="loadProviders"
          />
        </div>
      </el-tab-pane>

      <!-- 模型管理 -->
      <el-tab-pane label="模型管理" name="models">
        <div class="flex items-center justify-between mb-3">
          <div class="flex items-center gap-3">
            <el-input
              v-model="modelSearch"
              placeholder="搜索模型名称或编码"
              clearable
              style="width: 200px"
              @clear="loadModels"
              @keyup.enter="loadModels"
            />
            <el-select v-model="modelFilterProvider" placeholder="供应商" clearable style="width: 140px" @change="loadModels">
              <el-option v-for="p in providerOptions" :key="p.id" :label="p.name" :value="p.id" />
            </el-select>
          </div>
          <el-button type="primary" @click="handleCreateModel">添加模型</el-button>
        </div>

        <el-table :data="modelTableData" v-loading="modelLoading" stripe border>
          <el-table-column prop="provider_name" label="供应商" width="130" />
          <el-table-column prop="model_code" label="模型编码" width="180" />
          <el-table-column prop="display_name" label="显示名称" width="180" />
          <el-table-column prop="context_window" label="上下文窗口" width="130" />
          <el-table-column prop="max_output_tokens" label="最大输出" width="120" />
          <el-table-column label="状态" width="80">
            <template #default="{ row }">
              <el-tag :type="row.enabled ? 'success' : 'info'" size="small">{{ row.enabled ? '可用' : '停用' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="sort_order" label="排序" width="80" />
          <el-table-column label="操作" width="150" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" size="small" @click="handleEditModel(row)">编辑</el-button>
              <el-button link type="danger" size="small" @click="handleDeleteModel(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>

        <div class="flex justify-end mt-4">
          <el-pagination
            v-model:current-page="modelPage"
            v-model:page-size="modelPageSize"
            :total="modelTotal"
            :page-sizes="[10, 20, 50]"
            layout="total, sizes, prev, pager, next"
            @current-change="loadModels"
            @size-change="loadModels"
          />
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- 供应商表单对话框 -->
    <el-dialog v-model="providerFormVisible" :title="providerFormTitle" width="500px" @closed="resetProviderForm">
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
    <el-dialog v-model="modelFormVisible" :title="modelFormTitle" width="500px" @closed="resetModelForm">
      <el-form :model="modelForm" label-width="120px">
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
