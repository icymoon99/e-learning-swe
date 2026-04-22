<template>
  <div class="task-detail p-4" v-loading="detailLoading">
    <!-- 返回 + 标题 -->
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center gap-3">
        <el-button link @click="$router.back()">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <h2 class="text-xl font-semibold">{{ taskDetail?.title }}</h2>
        <el-tag :type="taskDetail?.status === 'open' ? 'success' : 'info'" size="small">
          {{ taskDetail?.status_display }}
        </el-tag>
      </div>
      <div class="flex items-center gap-2">
        <el-button type="warning" size="small" @click="handleCloseTask" v-if="taskDetail?.status === 'open'">关闭任务</el-button>
      </div>
    </div>

    <!-- 任务信息卡片 -->
    <el-descriptions :column="3" border class="mb-4" size="small">
      <el-descriptions-item label="仓库源">
        {{ taskDetail?.git_source?.name || '-' }}
      </el-descriptions-item>
      <el-descriptions-item label="平台">
        {{ taskDetail?.git_source?.platform_display || '-' }}
      </el-descriptions-item>
      <el-descriptions-item label="源分支">
        {{ taskDetail?.source_branch }}
      </el-descriptions-item>
      <el-descriptions-item label="最新执行状态" :span="3">
        <el-tag v-if="taskDetail?.latest_execution_status" :type="getExecType(taskDetail.latest_execution_status)" size="small">
          {{ taskDetail.latest_execution_status }}
        </el-tag>
        <span v-else class="text-gray-400">暂无执行记录</span>
      </el-descriptions-item>
      <el-descriptions-item label="描述" :span="3">
        {{ taskDetail?.description || '-' }}
      </el-descriptions-item>
    </el-descriptions>

    <!-- 对话区域 -->
    <div class="chat-container border rounded-lg flex flex-col" style="height: 500px;">
      <!-- 消息列表 -->
      <div class="flex-1 overflow-y-auto p-4" ref="chatContainer">
        <div v-if="conversations.length === 0" class="text-center text-gray-400 py-8">
          暂无对话记录，输入第一条指令开始
        </div>
        <div v-for="msg in conversations" :key="msg.id" class="mb-3">
          <!-- 用户指令 -->
          <div v-if="msg.comment_type === 'user'" class="flex justify-end">
            <div class="bg-blue-500 text-white rounded-lg px-3 py-2 max-w-[70%]">
              <div class="text-xs opacity-75 mb-1">{{ msg.agent_name || msg.agent_code }}</div>
              <div>{{ msg.content }}</div>
              <div class="text-xs opacity-75 mt-1">{{ msg.created_at }}</div>
            </div>
          </div>
          <!-- AI 回复 -->
          <div v-else-if="msg.comment_type === 'ai'" class="flex justify-start">
            <div class="bg-gray-100 rounded-lg px-3 py-2 max-w-[70%]">
              <div class="text-xs text-gray-500 mb-1">{{ msg.agent_name || 'AI' }}</div>
              <div class="whitespace-pre-wrap">{{ msg.content }}</div>
              <div class="text-xs text-gray-400 mt-1">{{ msg.created_at }}</div>
            </div>
          </div>
          <!-- 系统通知 -->
          <div v-else class="flex justify-center">
            <div class="text-xs text-gray-400 bg-gray-50 rounded px-3 py-1">
              {{ msg.content }}
            </div>
          </div>
        </div>
      </div>

      <!-- 输入区域 -->
      <div class="border-t p-3 flex items-center gap-2">
        <el-select v-model="selectedAgent" placeholder="选择 Agent" style="width: 140px" :disabled="taskDetail?.status === 'closed'">
          <el-option v-for="agent in agentOptions" :key="agent.code" :label="agent.name" :value="agent.code" />
        </el-select>
        <el-input
          v-model="inputContent"
          placeholder="输入指令..."
          clearable
          @keyup.enter="handleSend"
          :disabled="taskDetail?.status === 'closed' || sending"
        />
        <el-button type="primary" @click="handleSend" :loading="sending" :disabled="taskDetail?.status === 'closed' || !inputContent || !selectedAgent">
          发送
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { ArrowLeft } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getTaskDetailApi,
  closeTaskApi,
  getConversationListApi,
  sendCommandApi,
} from '@/api/task'
import { getAgentListApi } from '@/api/agent'
import type { TaskDetail, ConversationItem } from '@/types/task'

const route = useRoute()
const taskId = route.params.id as string

// 任务详情
const taskDetail = ref<TaskDetail | null>(null)
const detailLoading = ref(false)

// 对话
const conversations = ref<ConversationItem[]>([])
const sending = ref(false)
const inputContent = ref('')
const selectedAgent = ref('')
const agentOptions = ref<Array<{ code: string; name: string }>>([])
const chatContainer = ref<HTMLElement | null>(null)

// 加载任务详情
async function loadDetail() {
  detailLoading.value = true
  try {
    const resp = await getTaskDetailApi(taskId)
    taskDetail.value = resp.data.content
  } catch {
    ElMessage.error('加载任务详情失败')
  } finally {
    detailLoading.value = false
  }
}

// 加载对话列表
async function loadConversations() {
  try {
    const resp = await getConversationListApi(taskId, { page: 1, page_size: 100 })
    conversations.value = resp.data.content?.results || []
    await nextTick()
    scrollToBottom()
  } catch {
    // 忽略
  }
}

// 加载 Agent 列表
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

function getExecType(status: string): string {
  const map: Record<string, string> = { completed: 'success', running: 'warning', failed: 'danger' }
  return map[status] || 'info'
}

// 发送指令
async function handleSend() {
  if (!inputContent.value || !selectedAgent.value) return
  sending.value = true
  try {
    await sendCommandApi(taskId, {
      content: inputContent.value,
      agent_code: selectedAgent.value,
    })
    inputContent.value = ''
    await loadConversations()
  } catch {
    ElMessage.error('发送指令失败')
  } finally {
    sending.value = false
  }
}

// 关闭任务
async function handleCloseTask() {
  try {
    await ElMessageBox.confirm('确定要关闭此任务吗？', '确认关闭')
    await closeTaskApi(taskId)
    ElMessage.success('任务已关闭')
    await loadDetail()
  } catch {
    // 用户取消
  }
}

onMounted(async () => {
  await Promise.all([loadDetail(), loadConversations(), loadAgents()])
})
</script>
