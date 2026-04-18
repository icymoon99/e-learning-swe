<template>
  <div class="queue-status p-4">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>Worker 状态</template>
          <el-tag :type="status.worker_running ? 'success' : 'danger'" size="large">
            {{ status.worker_running ? '运行中' : '已停止' }}
          </el-tag>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>队列大小</template>
          <el-statistic :value="status.queue_size" />
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>正在执行</template>
          <el-statistic :value="status.tasks_running" />
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>失败任务</template>
          <el-statistic :value="status.tasks_failed">
            <template #suffix>
              <el-tag v-if="status.tasks_failed > 0" type="danger" size="small">!</el-tag>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
    </el-row>
    <el-empty v-if="!status.worker_running" description="Worker 未运行，无法执行任务" />
  </div>
</template>

<script setup lang="ts">
import type { Q2QueueStatus } from '@/types/q2'

defineProps<{
  status: Q2QueueStatus
}>()
</script>
