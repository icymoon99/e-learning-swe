<template>
  <div class="executor-management">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="page-header-left">
        <h1>执行器管理</h1>
        <p>管理 Agent 的执行引擎配置</p>
      </div>
    </div>

    <!-- 列表表格 -->
    <div class="table-container">
      <el-table :data="tableData" v-loading="loading" :show-header="true">
        <el-table-column prop="code" label="编码" width="150" />
        <el-table-column prop="name" label="名称" min-width="200" />
        <el-table-column label="状态" width="120">
          <template #default="{ row }">
            <el-switch
              v-model="row.enabled"
              @change="handleToggleEnabled(row)"
              :loading="row._saving"
            />
          </template>
        </el-table-column>
        <el-table-column prop="timeout" label="超时（秒）" width="120" />
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <div class="action-group">
              <button class="action-btn edit" title="编辑" @click="handleEdit(row)">
                <el-icon><Edit /></el-icon>
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

    <!-- 编辑抽屉 -->
    <el-drawer v-model="drawerVisible" size="560px" :with-header="false" class="modern-drawer">
      <div v-loading="drawerLoading" class="drawer-content">
        <!-- 抽屉头部 -->
        <div class="drawer-header">
          <div>
            <h2>{{ editingExecutor?.name }}</h2>
            <div class="drawer-subtitle">{{ editingExecutor?.code }}</div>
          </div>
          <el-button class="drawer-close-btn" @click="drawerVisible = false">
            <el-icon><Close /></el-icon>
          </el-button>
        </div>

        <!-- 抽屉内容 -->
        <div class="drawer-body">
          <!-- 只读信息 -->
          <div class="info-grid">
            <div class="info-item">
              <span class="info-label">编码</span>
              <span class="info-value">{{ editingExecutor?.code }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">超时</span>
              <span class="info-value">{{ editingExecutor?.timeout }} 秒</span>
            </div>
          </div>

          <!-- 启用开关 -->
          <div class="enabled-row">
            <span class="info-label">启用状态</span>
            <el-switch v-model="editForm.enabled" />
          </div>

          <div class="divider"></div>

          <!-- Metadata 表单 -->
          <div v-for="(group, groupKey) in editForm.metadata_schema_input" :key="groupKey">
            <div class="section-title">{{ getGroupLabel(groupKey) }}</div>
            <el-form label-position="top" v-if="Object.keys(group).length > 0">
              <el-form-item
                v-for="(field, fieldKey) in group"
                :key="fieldKey"
                :label="field.label"
                :required="field.required"
              >
                <template #extra v-if="field.hint">{{ field.hint }}</template>
                <el-input
                  v-if="field.type === 'password'"
                  v-model="(field.value as string)"
                  type="password"
                  show-password
                  :placeholder="field.label"
                />
                <el-input-number
                  v-else-if="field.type === 'number'"
                  v-model="(field.value as number)"
                  style="width: 100%"
                />
                <el-input
                  v-else
                  v-model="(field.value as string)"
                  type="textarea"
                  :rows="field.type === 'textarea' ? 3 : 1"
                  :placeholder="field.label"
                />
              </el-form-item>
            </el-form>
            <div v-else class="empty-group">暂无配置项</div>
          </div>
        </div>

        <!-- 底部按钮 -->
        <div class="drawer-footer">
          <el-button @click="drawerVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSave" :loading="saving">保存</el-button>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Edit, Close } from '@element-plus/icons-vue'
import { getExecutorListApi, getExecutorDetailApi, updateExecutorApi } from '@/api/executor'
import type { Executor, UpdateExecutorParams } from '@/types/executor'

// 状态
const loading = ref(false)
const tableData = ref<Executor[]>([])
const currentPage = ref(1)
const pageSize = ref(10)
const totalCount = ref(0)

const totalPages = computed(() => Math.ceil(totalCount.value / pageSize.value))

// 加载数据
async function loadData() {
  loading.value = true
  try {
    const resp = await getExecutorListApi({ page: currentPage.value, page_size: pageSize.value })
    tableData.value = resp.data.content?.results || []
    totalCount.value = resp.data.content?.count || 0
  } catch {
    ElMessage.error('加载执行器列表失败')
  } finally {
    loading.value = false
  }
}

function onPageSizeChange() { currentPage.value = 1; loadData() }

// 快速切换 enabled
async function handleToggleEnabled(row: Executor) {
  row._saving = true
  try {
    await updateExecutorApi(row.id, { enabled: row.enabled, metadata_schema_input: row.metadata_schema })
    ElMessage.success('状态已更新')
  } catch {
    ElMessage.error('更新失败')
    row.enabled = !row.enabled
  } finally {
    delete row._saving
  }
}

// 编辑抽屉
const drawerVisible = ref(false)
const drawerLoading = ref(false)
const saving = ref(false)
const editingExecutor = ref<Executor | null>(null)
const editForm = ref<UpdateExecutorParams>({ enabled: true, metadata_schema_input: { env_vars: {}, cli_args: {} } })

function getGroupLabel(key: string): string {
  const labels: Record<string, string> = { env_vars: '环境变量', cli_args: '运行参数' }
  return labels[key] || key
}

async function handleEdit(row: Executor) {
  drawerVisible.value = true
  drawerLoading.value = true
  editingExecutor.value = null
  try {
    const resp = await getExecutorDetailApi(row.id)
    editingExecutor.value = resp.data.content
    editForm.value = {
      enabled: resp.data.content.enabled,
      metadata_schema_input: JSON.parse(JSON.stringify(resp.data.content.metadata_schema)),
    }
  } catch {
    ElMessage.error('加载详情失败')
  } finally {
    drawerLoading.value = false
  }
}

async function handleSave() {
  if (!editingExecutor.value) return
  saving.value = true
  try {
    await updateExecutorApi(editingExecutor.value.id, editForm.value)
    ElMessage.success('保存成功')
    drawerVisible.value = false
    loadData()
  } catch {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

onMounted(() => loadData())
</script>

<style scoped lang="scss">
.executor-management {
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

/* 抽屉样式 */
:deep(.modern-drawer) {
  .el-drawer__body { padding: 0; }
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
  border-bottom: 1px solid var(--border-light);

  h2 {
    font-size: 18px;
    font-weight: 700;
    letter-spacing: -0.01em;
  }
}

.drawer-subtitle {
  font-size: 13px;
  color: var(--text-tertiary);
  margin-top: 4px;
  font-family: 'SF Mono', 'Fira Code', monospace;
}

.drawer-close-btn {
  border: none;
  background: transparent;
  color: var(--text-tertiary);
  padding: 4px;

  &:hover {
    background: #f1f5f9;
    color: var(--text-primary);
  }
}

.drawer-body {
  flex: 1;
  overflow-y: auto;
  padding: 20px 24px;
}

.drawer-footer {
  padding: 16px 24px;
  border-top: 1px solid var(--border-light);
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  background: #f8fafc;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 16px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.info-value {
  font-size: 14px;
  color: var(--text-primary);
}

.enabled-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.divider {
  height: 1px;
  background: var(--border-light);
  margin: 20px 0;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border-light);
}

.empty-group {
  color: var(--text-tertiary);
  font-size: 13px;
  padding: 12px 0;
  text-align: center;
}
</style>
