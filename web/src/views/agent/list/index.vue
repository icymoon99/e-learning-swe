<template>
  <div class="agent-management p-4">
    <!-- 顶部操作栏 -->
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-xl font-semibold">Agent 管理</h2>
      <el-button type="primary" @click="handleCreate">
        创建 Agent
      </el-button>
    </div>

    <!-- 过滤栏 -->
    <div class="flex items-center gap-3 mb-4">
      <el-input
        v-model="searchName"
        placeholder="搜索名称"
        clearable
        style="width: 200px"
        @clear="loadData"
        @keyup.enter="loadData"
      />
      <el-select v-model="filterStatus" placeholder="状态" clearable style="width: 120px" @change="onFilterChange">
        <el-option label="启用" value="active" />
        <el-option label="停用" value="inactive" />
        <el-option label="已删除" value="deleted" />
      </el-select>
    </div>

    <!-- Agent 列表表格 -->
    <el-table :data="tableData" v-loading="loading" stripe border>
      <el-table-column prop="code" label="编码" width="150" />
      <el-table-column prop="name" label="名称" min-width="150" show-overflow-tooltip />
      <el-table-column prop="model" label="模型" width="180" show-overflow-tooltip />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="getStatusTagType(row.status)" size="small">
            {{ row.status_display }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
      <el-table-column prop="created_at" label="创建时间" width="180" />
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" size="small" @click="handleEdit(row)">编辑</el-button>
          <el-button link type="danger" size="small" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="flex justify-end mt-4">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="totalCount"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        @current-change="loadData"
        @size-change="onPageSizeChange"
      />
    </div>

    <!-- 创建/编辑对话框 -->
    <el-dialog v-model="formVisible" :title="formTitle" width="600px" @closed="resetForm">
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
          <el-input v-model="form.model" placeholder="claude-sonnet-4-6" />
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
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getAgentListApi,
  createAgentApi,
  updateAgentApi,
  deleteAgentApi,
} from '@/api/agent'
import type { AgentInstance, AgentStatus } from '@/types/agent'

// 状态
const loading = ref(false)
const tableData = ref<AgentInstance[]>([])
const currentPage = ref(1)
const pageSize = ref(10)
const totalCount = ref(0)
const searchName = ref('')
const filterStatus = ref<AgentStatus | ''>('')

// 创建/编辑表单
const formVisible = ref(false)
const editingId = ref<string | null>(null)
const formTitle = ref('创建 Agent')
const form = ref({
  code: '',
  name: '',
  description: '',
  system_prompt: '',
  model: 'claude-sonnet-4-6',
  status: 'active' as AgentStatus,
  metadata: {} as Record<string, unknown>,
})

// 加载数据
async function loadData() {
  loading.value = true
  try {
    const params: Record<string, unknown> = {
      page: currentPage.value,
      page_size: pageSize.value,
    }
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

function onFilterChange() {
  currentPage.value = 1
  loadData()
}

function onPageSizeChange() {
  currentPage.value = 1
  loadData()
}

// 创建
function handleCreate() {
  editingId.value = null
  formTitle.value = '创建 Agent'
  form.value = {
    code: '',
    name: '',
    description: '',
    system_prompt: '',
    model: 'claude-sonnet-4-6',
    status: 'active',
    metadata: {},
  }
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
    model: row.model,
    status: row.status,
    metadata: { ...row.metadata },
  }
  formVisible.value = true
}

// 保存
async function handleSave() {
  if (!form.value.code) {
    ElMessage.warning('编码为必填字段')
    return
  }

  try {
    if (editingId.value) {
      await updateAgentApi(editingId.value, {
        name: form.value.name,
        description: form.value.description,
        system_prompt: form.value.system_prompt,
        model: form.value.model,
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
        model: form.value.model,
        status: form.value.status,
        metadata: form.value.metadata,
      })
      ElMessage.success('创建成功')
    }
    formVisible.value = false
    loadData()
  } catch {
    ElMessage.error('保存失败')
  }
}

function resetForm() {
  form.value = {
    code: '',
    name: '',
    description: '',
    system_prompt: '',
    model: 'claude-sonnet-4-6',
    status: 'active',
    metadata: {},
  }
  editingId.value = null
}

// 删除
async function handleDelete(row: AgentInstance) {
  try {
    await ElMessageBox.confirm(`确定要删除 Agent "${row.name}" 吗？此操作不可撤销。`, '确认删除')
    await deleteAgentApi(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch {
    // 用户取消
  }
}

// 状态标签颜色
function getStatusTagType(status: string): string {
  const map: Record<string, string> = { active: 'success', inactive: 'info', deleted: 'danger' }
  return map[status] || 'info'
}

onMounted(() => {
  loadData()
})
</script>
