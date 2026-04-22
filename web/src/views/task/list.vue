<template>
  <div class="task-management p-4">
    <!-- 顶部操作栏 -->
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-xl font-semibold">任务管理</h2>
      <el-button type="primary" @click="handleCreate">
        创建任务
      </el-button>
    </div>

    <!-- 过滤栏 -->
    <div class="flex items-center gap-3 mb-4">
      <el-input
        v-model="searchText"
        placeholder="搜索标题"
        clearable
        style="width: 200px"
        @clear="loadData"
        @keyup.enter="loadData"
      />
      <el-select v-model="filterStatus" placeholder="状态" clearable style="width: 120px" @change="onFilterChange">
        <el-option label="进行中" value="open" />
        <el-option label="已关闭" value="closed" />
      </el-select>
    </div>

    <!-- 任务列表表格 -->
    <el-table :data="tableData" v-loading="loading" stripe border>
      <el-table-column prop="title" label="标题" min-width="200" show-overflow-tooltip />
      <el-table-column prop="git_source_name" label="仓库源" width="150" show-overflow-tooltip />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status === 'open' ? 'success' : 'info'" size="small">
            {{ row.status_display }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="执行状态" width="120">
        <template #default="{ row }">
          <el-tag v-if="row.latest_execution_status" :type="getExecutionTagType(row.latest_execution_status)" size="small">
            {{ row.latest_execution_status }}
          </el-tag>
          <span v-else class="text-gray-400">-</span>
        </template>
      </el-table-column>
      <el-table-column prop="source_branch" label="源分支" width="120" />
      <el-table-column prop="updated_at" label="更新时间" width="180" />
      <el-table-column label="操作" width="240" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" size="small" @click="handleViewDetail(row)">详情</el-button>
          <el-button link type="primary" size="small" @click="handleEdit(row)">编辑</el-button>
          <el-button link type="warning" size="small" @click="handleClose(row)" v-if="row.status === 'open'">关闭</el-button>
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

    <!-- 创建对话框 -->
    <el-dialog v-model="createVisible" title="创建任务" width="600px">
      <el-form :model="createForm" label-width="100px">
        <el-form-item label="标题" required>
          <el-input v-model="createForm.title" placeholder="任务标题" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="createForm.description" type="textarea" :rows="3" placeholder="任务描述" />
        </el-form-item>
        <el-form-item label="仓库源">
          <el-select v-model="createForm.git_source_id" placeholder="选择仓库源" clearable style="width: 100%" @focus="loadDropdown">
            <el-option v-for="item in gitSourceOptions" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="源分支">
          <el-input v-model="createForm.source_branch" placeholder="main" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCreateSave">创建</el-button>
      </template>
    </el-dialog>

    <!-- 编辑对话框 -->
    <el-dialog v-model="editVisible" title="编辑任务" width="600px">
      <el-form :model="editForm" label-width="100px">
        <el-form-item label="标题" required>
          <el-input v-model="editForm.title" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="editForm.description" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="源分支">
          <el-input v-model="editForm.source_branch" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" @click="handleEditSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getTaskListApi,
  createTaskApi,
  updateTaskApi,
  deleteTaskApi,
  closeTaskApi,
} from '@/api/task'
import { getGitSourceDropdownApi } from '@/api/gitSource'
import type { TaskItem, TaskStatus } from '@/types/task'

const router = useRouter()

// 状态
const loading = ref(false)
const tableData = ref<TaskItem[]>([])
const currentPage = ref(1)
const pageSize = ref(10)
const totalCount = ref(0)
const searchText = ref('')
const filterStatus = ref<TaskStatus | ''>('')

// 创建表单
const createVisible = ref(false)
const createForm = ref({
  title: '',
  description: '',
  git_source_id: null as string | null,
  source_branch: 'main',
})

// 编辑表单
const editVisible = ref(false)
const editId = ref<string | null>(null)
const editForm = ref({
  title: '',
  description: '',
  source_branch: '',
})

// 仓库源下拉选项
const gitSourceOptions = ref<Array<{ id: string; name: string; platform: string }>>([])
const dropdownLoaded = ref(false)

async function loadDropdown() {
  if (dropdownLoaded.value) return
  try {
    const resp = await getGitSourceDropdownApi()
    gitSourceOptions.value = resp.data.content || []
    dropdownLoaded.value = true
  } catch {
    // 忽略
  }
}

// 加载数据
async function loadData() {
  loading.value = true
  try {
    const params: Record<string, unknown> = {
      page: currentPage.value,
      page_size: pageSize.value,
    }
    if (searchText.value) params.search = searchText.value
    if (filterStatus.value) params.status = filterStatus.value

    const resp = await getTaskListApi(params)
    tableData.value = resp.data.content?.results || []
    totalCount.value = resp.data.content?.count || 0
  } catch {
    ElMessage.error('加载任务列表失败')
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

function getExecutionTagType(status: string): string {
  const map: Record<string, string> = { completed: 'success', running: 'warning', failed: 'danger' }
  return map[status] || 'info'
}

// 查看详情
function handleViewDetail(row: TaskItem) {
  router.push({ name: 'TaskDetail', params: { id: row.id } })
}

// 创建
function handleCreate() {
  createForm.value = { title: '', description: '', git_source_id: null, source_branch: 'main' }
  createVisible.value = true
}

async function handleCreateSave() {
  if (!createForm.value.title) {
    ElMessage.warning('标题为必填')
    return
  }
  try {
    await createTaskApi(createForm.value)
    ElMessage.success('创建成功')
    createVisible.value = false
    loadData()
  } catch {
    ElMessage.error('创建失败')
  }
}

// 编辑
function handleEdit(row: TaskItem) {
  editId.value = row.id
  editForm.value = { title: row.title, description: '', source_branch: row.source_branch }
  editVisible.value = true
}

async function handleEditSave() {
  if (!editForm.value.title) {
    ElMessage.warning('标题为必填')
    return
  }
  try {
    await updateTaskApi(editId.value!, editForm.value)
    ElMessage.success('更新成功')
    editVisible.value = false
    loadData()
  } catch {
    ElMessage.error('更新失败')
  }
}

// 关闭任务
async function handleClose(row: TaskItem) {
  try {
    await ElMessageBox.confirm(`确定要关闭任务 "${row.title}" 吗？`, '确认关闭')
    await closeTaskApi(row.id)
    ElMessage.success('任务已关闭')
    loadData()
  } catch {
    // 用户取消
  }
}

// 删除
async function handleDelete(row: TaskItem) {
  try {
    await ElMessageBox.confirm(`确定要删除任务 "${row.title}" 吗？此操作不可撤销。`, '确认删除')
    await deleteTaskApi(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch {
    // 用户取消
  }
}

onMounted(() => {
  loadData()
})
</script>
