<template>
  <div class="q2-task-management p-4">
    <!-- 顶部状态栏 -->
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-xl font-semibold">Django-Q2 任务管理</h2>
      <div class="flex items-center gap-3">
        <el-tag :type="queueStatus.worker_running ? 'success' : 'danger'" size="small">
          {{ queueStatus.worker_running ? 'Worker 运行中' : 'Worker 已停止' }}
        </el-tag>
        <el-button size="small" @click="handleToggleQueue">
          {{ queueStatus.worker_running ? '暂停' : '恢复' }}
        </el-button>
        <el-button size="small" @click="refreshAll">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>

    <!-- Tab 切换 -->
    <el-tabs v-model="activeTab" @tab-click="onTabChange">
      <el-tab-pane label="运行中" name="running">
        <TaskTable
          :data="tableData"
          :loading="loading"
          :show-actions="true"
          :actions="['detail', 'terminate']"
          @action="handleAction"
        />
      </el-tab-pane>
      <el-tab-pane label="成功" name="success">
        <TaskTable
          :data="tableData"
          :loading="loading"
          :show-actions="true"
          :actions="['detail', 'delete']"
          @action="handleAction"
        />
      </el-tab-pane>
      <el-tab-pane label="失败" name="failure">
        <TaskTable
          :data="tableData"
          :loading="loading"
          :show-actions="true"
          :actions="['detail', 'retry', 'delete']"
          @action="handleAction"
        />
      </el-tab-pane>
      <el-tab-pane label="定时任务" name="schedules">
        <div class="mb-3">
          <el-button type="primary" size="small" @click="handleCreateSchedule">
            创建定时任务
          </el-button>
        </div>
        <ScheduleTable
          :data="scheduleData"
          :loading="loading"
          @action="handleScheduleAction"
        />
      </el-tab-pane>
      <el-tab-pane label="队列" name="queue">
        <QueueStatus :status="queueStatus" />
      </el-tab-pane>
    </el-tabs>

    <!-- 分页 -->
    <div class="flex justify-end mt-4" v-if="activeTab !== 'queue'">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="totalCount"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        @current-change="loadData"
        @size-change="loadData"
      />
    </div>

    <!-- 任务详情对话框 -->
    <el-dialog v-model="detailVisible" title="任务详情" width="600px">
      <el-descriptions :column="1" border v-if="selectedTask">
        <el-descriptions-item label="任务 ID">{{ selectedTask.id }}</el-descriptions-item>
        <el-descriptions-item label="任务名">{{ selectedTask.name }}</el-descriptions-item>
        <el-descriptions-item label="函数">{{ selectedTask.func }}</el-descriptions-item>
        <el-descriptions-item label="参数">{{ selectedTask.args || '-' }}</el-descriptions-item>
        <el-descriptions-item label="关键字参数">{{ selectedTask.kwargs ? JSON.stringify(selectedTask.kwargs) : '-' }}</el-descriptions-item>
        <el-descriptions-item label="开始时间">{{ selectedTask.started || '-' }}</el-descriptions-item>
        <el-descriptions-item label="结束时间">{{ selectedTask.stopped || '-' }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusTagType(selectedTask.success)">
            {{ getStatusText(selectedTask.success) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="结果" v-if="selectedTask.result">
          {{ JSON.stringify(selectedTask.result) }}
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>

    <!-- 创建/编辑定时任务对话框 -->
    <el-dialog v-model="scheduleDialogVisible" :title="scheduleDialogTitle" width="500px">
      <el-form :model="scheduleForm" label-width="120px">
        <el-form-item label="名称" required>
          <el-input v-model="scheduleForm.name" placeholder="任务名称" />
        </el-form-item>
        <el-form-item label="函数" required>
          <el-input v-model="scheduleForm.func" placeholder="myapp.tasks.my_task" />
        </el-form-item>
        <el-form-item label="调度类型" required>
          <el-select v-model="scheduleForm.schedule_type" style="width: 100%">
            <el-option label="一次性" value="ONCE" />
            <el-option label="按分钟" value="MINUTES" />
            <el-option label="每小时" value="HOURLY" />
            <el-option label="每天" value="DAILY" />
            <el-option label="每周" value="WEEKLY" />
            <el-option label="每月" value="MONTHLY" />
            <el-option label="每季度" value="QUARTERLY" />
            <el-option label="每年" value="YEARLY" />
            <el-option label="Cron" value="CRON" />
          </el-select>
        </el-form-item>
        <el-form-item label="分钟间隔" v-if="scheduleForm.schedule_type === 'MINUTES'">
          <el-input-number v-model="scheduleForm.minutes" :min="1" />
        </el-form-item>
        <el-form-item label="Cron 表达式" v-if="scheduleForm.schedule_type === 'CRON'">
          <el-input v-model="scheduleForm.cron" placeholder="0 9 * * *" />
        </el-form-item>
        <el-form-item label="重复次数">
          <el-input-number v-model="scheduleForm.repeats" :min="-1" />
          <span class="text-gray-400 text-sm ml-2">-1 表示无限</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="scheduleDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveSchedule">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { TabsPaneContext } from 'element-plus'
import {
  getTaskListApi,
  getTaskDetailApi,
  deleteTaskApi,
  retryFailureApi,
  getScheduleListApi,
  createScheduleApi,
  updateScheduleApi,
  deleteScheduleApi,
  getQueueStatusApi,
  toggleQueueApi,
} from '@/api/q2'
import type { Q2Task, Q2Schedule, Q2QueueStatus, CreateScheduleParams } from '@/types/q2'

// 组件
import TaskTable from './components/TaskTable.vue'
import ScheduleTable from './components/ScheduleTable.vue'
import QueueStatus from './components/QueueStatus.vue'

// 状态
const activeTab = ref('running')
const loading = ref(false)
const tableData = ref<Q2Task[]>([])
const scheduleData = ref<Q2Schedule[]>([])
const queueStatus = ref<Q2QueueStatus>({
  worker_running: false,
  queue_size: 0,
  tasks_running: 0,
  tasks_failed: 0,
})
const currentPage = ref(1)
const pageSize = ref(20)
const totalCount = ref(0)

// 详情对话框
const detailVisible = ref(false)
const selectedTask = ref<Q2Task | null>(null)

// 定时任务对话框
const scheduleDialogVisible = ref(false)
const scheduleForm = ref<CreateScheduleParams>({
  name: '',
  func: '',
  schedule_type: 'DAILY',
  minutes: null,
  repeats: -1,
  cron: null,
})
const editingScheduleId = ref<number | null>(null)

const scheduleDialogTitle = ref('创建定时任务')

// 方法
function getStatusTagType(success: boolean | null) {
  if (success === null) return 'warning'
  return success ? 'success' : 'danger'
}

function getStatusText(success: boolean | null) {
  if (success === null) return '运行中'
  return success ? '成功' : '失败'
}

async function loadData() {
  loading.value = true
  try {
    if (activeTab.value === 'schedules') {
      const resp = await getScheduleListApi({
        page: currentPage.value,
        page_size: pageSize.value,
      })
      scheduleData.value = resp.data.content?.results || []
      totalCount.value = resp.data.content?.count || 0
    } else if (activeTab.value !== 'queue') {
      const resp = await getTaskListApi({
        status: activeTab.value as 'running' | 'success' | 'failure',
        page: currentPage.value,
        page_size: pageSize.value,
      })
      tableData.value = resp.data.content?.results || []
      totalCount.value = resp.data.content?.count || 0
    }
  } catch {
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

async function loadQueueStatus() {
  try {
    const resp = await getQueueStatusApi()
    queueStatus.value = resp.data.content
  } catch {
    // 静默失败
  }
}

function refreshAll() {
  loadData()
  loadQueueStatus()
}

function onTabChange(_tab: TabsPaneContext) {
  currentPage.value = 1
  loadData()
}

async function handleAction(action: string, row: Q2Task) {
  if (action === 'detail') {
    try {
      const resp = await getTaskDetailApi(row.id)
      selectedTask.value = resp.data.content
      detailVisible.value = true
    } catch {
      ElMessage.error('获取任务详情失败')
    }
  } else if (action === 'delete') {
    try {
      await ElMessageBox.confirm('确定要删除此任务吗？', '确认删除')
      await deleteTaskApi(row.id)
      ElMessage.success('删除成功')
      loadData()
    } catch {
      // 用户取消或请求失败
    }
  } else if (action === 'retry') {
    try {
      await ElMessageBox.confirm('确定要重试此失败任务吗？', '确认重试')
      const resp = await retryFailureApi(row.id)
      ElMessage.success(`重试成功，新任务 ID: ${resp.data.content?.task_id}`)
      loadData()
    } catch {
      // 用户取消或请求失败
    }
  } else if (action === 'terminate') {
    ElMessage.info('终止功能暂未实现')
  }
}

function handleScheduleAction(action: string, row: Q2Schedule) {
  if (action === 'edit') {
    editingScheduleId.value = row.id
    scheduleForm.value = {
      name: row.name,
      func: row.func,
      schedule_type: row.schedule_type,
      minutes: row.minutes,
      repeats: row.repeats,
      cron: row.cron,
    }
    scheduleDialogTitle.value = '编辑定时任务'
    scheduleDialogVisible.value = true
  } else if (action === 'delete') {
    ElMessageBox.confirm('确定要删除此定时任务吗？', '确认删除').then(async () => {
      try {
        await deleteScheduleApi(row.id)
        ElMessage.success('删除成功')
        loadData()
      } catch {
        ElMessage.error('删除失败')
      }
    }).catch(() => {})
  }
}

function handleCreateSchedule() {
  editingScheduleId.value = null
  scheduleForm.value = {
    name: '',
    func: '',
    schedule_type: 'DAILY',
    minutes: null,
    repeats: -1,
    cron: null,
  }
  scheduleDialogTitle.value = '创建定时任务'
  scheduleDialogVisible.value = true
}

async function handleSaveSchedule() {
  if (!scheduleForm.value.name || !scheduleForm.value.func) {
    ElMessage.warning('请填写名称和函数')
    return
  }
  try {
    if (editingScheduleId.value) {
      await updateScheduleApi(editingScheduleId.value, scheduleForm.value)
      ElMessage.success('更新成功')
    } else {
      await createScheduleApi(scheduleForm.value)
      ElMessage.success('创建成功')
    }
    scheduleDialogVisible.value = false
    loadData()
  } catch {
    ElMessage.error('保存失败')
  }
}

async function handleToggleQueue() {
  const action = queueStatus.value.worker_running ? 'pause' : 'resume'
  try {
    await toggleQueueApi(action)
    ElMessage.success(action === 'pause' ? '已暂停队列' : '已恢复队列')
    loadQueueStatus()
  } catch {
    ElMessage.error('操作失败')
  }
}

// 初始化
onMounted(() => {
  loadData()
  loadQueueStatus()
})
</script>
