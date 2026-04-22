<template>
  <div class="git-source-management p-4">
    <!-- 顶部操作栏 -->
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-xl font-semibold">仓库源管理</h2>
      <el-button type="primary" @click="handleCreate">
        添加仓库源
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
      <el-select v-model="filterPlatform" placeholder="平台" clearable style="width: 120px" @change="onFilterChange">
        <el-option label="GitHub" value="github" />
        <el-option label="Gitee" value="gitee" />
        <el-option label="GitLab" value="gitlab" />
      </el-select>
    </div>

    <!-- 仓库源列表表格 -->
    <el-table :data="tableData" v-loading="loading" stripe border>
      <el-table-column prop="name" label="名称" min-width="150" show-overflow-tooltip />
      <el-table-column label="平台" width="100">
        <template #default="{ row }">
          <el-tag :type="getPlatformTagType(row.platform)" size="small">
            {{ row.platform_display }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="repo_url" label="仓库地址" min-width="250" show-overflow-tooltip />
      <el-table-column prop="default_branch" label="默认分支" width="120" />
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
      <el-form :model="form" label-width="100px">
        <el-form-item label="名称" required>
          <el-input v-model="form.name" placeholder="仓库源名称" :disabled="!!editingId" />
        </el-form-item>
        <el-form-item label="平台" required>
          <el-select v-model="form.platform" style="width: 100%">
            <el-option label="GitHub" value="github" />
            <el-option label="Gitee" value="gitee" />
            <el-option label="GitLab" value="gitlab" />
          </el-select>
        </el-form-item>
        <el-form-item label="仓库地址" required>
          <el-input v-model="form.repo_url" placeholder="https://github.com/owner/repo.git" />
        </el-form-item>
        <el-form-item label="Token" required>
          <el-input v-model="form.token" type="password" show-password placeholder="访问令牌" />
        </el-form-item>
        <el-form-item label="默认分支">
          <el-input v-model="form.default_branch" placeholder="main" />
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
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getGitSourceListApi,
  createGitSourceApi,
  updateGitSourceApi,
  deleteGitSourceApi,
} from '@/api/gitSource'
import type { GitSource, GitPlatform } from '@/types/gitSource'

// 状态
const loading = ref(false)
const tableData = ref<GitSource[]>([])
const currentPage = ref(1)
const pageSize = ref(10)
const totalCount = ref(0)
const searchName = ref('')
const filterPlatform = ref<GitPlatform | ''>('')

// 创建/编辑表单
const formVisible = ref(false)
const editingId = ref<string | null>(null)
const formTitle = ref('添加仓库源')
const form = ref({
  name: '',
  platform: 'github' as GitPlatform,
  repo_url: '',
  token: '',
  default_branch: 'main',
  description: '',
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
  formTitle.value = '添加仓库源'
  form.value = {
    name: '',
    platform: 'github',
    repo_url: '',
    token: '',
    default_branch: 'main',
    description: '',
  }
  formVisible.value = true
}

// 编辑
function handleEdit(row: GitSource) {
  editingId.value = row.id
  formTitle.value = '编辑仓库源'
  form.value = {
    name: row.name,
    platform: row.platform,
    repo_url: row.repo_url,
    token: '',
    default_branch: row.default_branch,
    description: row.description,
  }
  formVisible.value = true
}

// 保存
async function handleSave() {
  if (!form.value.name) {
    ElMessage.warning('名称为必填字段')
    return
  }
  if (!form.value.repo_url) {
    ElMessage.warning('仓库地址为必填字段')
    return
  }

  try {
    if (editingId.value) {
      await updateGitSourceApi(editingId.value, {
        name: form.value.name,
        platform: form.value.platform,
        repo_url: form.value.repo_url,
        ...(form.value.token && { token: form.value.token }),
        default_branch: form.value.default_branch,
        description: form.value.description,
      })
      ElMessage.success('更新成功')
    } else {
      await createGitSourceApi({
        name: form.value.name,
        platform: form.value.platform,
        repo_url: form.value.repo_url,
        token: form.value.token,
        default_branch: form.value.default_branch,
        description: form.value.description,
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
    name: '',
    platform: 'github',
    repo_url: '',
    token: '',
    default_branch: 'main',
    description: '',
  }
  editingId.value = null
}

// 删除
async function handleDelete(row: GitSource) {
  try {
    await ElMessageBox.confirm(`确定要删除仓库源 "${row.name}" 吗？此操作不可撤销。`, '确认删除')
    await deleteGitSourceApi(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch {
    // 用户取消
  }
}

// 平台标签颜色
function getPlatformTagType(platform: string): string {
  const map: Record<string, string> = { github: '', gitee: 'success', gitlab: 'warning' }
  return map[platform] || 'info'
}

onMounted(() => {
  loadData()
})
</script>
