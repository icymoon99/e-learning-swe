<template>
  <el-table :data="data" v-loading="loading" stripe border>
    <el-table-column prop="id" label="ID" width="60" />
    <el-table-column prop="name" label="名称" min-width="150" show-overflow-tooltip />
    <el-table-column prop="func" label="函数" min-width="200" show-overflow-tooltip />
    <el-table-column prop="schedule_type" label="调度类型" width="120" />
    <el-table-column prop="minutes" label="分钟间隔" width="100">
      <template #default="{ row }">{{ row.minutes ?? '-' }}</template>
    </el-table-column>
    <el-table-column prop="repeats" label="重复次数" width="100">
      <template #default="{ row }">{{ row.repeats === -1 ? '无限' : row.repeats }}</template>
    </el-table-column>
    <el-table-column prop="next_run" label="下次执行" width="180" />
    <el-table-column label="操作" width="120" fixed="right">
      <template #default="{ row }">
        <el-button link type="primary" size="small" @click="$emit('action', 'edit', row)">
          编辑
        </el-button>
        <el-button link type="danger" size="small" @click="$emit('action', 'delete', row)">
          删除
        </el-button>
      </template>
    </el-table-column>
  </el-table>
</template>

<script setup lang="ts">
import type { Q2Schedule } from '@/types/q2'

defineProps<{
  data: Q2Schedule[]
  loading: boolean
}>()

defineEmits<{
  action: [action: string, row: Q2Schedule]
}>()
</script>
