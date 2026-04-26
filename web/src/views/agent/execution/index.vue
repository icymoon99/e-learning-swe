<template>
  <div class="agent-execution">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="page-header-left">
        <h1>执行日志</h1>
        <p>查看和跟踪 Agent 执行记录</p>
      </div>
      <el-button class="btn-refresh" @click="loadData">
        <el-icon><Refresh /></el-icon>
        刷新
      </el-button>
    </div>

    <!-- 筛选栏 -->
    <div class="filter-bar">
      <div class="search-input">
        <el-icon><Search /></el-icon>
        <el-input v-model="searchThreadId" placeholder="搜索 Thread ID..." clearable @clear="loadData" @keyup.enter="loadData" />
      </div>
      <el-select v-model="filterStatus" placeholder="全部状态" clearable class="filter-select" @change="onFilterChange">
        <el-option label="执行中" value="running" />
        <el-option label="已完成" value="completed" />
        <el-option label="失败" value="failed" />
      </el-select>
    </div>

    <!-- 表格 -->
    <div class="table-container">
      <el-table :data="tableData" v-loading="loading" :show-header="true" :header-cell-style="{ textAlign: 'center' }">
        <el-table-column prop="agent_code" label="Agent 编码" width="150" header-align="center" />
        <el-table-column prop="agent_name" label="Agent 名称" min-width="150" show-overflow-tooltip header-align="center" />
        <el-table-column prop="thread_id" label="Thread ID" min-width="200" show-overflow-tooltip header-align="center" />
        <el-table-column label="状态" width="120" align="center" header-align="center">
          <template #default="{ row }">
            <span class="status-badge" :class="getStatusClass(row.status)">
              <span class="dot"></span>
              {{ row.status_display }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="error_message" label="错误信息" min-width="200" show-overflow-tooltip header-align="center" />
        <el-table-column prop="created_at" label="创建时间" width="200" align="center" header-align="center" />
        <el-table-column label="操作" width="100" fixed="right" align="center" header-align="center">
          <template #default="{ row }">
            <div class="action-group">
              <button class="action-btn view" title="详情" @click="handleDetail(row)">
                <el-icon><View /></el-icon>
              </button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-bar">
        <span class="pagination-info">共 {{ totalCount }} 条记录，第 {{ currentPage }} / {{ Math.ceil(totalCount / pageSize) || 1 }} 页</span>
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

    <!-- 详情抽屉 -->
    <el-drawer v-model="detailVisible" title="执行详情" size="550px" class="modern-drawer">
      <div v-if="selectedLog" class="drawer-content">
        <div class="detail-header">
          <h2>{{ selectedLog.agent_name }} <span class="mono-code">({{ selectedLog.agent_code }})</span></h2>
          <span class="status-badge" :class="getStatusClass(selectedLog.status)">
            <span class="dot"></span>
            {{ selectedLog.status_display }}
          </span>
        </div>

        <div class="detail-grid">
          <div class="detail-item full-width">
            <span class="detail-label">Agent 编码</span>
            <span class="detail-value mono">{{ selectedLog.agent_code }}</span>
          </div>
          <div class="detail-item full-width">
            <span class="detail-label">Thread ID</span>
            <span class="detail-value mono">{{ selectedLog.thread_id }}</span>
          </div>
          <div class="detail-item full-width" v-if="selectedLog.error_message">
            <span class="detail-label">错误信息</span>
            <span class="detail-value error-text">{{ selectedLog.error_message }}</span>
          </div>
          <div class="detail-item full-width" v-if="selectedLog.result">
            <span class="detail-label">执行结果</span>
            <pre class="json-block">{{ formatJson(selectedLog.result) }}</pre>
          </div>
          <div class="detail-item full-width" v-if="selectedLog.events">
            <span class="detail-label">事件流</span>
            <pre class="json-block">{{ formatJson(selectedLog.events) }}</pre>
          </div>
          <div class="detail-item">
            <span class="detail-label">创建时间</span>
            <span class="detail-value">{{ selectedLog.created_at }}</span>
          </div>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, Search, View } from '@element-plus/icons-vue'
import { getExecutionListApi } from '@/api/agent'
import type { AgentExecutionLog, ExecutionStatus } from '@/types/agent'

// 状态
const loading = ref(false)
const tableData = ref<AgentExecutionLog[]>([])
const currentPage = ref(1)
const pageSize = ref(10)
const totalCount = ref(0)
const filterStatus = ref<ExecutionStatus | ''>('')
const searchThreadId = ref('')

// 详情抽屉
const detailVisible = ref(false)
const selectedLog = ref<AgentExecutionLog | null>(null)

// 加载数据
async function loadData() {
  loading.value = true
  try {
    const params: Record<string, unknown> = {
      page: currentPage.value,
      page_size: pageSize.value,
    }
    if (filterStatus.value) params.status = filterStatus.value
    if (searchThreadId.value) params.thread_id = searchThreadId.value

    const resp = await getExecutionListApi(params)
    tableData.value = resp.data.content?.results || []
    totalCount.value = resp.data.content?.count || 0
  } catch {
    ElMessage.error('加载执行日志失败')
  } finally {
    loading.value = false
  }
}

function onFilterChange() { currentPage.value = 1; loadData() }
function onPageSizeChange() { currentPage.value = 1; loadData() }

// 详情
function handleDetail(row: AgentExecutionLog) {
  selectedLog.value = row
  detailVisible.value = true
}

// 状态样式
function getStatusClass(status: string): string {
  const map: Record<string, string> = {
    running: 'status-running',
    completed: 'status-active',
    failed: 'status-error',
  }
  return map[status] || 'status-inactive'
}

// JSON 格式化
function formatJson(data: unknown): string {
  if (!data) return '无'
  try {
    return JSON.stringify(data, null, 2)
  } catch {
    return String(data)
  }
}

onMounted(() => { loadData() })
</script>

<style scoped lang="scss">
/* ====== 页面布局 ====== */
.agent-execution {
  max-width: 1400px;
  padding: 0;
}

/* ====== 页面头部 ====== */
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

.btn-refresh {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: var(--primary);
  border: none;
  padding: 8px 16px;
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

/* ====== 筛选栏 ====== */
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
  width: 280px;
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
  width: 130px;
}

/* ====== 表格容器 ====== */
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
    &:hover { background: rgba(248, 250, 252, 0.6); cursor: pointer; }
  }
}

/* ====== 状态标签 ====== */
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

.status-running {
  background: #fffbeb;
  color: #d97706;
  .dot { background: #f59e0b; }
}

.status-error {
  background: #fef2f2;
  color: #ef4444;
  .dot { background: #ef4444; }
}

.status-inactive {
  background: #f1f5f9;
  color: #94a3b8;
  .dot { background: #94a3b8; }
}

/* ====== 操作按钮 ====== */
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
  &.delete:hover { color: #ef4444; background: #fef2f2; }
}

/* ====== 分页 ====== */
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

/* ====== 抽屉 ====== */
:deep(.modern-drawer) {
  .el-drawer__header {
    margin-bottom: 0;
    padding: 20px 24px;
    border-bottom: 1px solid #e2e8f0;
  }
}

.drawer-content {
  padding: 20px 24px;
}

.detail-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;

  h2 {
    font-size: 18px;
    font-weight: 700;
    letter-spacing: -0.01em;
    color: #0f172a;
  }
}

.mono-code {
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 14px;
  color: #64748b;
}

.detail-grid {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 4px;

  &.full-width {
    grid-column: 1 / -1;
  }
}

.detail-label {
  font-size: 11px;
  font-weight: 600;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.detail-value {
  font-size: 14px;
  color: #0f172a;
  word-break: break-all;

  &.mono {
    font-family: 'SF Mono', 'Fira Code', monospace;
    font-size: 13px;
  }

  &.error-text {
    color: #ef4444;
    font-weight: 500;
  }
}

.json-block {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 12px;
  font-size: 12px;
  font-family: 'SF Mono', 'Fira Code', monospace;
  max-height: 300px;
  overflow: auto;
  line-height: 1.5;
  color: #334155;
  margin: 0;
}

/* ====== 滚动条 ====== */
.json-block::-webkit-scrollbar {
  width: 4px;
  height: 4px;
}

.json-block::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 2px;
}
</style>
