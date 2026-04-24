<template>
  <div class="sandbox-instance-management p-4">
    <!-- 顶部状态栏 -->
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-xl font-semibold">沙箱实例管理</h2>
      <div class="flex items-center gap-3">
        <el-button size="small" @click="refreshAll">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
        <el-button type="primary" size="small" @click="handleCreate">
          创建实例
        </el-button>
      </div>
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
      <el-select v-model="filterType" placeholder="类型" clearable style="width: 150px" @change="onFilterChange">
        <el-option v-for="(schema, key) in sandboxTypes" :key="key" :label="schema.label" :value="key" />
      </el-select>
      <el-select v-model="filterStatus" placeholder="状态" clearable style="width: 120px" @change="onFilterChange">
        <el-option label="活跃" value="active" />
        <el-option label="未激活" value="inactive" />
        <el-option label="错误" value="error" />
      </el-select>
    </div>

    <!-- 实例列表表格 -->
    <el-table :data="tableData" v-loading="loading" stripe border>
      <el-table-column prop="name" label="名称" min-width="150" show-overflow-tooltip />
      <el-table-column label="类型" width="120">
        <template #default="{ row }">
          <el-tag :type="getTypeTagType(row.type)" size="small">
            {{ row.type_display }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="getStatusTagType(row.status)" size="small">
            {{ row.status_display }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="180" />
      <el-table-column label="操作" width="300" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" size="small" @click="handleDetail(row)">详情</el-button>
          <el-button link type="primary" size="small" @click="handleEdit(row)">编辑</el-button>
          <el-button link type="success" size="small" @click="handleStart(row)">启动</el-button>
          <el-button link type="warning" size="small" @click="handleStop(row)">停止</el-button>
          <el-button link type="info" size="small" @click="handleReset(row)">重置</el-button>
          <el-button link type="danger" size="small" @click="handleExecute(row)">执行</el-button>
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
    <el-dialog v-model="formVisible" :title="formTitle" width="500px" @closed="resetForm">
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
          <div v-if="fieldMeta.hint" class="text-xs text-gray-400 mt-1">
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
    <el-drawer v-model="detailVisible" title="沙箱实例详情" size="450px">
      <el-descriptions :column="1" border v-if="selectedInstance">
        <el-descriptions-item label="ID">{{ selectedInstance.id }}</el-descriptions-item>
        <el-descriptions-item label="名称">{{ selectedInstance.name }}</el-descriptions-item>
        <el-descriptions-item label="类型">
          <el-tag :type="getTypeTagType(selectedInstance.type)" size="small">
            {{ selectedInstance.type_display }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusTagType(selectedInstance.status)" size="small">
            {{ selectedInstance.status_display }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="元信息">
          <pre class="text-xs bg-gray-50 p-2 rounded">{{ JSON.stringify(selectedInstance.metadata, null, 2) }}</pre>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ selectedInstance.created_at }}</el-descriptions-item>
        <el-descriptions-item label="更新时间">{{ selectedInstance.updated_at }}</el-descriptions-item>
      </el-descriptions>
    </el-drawer>

    <!-- 执行命令对话框 -->
    <el-dialog v-model="executeVisible" :title="`执行命令 — ${executeTarget?.name || ''}`" width="600px">
      <div class="flex gap-2 mb-3">
        <el-input
          v-model="executeCommand"
          placeholder="输入命令，例如: echo hello"
          @keyup.enter="handleRunCommand"
        />
        <el-button type="primary" @click="handleRunCommand" :loading="executeLoading">
          执行
        </el-button>
      </div>
      <el-input
        v-model="executeOutput"
        type="textarea"
        :rows="10"
        readonly
        placeholder="输出将显示在这里"
      />
      <div class="mt-2 text-sm text-gray-500" v-if="executeResult">
        <span>退出码: {{ executeResult.exit_code }}</span>
        <span class="ml-4">输出已截断: {{ executeResult.truncated ? '是' : '否' }}</span>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
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

onMounted(() => {
  loadSandboxTypes()
  loadData()
})
</script>
