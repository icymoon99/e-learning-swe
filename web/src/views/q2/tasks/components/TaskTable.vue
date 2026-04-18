<template>
  <el-table :data="data" v-loading="loading" stripe border>
    <el-table-column prop="id" label="任务 ID" width="120" show-overflow-tooltip />
    <el-table-column prop="name" label="任务名" min-width="180" show-overflow-tooltip />
    <el-table-column prop="func" label="函数" min-width="200" show-overflow-tooltip />
    <el-table-column label="状态" width="90">
      <template #default="{ row }">
        <el-tag :type="getStatusType(row.success)" size="small">
          {{ getStatusText(row.success) }}
        </el-tag>
      </template>
    </el-table-column>
    <el-table-column prop="started" label="开始时间" width="180" />
    <el-table-column prop="stopped" label="结束时间" width="180" />
    <el-table-column label="耗时" width="100">
      <template #default="{ row }">
        {{ getDuration(row) }}
      </template>
    </el-table-column>
    <el-table-column label="操作" width="160" fixed="right">
      <template #default="{ row }">
        <el-button link type="primary" size="small" @click="$emit('action', 'detail', row)">
          详情
        </el-button>
        <el-button
          v-if="actions.includes('retry')"
          link
          type="warning"
          size="small"
          @click="$emit('action', 'retry', row)"
        >
          重试
        </el-button>
        <el-button
          v-if="actions.includes('terminate')"
          link
          type="danger"
          size="small"
          @click="$emit('action', 'terminate', row)"
        >
          终止
        </el-button>
        <el-button
          v-if="actions.includes('delete')"
          link
          type="danger"
          size="small"
          @click="$emit('action', 'delete', row)"
        >
          删除
        </el-button>
      </template>
    </el-table-column>
  </el-table>
</template>

<script setup lang="ts">
import type { Q2Task } from '@/types/q2'

defineProps<{
  data: Q2Task[]
  loading: boolean
  actions: string[]
}>()

defineEmits<{
  action: [action: string, row: Q2Task]
}>()

function getStatusType(success: boolean | null) {
  if (success === null) return 'warning'
  return success ? 'success' : 'danger'
}

function getStatusText(success: boolean | null) {
  if (success === null) return '运行中'
  return success ? '成功' : '失败'
}

function getDuration(row: Q2Task) {
  if (!row.started || !row.stopped) return '-'
  const start = new Date(row.started).getTime()
  const stop = new Date(row.stopped).getTime()
  const diff = (stop - start) / 1000
  if (diff < 60) return `${diff.toFixed(1)}s`
  return `${Math.floor(diff / 60)}m ${Math.floor(diff % 60)}s`
}
</script>
