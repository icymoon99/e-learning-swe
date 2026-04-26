<template>
  <div class="task-management">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="page-header-left">
        <h1>任务列表</h1>
        <p>管理和跟踪所有任务的执行状态</p>
      </div>
      <el-button type="primary" class="btn-create" @click="handleCreate">
        <el-icon><Plus /></el-icon>
        创建任务
      </el-button>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-row">
      <div class="stat-card">
        <div class="stat-label">全部任务</div>
        <div class="stat-value">{{ totalCount }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">进行中</div>
        <div class="stat-value">{{ tableData.filter(t => t.status === 'open').length }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">已完成</div>
        <div class="stat-value">{{ tableData.filter(t => t.latest_execution_status === 'completed').length }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">执行失败</div>
        <div class="stat-value">{{ tableData.filter(t => t.latest_execution_status === 'failed').length }}</div>
      </div>
    </div>

    <!-- 筛选栏 -->
    <div class="filter-bar">
      <div class="search-input">
        <el-icon><Search /></el-icon>
        <el-input v-model="searchText" placeholder="搜索标题..." clearable @clear="loadData" @keyup.enter="loadData" />
      </div>
      <el-select v-model="filterStatus" placeholder="全部状态" clearable class="filter-select" @change="onFilterChange">
        <el-option label="进行中" value="open" />
        <el-option label="已关闭" value="closed" />
      </el-select>
    </div>

    <!-- 表格 -->
    <div class="table-container">
      <el-table :data="tableData" v-loading="loading" :show-header="true" :header-cell-style="{ textAlign: 'center' }">
        <el-table-column label="任务" min-width="150" show-overflow-tooltip header-align="center">
          <template #default="{ row }">
            <div class="task-title">{{ row.title }}</div>
            <div class="task-desc">{{ row.description || '-' }}</div>
          </template>
        </el-table-column>
        <el-table-column label="仓库源" width="200" show-overflow-tooltip header-align="center">
          <template #default="{ row }">
            <span class="repo-tag">
              <el-icon><Connection /></el-icon>
              {{ row.git_source_name }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="150" align="center" header-align="center">
          <template #default="{ row }">
            <span class="status-badge" :class="row.status === 'open' ? 'status-open' : 'status-closed'">
              <span class="dot"></span>
              {{ row.status_display }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="执行状态" width="120" align="center" header-align="center">
          <template #default="{ row }">
            <span v-if="row.latest_execution_status" class="exec-badge" :class="'exec-' + row.latest_execution_status">
              {{ row.latest_execution_status }}
            </span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="源分支" width="200" show-overflow-tooltip header-align="center">
          <template #default="{ row }">
            <span class="branch-tag">{{ row.source_branch }}</span>
          </template>
        </el-table-column>
        <el-table-column label="更新时间" width="250" align="center" header-align="center">
          <template #default="{ row }">
            <span class="time-text">{{ row.updated_at }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right" align="center" header-align="center">
          <template #default="{ row }">
            <div class="action-group">
              <button class="action-btn view" title="查看" @click="handleViewDetail(row)">
                <el-icon><View /></el-icon>
              </button>
              <button class="action-btn edit" title="编辑" @click="handleEdit(row)">
                <el-icon><Edit /></el-icon>
              </button>
              <button v-if="row.status === 'open'" class="action-btn close" title="关闭" @click="handleClose(row)">
                <el-icon><CircleClose /></el-icon>
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
        <span class="pagination-info">共 {{ totalCount }} 条记录，第 {{ currentPage }} / {{ Math.ceil(totalCount / pageSize) || 1 }} 页</span>
        <div style="display: flex; align-items: center;">
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
          <div class="page-size-select">
            每页
            <select v-model.number="pageSize" @change="onPageSizeChange">
              <option :value="10">10</option>
              <option :value="20">20</option>
              <option :value="50">50</option>
            </select>
            条
          </div>
        </div>
      </div>
    </div>

    <!-- 创建对话框 -->
    <el-dialog v-model="createVisible" title="创建任务" width="480px" class="modern-dialog">
      <el-form :model="createForm" label-width="80px">
        <el-form-item label="标题" required>
          <el-input v-model="createForm.title" placeholder="输入任务标题" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="createForm.description" type="textarea" :rows="3" placeholder="输入任务描述" />
        </el-form-item>
        <el-form-item label="仓库源">
          <el-select v-model="createForm.git_source_id" placeholder="选择仓库源" clearable style="width: 100%" @focus="loadDropdown" @change="onGitSourceChange">
            <el-option v-for="item in gitSourceOptions" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="源分支">
          <el-select v-model="createForm.source_branch" placeholder="选择分支" clearable style="width: 100%" :loading="branchLoading" @change="onCreateBranchChange">
            <el-option v-for="branch in createBranchOptions" :key="branch" :label="branch" :value="branch" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCreateSave">创建</el-button>
      </template>
    </el-dialog>

    <!-- 编辑对话框 -->
    <el-dialog v-model="editVisible" title="编辑任务" width="480px" class="modern-dialog">
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="标题" required>
          <el-input v-model="editForm.title" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="editForm.description" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="源分支">
          <el-select v-model="editForm.source_branch" placeholder="选择分支" clearable style="width: 100%" :loading="branchLoading">
            <el-option v-for="branch in editBranchOptions" :key="branch" :label="branch" :value="branch" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" @click="handleEditSave">保存</el-button>
      </template>
    </el-dialog>

    <!-- 详情抽屉 -->
    <el-drawer v-model="detailVisible" size="520px" :with-header="false" class="modern-drawer">
      <div v-loading="detailLoading" class="drawer-content">
        <!-- 抽屉头部 -->
        <div class="drawer-header">
          <div>
            <h2>{{ detailTask?.title }}</h2>
            <div class="drawer-subtitle">{{ detailTask?.description || '' }}</div>
          </div>
          <el-button class="drawer-close-btn" @click="detailVisible = false">
            <el-icon><Close /></el-icon>
          </el-button>
        </div>

        <!-- 抽屉内容 -->
        <div class="drawer-body">
          <!-- 状态 + 关闭按钮 -->
          <div class="drawer-status-row">
            <span class="status-badge" :class="detailTask?.status === 'open' ? 'status-open' : 'status-closed'">
              <span class="dot"></span>
              {{ detailTask?.status_display }}
            </span>
            <el-button link type="danger" size="small" @click="handleCloseDetailTask" v-if="detailTask?.status === 'open'">
              <el-icon><CircleClose /></el-icon>
              关闭任务
            </el-button>
          </div>

          <!-- 任务信息 -->
          <div class="info-grid">
            <div class="info-item">
              <span class="info-label">仓库源</span>
              <span class="info-value">{{ detailTask?.git_source?.name || '-' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">平台</span>
              <span class="info-value">{{ detailTask?.git_source?.platform_display || '-' }}</span>
            </div>
            <div class="info-item full-width">
              <span class="info-label">源分支</span>
              <span class="info-value"><span class="branch-tag">{{ detailTask?.source_branch }}</span></span>
            </div>
            <div class="info-item full-width">
              <span class="info-label">最新执行状态</span>
              <span class="info-value">
                <span v-if="detailTask?.latest_execution_status" class="exec-badge" :class="'exec-' + detailTask.latest_execution_status">
                  {{ detailTask.latest_execution_status }}
                </span>
                <span v-else class="text-gray-400">暂无执行记录</span>
              </span>
            </div>
            <div class="info-item full-width">
              <span class="info-label">描述</span>
              <span class="info-value">{{ detailTask?.description || '-' }}</span>
            </div>
          </div>

          <div class="divider"></div>

          <!-- 对话区域 -->
          <div class="section-title">
            对话记录
            <span class="count">{{ conversations.length }}</span>
          </div>

          <div class="chat-container">
            <div class="chat-messages" ref="chatContainer">
              <div v-if="conversations.length === 0" class="chat-empty">
                暂无对话记录，输入第一条指令开始
              </div>
              <div v-for="msg in conversations" :key="msg.id" class="chat-msg" :class="msg.comment_type">
                <div class="chat-bubble">
                  <div class="agent-name">{{ msg.agent_name || msg.agent_code || 'AI' }}</div>
                  <div>{{ msg.content }}</div>
                  <div class="timestamp">{{ msg.created_at }}</div>
                </div>
              </div>
            </div>
            <div class="chat-input-area">
              <el-select v-model="selectedAgent" placeholder="选择 Agent" style="width: 110px" :disabled="detailTask?.status === 'closed'">
                <el-option v-for="agent in agentOptions" :key="agent.code" :label="agent.name" :value="agent.code" />
              </el-select>
              <el-input
                v-model="inputContent"
                placeholder="输入指令..."
                clearable
                @keyup.enter="handleSend"
                :disabled="detailTask?.status === 'closed' || sending"
              />
              <el-button type="primary" @click="handleSend" :loading="sending" :disabled="detailTask?.status === 'closed' || !inputContent || !selectedAgent">
                发送
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Connection, View, Edit, CircleClose, Delete, Close } from '@element-plus/icons-vue'
import {
  getTaskListApi,
  createTaskApi,
  updateTaskApi,
  deleteTaskApi,
  closeTaskApi,
  getTaskDetailApi,
  getConversationListApi,
  sendCommandApi,
} from '@/api/task'
import { getAgentListApi } from '@/api/agent'
import { getGitSourceDropdownApi, getRemoteBranchesApi } from '@/api/gitSource'
import type { TaskItem, TaskStatus, TaskDetail, ConversationItem } from '@/types/task'

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

// 仓库源
const gitSourceOptions = ref<Array<{ id: string; name: string; platform: string; default_branch?: string }>>([])
const dropdownLoaded = ref(false)

// 分支选项
const createBranchOptions = ref<string[]>([])
const editBranchOptions = ref<string[]>([])
const branchLoading = ref(false)

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

// 选择仓库源后加载分支
async function onGitSourceChange(sourceId: string) {
  const source = gitSourceOptions.value.find(s => s.id === sourceId)
  if (!source) {
    createBranchOptions.value = []
    createForm.value.source_branch = 'main'
    return
  }
  await loadBranches(source, 'create')
}

async function loadBranches(source: { id: string; name: string; platform: string; default_branch?: string }, mode: 'create' | 'edit') {
  branchLoading.value = true
  try {
    const resp = await getRemoteBranchesApi({
      source_id: source.id,
    } as any)
    const branches = resp.data.content?.branches || []
    const defaultBranch = resp.data.content?.default_branch || source.default_branch || 'main'

    if (mode === 'create') {
      createBranchOptions.value = branches.length > 0 ? branches : [defaultBranch]
      createForm.value.source_branch = defaultBranch
    } else {
      editBranchOptions.value = branches.length > 0 ? branches : [defaultBranch]
      editForm.value.source_branch = defaultBranch
    }
  } catch {
    // 如果 API 调用失败，使用默认分支
    const defaultBranch = source.default_branch || 'main'
    if (mode === 'create') {
      createBranchOptions.value = [defaultBranch]
      createForm.value.source_branch = defaultBranch
    } else {
      editBranchOptions.value = [defaultBranch]
      editForm.value.source_branch = defaultBranch
    }
  } finally {
    branchLoading.value = false
  }
}

function onCreateBranchChange() {
  // 创建时分支选择变化，可在此处添加额外逻辑
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

// 创建
function handleCreate() {
  createForm.value = { title: '', description: '', git_source_id: null, source_branch: 'main' }
  createBranchOptions.value = []
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
  editBranchOptions.value = [row.source_branch] // 默认显示当前分支
  editVisible.value = true
}

// 监听编辑对话框打开，加载分支选项
watch(editVisible, async (visible) => {
  if (!visible || !editId.value) return
  // 通过任务详情获取 git_source_id
  try {
    const resp = await getTaskDetailApi(editId.value!)
    const gitSource = resp.data.content?.git_source
    if (gitSource?.id) {
      await loadBranches({
        id: gitSource.id,
        name: gitSource.name,
        platform: gitSource.platform,
        default_branch: (gitSource as any).default_branch,
      }, 'edit')
      // 如果当前分支不在选项里，手动加入
      if (!editBranchOptions.value.includes(editForm.value.source_branch)) {
        editBranchOptions.value.unshift(editForm.value.source_branch)
      }
    }
  } catch {
    // 忽略
  }
})

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

// 关闭
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

// ===== 详情抽屉 =====
const detailVisible = ref(false)
const detailTask = ref<TaskDetail | null>(null)
const detailLoading = ref(false)
const conversations = ref<ConversationItem[]>([])
const sending = ref(false)
const inputContent = ref('')
const selectedAgent = ref('')
const agentOptions = ref<Array<{ code: string; name: string }>>([])
const chatContainer = ref<HTMLElement | null>(null)

// 查看详情
async function handleViewDetail(row: TaskItem) {
  detailVisible.value = true
  detailTask.value = null
  conversations.value = []
  await loadDetail(row.id)
  await Promise.all([loadConversations(row.id), loadAgents()])
}

async function loadDetail(id: string) {
  detailLoading.value = true
  try {
    const resp = await getTaskDetailApi(id)
    detailTask.value = resp.data.content
  } catch {
    ElMessage.error('加载任务详情失败')
  } finally {
    detailLoading.value = false
  }
}

async function loadConversations(taskId: string) {
  try {
    const resp = await getConversationListApi(taskId, { page: 1, page_size: 100 })
    conversations.value = resp.data.content?.results || []
    await nextTick()
    scrollToBottom()
  } catch {
    // 忽略
  }
}

async function loadAgents() {
  try {
    const resp = await getAgentListApi({ page: 1, page_size: 50 })
    agentOptions.value = (resp.data.content?.results || []).map((a: { code: string; name: string }) => ({
      code: a.code,
      name: a.name,
    }))
    if (agentOptions.value.length > 0) {
      selectedAgent.value = agentOptions.value[0].code
    }
  } catch {
    // 忽略
  }
}

function scrollToBottom() {
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

// 发送指令
async function handleSend() {
  if (!inputContent.value || !selectedAgent.value || !detailTask.value) return
  sending.value = true
  try {
    await sendCommandApi(detailTask.value.id, {
      content: inputContent.value,
      agent_code: selectedAgent.value,
    })
    inputContent.value = ''
    await loadConversations(detailTask.value.id)
  } catch {
    ElMessage.error('发送指令失败')
  } finally {
    sending.value = false
  }
}

// 关闭详情任务
async function handleCloseDetailTask() {
  if (!detailTask.value) return
  try {
    await ElMessageBox.confirm('确定要关闭此任务吗？', '确认关闭')
    await closeTaskApi(detailTask.value.id)
    ElMessage.success('任务已关闭')
    await loadDetail(detailTask.value.id)
    loadData()
  } catch {
    // 用户取消
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped lang="scss">
.task-management {
  max-width: 1400px;
  padding: 0;
}

/* 页面头部 */
.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 24px;
}

.page-header-left h1 {
  font-size: 24px;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: #0f172a;
}

.page-header-left p {
  color: #475569;
  font-size: 14px;
  margin-top: 4px;
}

.btn-create {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: #3b82f6;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  color: white;
  cursor: pointer;
  transition: all 0.15s ease;
  box-shadow: 0 1px 2px rgba(59, 130, 246, 0.3);

  &:hover {
    background: #2563eb;
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.35);
    transform: translateY(-1px);
  }
}

/* 统计卡片 */
.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 20px;
  transition: all 0.2s ease;

  &:hover {
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.06);
    border-color: #cbd5e1;
  }
}

.stat-label {
  font-size: 13px;
  color: #94a3b8;
  font-weight: 500;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: #0f172a;
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
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 8px 14px;
  width: 240px;
  transition: all 0.15s ease;

  &:focus-within {
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }

  :deep(.el-input__wrapper) {
    box-shadow: none !important;
    padding: 0 !important;
    background: transparent !important;
  }
}

.filter-select {
  width: 120px;
}

/* 表格容器 */
.table-container {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  overflow: hidden;
}

:deep(.el-table) {
  background: transparent;

  th.el-table__cell {
    background: #f8fafc;
    color: #94a3b8;
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    border-bottom: 1px solid #e2e8f0 !important;
  }

  td.el-table__cell {
    border-bottom: 1px solid #e2e8f0 !important;
    padding: 16px;
  }

  .el-table__row {
    transition: background 0.1s ease;

    &:hover {
      background: #f8fafc;
    }
  }
}

/* 任务标题和描述 */
.task-title {
  font-weight: 600;
  color: #0f172a;
  margin-bottom: 2px;
}

.task-desc {
  font-size: 12px;
  color: #94a3b8;
  max-width: 320px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 仓库标签 */
.repo-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: #f1f5f9;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  color: #475569;
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

.status-open {
  background: #ecfdf5;
  color: #059669;

  .dot { background: #10b981; }
}

.status-closed {
  background: #f1f5f9;
  color: #94a3b8;

  .dot { background: #94a3b8; }
}

/* 执行状态标签 */
.exec-badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
}

.exec-completed {
  background: #ecfdf5;
  color: #059669;
}

.exec-running {
  background: #fffbeb;
  color: #d97706;
}

.exec-failed {
  background: #fef2f2;
  color: #ef4444;
}

/* 分支标签 */
.branch-tag {
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 12px;
  background: #f5f3ff;
  color: #8b5cf6;
  padding: 3px 8px;
  border-radius: 4px;
  font-weight: 500;
}

.time-text {
  font-size: 13px;
  color: #475569;
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
  transition: all 0.15s ease;
  color: #94a3b8;

  &.view:hover { color: #3b82f6; background: #eff6ff; }
  &.edit:hover { color: #f59e0b; background: #fffbeb; }
  &.close:hover { color: #ef4444; background: #fef2f2; }
  &.delete:hover { color: #ef4444; background: #fef2f2; }
}

/* 分页 */
.pagination-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-top: 1px solid #e2e8f0;
}

.pagination-info {
  font-size: 13px;
  color: #94a3b8;
}

.page-size-select {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-left: 16px;
  font-size: 13px;
  color: #94a3b8;

  select {
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    padding: 4px 8px;
    font-size: 13px;
    color: #475569;
    background: white;
    outline: none;
    cursor: pointer;
  }
}

/* 抽屉样式 */
:deep(.modern-drawer) {
  .el-drawer__body {
    padding: 0;
  }
}

.drawer-content {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.drawer-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 24px 24px 20px;
  border-bottom: 1px solid #e2e8f0;

  h2 {
    font-size: 18px;
    font-weight: 700;
    letter-spacing: -0.01em;
  }
}

.drawer-subtitle {
  font-size: 13px;
  color: #94a3b8;
  margin-top: 4px;
}

.drawer-close-btn {
  border: none;
  background: transparent;
  color: #94a3b8;
  padding: 4px;

  &:hover {
    background: #f1f5f9;
    color: #0f172a;
  }
}

.drawer-body {
  flex: 1;
  overflow-y: auto;
  padding: 20px 24px;
}

.drawer-status-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;

  &.full-width {
    grid-column: 1 / -1;
  }
}

.info-label {
  font-size: 12px;
  font-weight: 600;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.info-value {
  font-size: 14px;
  color: #0f172a;
}

.divider {
  height: 1px;
  background: #e2e8f0;
  margin: 20px 0;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: #0f172a;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 8px;

  .count {
    background: #f1f5f9;
    color: #94a3b8;
    font-size: 11px;
    padding: 2px 8px;
    border-radius: 10px;
    font-weight: 600;
  }
}

/* 对话容器 */
.chat-container {
  display: flex;
  flex-direction: column;
  height: 360px;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  overflow: hidden;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.chat-empty {
  text-align: center;
  color: #94a3b8;
  padding: 32px 0;
}

.chat-msg {
  margin-bottom: 12px;
  display: flex;

  &.user { justify-content: flex-end; }
  &.ai { justify-content: flex-start; }
  &.system { justify-content: center; }
}

.chat-bubble {
  max-width: 75%;
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 13px;
  line-height: 1.5;
}

.chat-msg.user .chat-bubble {
  background: #3b82f6;
  color: white;
  border-bottom-right-radius: 4px;
}

.chat-msg.ai .chat-bubble {
  background: #f1f5f9;
  color: #0f172a;
  border-bottom-left-radius: 4px;
}

.chat-msg.system .chat-bubble {
  background: transparent;
  color: #94a3b8;
  font-size: 12px;
  padding: 4px 12px;
}

.agent-name {
  font-size: 11px;
  opacity: 0.7;
  margin-bottom: 4px;
  font-weight: 600;
}

.timestamp {
  font-size: 10px;
  opacity: 0.6;
  margin-top: 4px;
}

.chat-input-area {
  border-top: 1px solid #e2e8f0;
  padding: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
  background: #f8fafc;
}

/* 对话框样式 */
:deep(.modern-dialog) {
  .el-dialog__header {
    padding: 20px 24px;
    border-bottom: 1px solid #e2e8f0;
  }

  .el-dialog__body {
    padding: 24px;
  }

  .el-dialog__footer {
    padding: 16px 24px;
    border-top: 1px solid #e2e8f0;
    background: #f8fafc;
  }
}
</style>
