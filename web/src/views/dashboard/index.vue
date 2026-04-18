<template>
  <div class="dashboard-container">
    <h2 class="page-title">仪表盘</h2>
    <el-row :gutter="20" class="mt-6">
      <el-col :span="8">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon :size="24" color="#409eff"><User /></el-icon>
              <span class="ml-2">用户数</span>
            </div>
          </template>
          <div class="card-value">--</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon :size="24" color="#67c23a"><Document /></el-icon>
              <span class="ml-2">任务数</span>
            </div>
          </template>
          <div class="card-value">--</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon :size="24" color="#e6a23c"><Folder /></el-icon>
              <span class="ml-2">仓库数</span>
            </div>
          </template>
          <div class="card-value">--</div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { User, Document, Folder } from '@element-plus/icons-vue'
</script>

<style scoped lang="scss">
.dashboard-container {
  padding: 20px;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  color: #333;
}

.card-header {
  display: flex;
  align-items: center;
  font-size: 14px;
  color: #666;
}

.card-value {
  font-size: 32px;
  font-weight: 700;
  color: #333;
  text-align: center;
  padding: 16px 0;
}
</style>
