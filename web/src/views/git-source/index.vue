<template>
  <div class="git-source-management">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="page-header-left">
        <h1>仓库源管理</h1>
        <p>管理和配置 Git 仓库源</p>
      </div>
      <el-button type="primary" class="btn-create" @click="handleCreate">
        <el-icon><Plus /></el-icon>
        添加仓库源
      </el-button>
    </div>

    <!-- 筛选栏 -->
    <div class="filter-bar">
      <div class="search-input">
        <el-icon><Search /></el-icon>
        <el-input v-model="searchName" placeholder="搜索名称..." clearable @clear="loadData" @keyup.enter="loadData" />
      </div>
      <el-select v-model="filterPlatform" placeholder="全部平台" clearable class="filter-select" @change="onFilterChange">
        <el-option label="GitHub" value="github" />
        <el-option label="Gitee" value="gitee" />
        <el-option label="GitLab" value="gitlab" />
      </el-select>
    </div>

    <!-- 表格 -->
    <div class="table-container">
      <el-table :data="tableData" v-loading="loading" :show-header="true">
        <el-table-column prop="name" label="名称" min-width="150" show-overflow-tooltip />
        <el-table-column label="平台" width="120">
          <template #default="{ row }">
            <span class="status-badge" :class="'platform-' + row.platform">
              <span class="dot"></span>
              {{ row.platform_display }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="repo_url" label="仓库地址" min-width="150" show-overflow-tooltip />
        <el-table-column prop="default_branch" label="默认分支" min-width="200" show-overflow-tooltip />
        <el-table-column prop="description" label="描述" min-width="150" show-overflow-tooltip />
        <el-table-column prop="created_at" label="创建时间" width="250" />
        <el-table-column label="操作" width="120" fixed="right">
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
    <el-dialog v-model="formVisible" :title="formTitle" width="650px" class="modern-dialog" @closed="resetForm">
      <el-form :model="form" label-width="100px">
        <el-form-item label="名称" required>
          <el-input v-model="form.name" placeholder="仓库源名称" :disabled="!!editingId" />
        </el-form-item>
        <el-form-item label="平台" required>
          <el-select v-model="form.platform" style="width: 100%" @change="onPlatformChange">
            <el-option label="GitHub" value="github" />
            <el-option label="Gitee" value="gitee" />
            <el-option label="GitLab" value="gitlab" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="form.platform === 'gitlab'" label="平台地址">
          <el-input v-model="form.api_url" placeholder="https://git.example.com（可选）" />
        </el-form-item>
        <el-form-item label="Token" :required="!editingId">
          <div class="flex gap-2 w-full">
            <el-input
              v-model="form.token"
              type="password"
              show-password
              :placeholder="editingId ? '不修改请留空' : '访问令牌'"
              class="flex-1"
            />
            <el-button
              type="primary"
              :loading="fetchingRepos"
              :disabled="!form.platform || !form.token"
              @click="handleFetchRepos"
            >
              获取仓库
            </el-button>
          </div>
        </el-form-item>
        <el-form-item label="仓库地址" required>
          <el-select
            v-model="form.repo_url"
            filterable
            placeholder="先输入 Token 并点击「获取仓库」"
            style="width: 100%"
            @change="onRepoChange"
          >
            <el-option
              v-for="repo in remoteRepos"
              :key="repo.full_name"
              :label="`${repo.full_name} (${repo.default_branch})`"
              :value="repo.url"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="默认分支">
          <el-select v-model="form.default_branch" placeholder="选择分支" style="width: 100%">
            <el-option
              v-for="branch in remoteBranches"
              :key="branch"
              :label="branch"
              :value="branch"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="2" placeholder="仓库描述" />
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
  getGitSourceListApi,
  createGitSourceApi,
  updateGitSourceApi,
  deleteGitSourceApi,
  getRemoteReposApi,
  getRemoteBranchesApi,
} from '@/api/gitSource'
import type { GitSource, GitPlatform, RemoteRepo } from '@/types/gitSource'

// 状态
const loading = ref(false)
const tableData = ref<GitSource[]>([])
const currentPage = ref(1)
const pageSize = ref(10)
const totalCount = ref(0)
const searchName = ref('')
const filterPlatform = ref<GitPlatform | ''>('')

const totalPages = computed(() => Math.ceil(totalCount.value / pageSize.value))

// 创建/编辑表单
const formVisible = ref(false)
const editingId = ref<string | null>(null)
const formTitle = ref('添加仓库源')
const form = ref({
  name: '',
  platform: 'github' as GitPlatform,
  api_url: '',
  repo_url: '',
  token: '',
  default_branch: 'main',
  description: '',
})

// 远程仓库和分支数据
const remoteRepos = ref<RemoteRepo[]>([])
const remoteBranches = ref<string[]>([])
const fetchingRepos = ref(false)
const fetchingBranches = ref(false)

// 加载数据
async function loadData() {
  loading.value = true
  try {
    const params: Record<string, unknown> = { page: currentPage.value, page_size: pageSize.value }
    if (searchName.value) params.search = searchName.value
    if (filterPlatform.value) params.platform = filterPlatform.value

    const resp = await getGitSourceListApi(params)
    tableData.value = resp.data.content?.results || []
    totalCount.value = resp.data.content?.count || 0
  } catch {
    ElMessage.error('加载仓库源列表失败')
  } finally {
    loading.value = false
  }
}

function onFilterChange() { currentPage.value = 1; loadData() }
function onPageSizeChange() { currentPage.value = 1; loadData() }

// 创建
function handleCreate() {
  editingId.value = null
  formTitle.value = '添加仓库源'
  form.value = { name: '', platform: 'github', api_url: '', repo_url: '', token: '', default_branch: 'main', description: '' }
  remoteRepos.value = []
  remoteBranches.value = []
  formVisible.value = true
}

// 编辑
function handleEdit(row: GitSource) {
  editingId.value = row.id
  formTitle.value = '编辑仓库源'
  form.value = { name: row.name, platform: row.platform, api_url: '', repo_url: row.repo_url, token: '', default_branch: row.default_branch, description: row.description }
  remoteRepos.value = []
  remoteBranches.value = []
  formVisible.value = true
}

// 平台切换时清空远程数据
function onPlatformChange() {
  remoteRepos.value = []
  remoteBranches.value = []
  form.value.repo_url = ''
  form.value.default_branch = 'main'
  form.value.description = ''
}

// 获取远程仓库列表
async function handleFetchRepos() {
  if (!form.value.platform || !form.value.token) {
    ElMessage.warning('请先选择平台并输入 Token')
    return
  }

  fetchingRepos.value = true
  try {
    const resp = await getRemoteReposApi({
      platform: form.value.platform,
      token: form.value.token,
      ...(form.value.platform === 'gitlab' && form.value.api_url
        ? { api_url: form.value.api_url }
        : {}),
    })
    const repos = resp.data.content?.repos || []
    remoteRepos.value = repos
    if (repos.length === 0) {
      ElMessage.warning('该 Token 没有可访问的仓库')
    } else {
      ElMessage.success(`获取到 ${repos.length} 个仓库`)
    }
  } catch (e: unknown) {
    const msg = e instanceof Error ? e.message : '获取仓库列表失败'
    ElMessage.error(msg)
  } finally {
    fetchingRepos.value = false
  }
}

// 选择仓库后获取分支列表
async function onRepoChange(url: string) {
  if (!url || !form.value.token) return

  const repo = remoteRepos.value.find(r => r.url === url)
  if (!repo) return

  form.value.description = repo.description
  form.value.default_branch = repo.default_branch

  fetchingBranches.value = true
  try {
    const resp = await getRemoteBranchesApi({
      platform: form.value.platform,
      token: form.value.token,
      repo_full_name: repo.full_name,
      ...(form.value.platform === 'gitlab' && form.value.api_url
        ? { api_url: form.value.api_url }
        : {}),
    })
    const data = resp.data.content
    if (data?.branches) {
      remoteBranches.value = data.branches
    }
  } catch {
    ElMessage.warning('获取分支列表失败')
  } finally {
    fetchingBranches.value = false
  }
}

// 保存
async function handleSave() {
  if (!form.value.name) { ElMessage.warning('名称为必填字段'); return }
  if (!form.value.repo_url) { ElMessage.warning('请选择仓库地址'); return }
  if (!editingId.value && !form.value.token) { ElMessage.warning('Token 为必填字段'); return }

  try {
    if (editingId.value) {
      const updateData: Record<string, unknown> = { name: form.value.name, platform: form.value.platform, repo_url: form.value.repo_url, default_branch: form.value.default_branch, description: form.value.description }
      if (form.value.token) { updateData.token = form.value.token }
      await updateGitSourceApi(editingId.value, updateData)
      ElMessage.success('更新成功')
    } else {
      await createGitSourceApi({ name: form.value.name, platform: form.value.platform, repo_url: form.value.repo_url, token: form.value.token, default_branch: form.value.default_branch, description: form.value.description })
      ElMessage.success('创建成功')
    }
    formVisible.value = false
    loadData()
  } catch { /* 响应拦截器已显示错误 */ }
}

function resetForm() {
  form.value = { name: '', platform: 'github', api_url: '', repo_url: '', token: '', default_branch: 'main', description: '' }
  remoteRepos.value = []
  remoteBranches.value = []
  editingId.value = null
}

// 删除
async function handleDelete(row: GitSource) {
  try {
    await ElMessageBox.confirm(`确定要删除仓库源 "${row.name}" 吗？此操作不可撤销。`, '确认删除')
    await deleteGitSourceApi(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch { /* 用户取消 */ }
}

onMounted(() => { loadData() })
</script>

<style scoped lang="scss">
.git-source-management {
  max-width: 1400px;
  position: relative;
  z-index: 1;
}

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

.platform-github {
  background: #f1f5f9;
  color: #475569;
  .dot { background: #475569; }
}

.platform-gitee {
  background: #ecfdf5;
  color: #059669;
  .dot { background: #10b981; }
}

.platform-gitlab {
  background: #fffbeb;
  color: #d97706;
  .dot { background: #f59e0b; }
}

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
