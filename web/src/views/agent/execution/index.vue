<template>
  <div class="agent-execution p-4">
    <!-- 顶部 -->
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-xl font-semibold">执行日志</h2>
      <el-button size="small" @click="loadData">
        刷新
      </el-button>
    </div>

    <!-- 过滤栏 -->
    <div class="flex items-center gap-3 mb-4">
      <el-select v-model="filterStatus" placeholder="状态" clearable style="width: 120px" @change="onFilterChange">
        <el-option label="执行中" value="running" />
        <el-option label="已完成" value="completed" />
        <el-option label="失败" value="failed" />
      </el-select>
      <el-input
        v-model="searchThreadId"
        placeholder="搜索 Thread ID"
        clearable
        style="width: 250px"
        @clear="loadData"
        @keyup.enter="loadData"
      />
    </div>

    <!-- 执行日志表格 -->
    <el-table :data="tableData" v-loading="loading" stripe border @row-click="handleDetail">
      <el-table-column prop="agent_code" label="Agent 编码" width="150" />
      <el-table-column prop="agent_name" label="Agent 名称" min-width="150" show-overflow-tooltip />
      <el-table-column prop="thread_id" label="Thread ID" min-width="200" show-overflow-tooltip />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="getExecutionTagType(row.status)" size="small">
            {{ row.status_display }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="error_message" label="错误信息" min-width="200" show-overflow-tooltip />
      <el-table-column prop="created_at" label="创建时间" width="180" />
      <el-table-column label="操作" width="100" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" size="small" @click.stop="handleDetail(row)">详情</el-button>
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

    <!-- 详情抽屉 -->
    <el-drawer v-model="detailVisible" title="执行详情" size="550px">
      <el-descriptions :column="1" border v-if="selectedLog">
        <el-descriptions-item label="Agent">{{ selectedLog.agent_name }} ({{ selectedLog.agent_code }})</el-descriptions-item>
        <el-descriptions-item label="Thread ID">{{ selectedLog.thread_id }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getExecutionTagType(selectedLog.status)" size="small">
            {{ selectedLog.status_display }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="结果">
          <pre class="text-xs bg-gray-50 p-2 rounded max-h-40 overflow-auto">{{ formatJson(selectedLog.result) }}</pre>
        </el-descriptions-item>
        <el-descriptions-item label="错误信息" v-if="selectedLog.error_message">
          <span class="text-red-500">{{ selectedLog.error_message }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="事件流">
          <pre class="text-xs bg-gray-50 p-2 rounded max-h-60 overflow-auto">{{ formatJson(selectedLog.events) }}</pre>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ selectedLog.created_at }}</el-descriptions-item>
      </el-descriptions>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
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

function onFilterChange() {
  currentPage.value = 1
  loadData()
}

function onPageSizeChange() {
  currentPage.value = 1
  loadData()
}

// 详情
function handleDetail(row: AgentExecutionLog) {
  selectedLog.value = row
  detailVisible.value = true
}

// 状态标签颜色
function getExecutionTagType(status: string): string {
  const map: Record<string, string> = { running: 'warning', completed: 'success', failed: 'danger' }
  return map[status] || 'info'
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

onMounted(() => {
  loadData()
})
</script>
