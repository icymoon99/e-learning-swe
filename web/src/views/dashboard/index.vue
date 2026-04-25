<template>
  <div class="dashboard">
    <!-- Welcome Section -->
    <div class="welcome-section">
      <h2>欢迎回来</h2>
      <p>以下是平台运行概览</p>
    </div>

    <!-- Stat Cards -->
    <div class="stat-grid">
      <div class="stat-card" v-for="stat in stats" :key="stat.label">
        <div class="stat-header">
          <span class="stat-label">{{ stat.label }}</span>
          <div class="stat-icon" :class="stat.iconClass">
            <el-icon :size="20"><component :is="stat.icon" /></el-icon>
          </div>
        </div>
        <div class="stat-value">{{ stat.value }}</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { User, Document, Folder } from '@element-plus/icons-vue'

// TODO: 接入真实 API 获取数据
const userCount = ref(0)
const taskCount = ref(0)
const gitSourceCount = ref(0)

const stats = computed(() => [
  {
    label: '用户数',
    value: userCount.value || '--',
    icon: User,
    iconClass: 'blue',
  },
  {
    label: '任务数',
    value: taskCount.value || '--',
    icon: Document,
    iconClass: 'green',
  },
  {
    label: '仓库数',
    value: gitSourceCount.value || '--',
    icon: Folder,
    iconClass: 'amber',
  },
])
</script>

<style scoped lang="scss">
.dashboard {
  position: relative;
  z-index: 1;
}

.welcome-section {
  margin-bottom: 28px;
  animation: fadeUp 0.5s cubic-bezier(0.16, 1, 0.3, 1) both;

  h2 {
    font-size: 26px;
    font-weight: 800;
    color: var(--text-primary);
    letter-spacing: -0.03em;
    margin-bottom: 6px;
  }

  p {
    font-size: 14px;
    color: var(--text-secondary);
    font-weight: 500;
  }
}

.stat-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  max-width: 800px;
}

.stat-card {
  background: var(--surface-glass);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid var(--border-glass);
  border-radius: 16px;
  padding: 24px;
  position: relative;
  overflow: hidden;
  transition: all 220ms cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow:
    0 2px 8px rgba(0, 0, 0, 0.03),
    inset 0 1px 0 rgba(255, 255, 255, 0.6);
  animation: fadeUp 0.5s cubic-bezier(0.16, 1, 0.3, 1) both;

  &:nth-child(1) { animation-delay: 0.05s; }
  &:nth-child(2) { animation-delay: 0.1s; }
  &:nth-child(3) { animation-delay: 0.15s; }

  &:hover {
    transform: translateY(-2px);
    box-shadow:
      0 8px 24px rgba(0, 0, 0, 0.06),
      inset 0 1px 0 rgba(255, 255, 255, 0.7);
    border-color: rgba(255, 255, 255, 0.8);
  }

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 15%;
    right: 15%;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.8), transparent);
  }
}

.stat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.stat-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
}

.stat-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;

  &.blue { background: linear-gradient(135deg, #3b82f6, #6366f1); }
  &.green { background: linear-gradient(135deg, #10b981, #059669); }
  &.amber { background: linear-gradient(135deg, #f59e0b, #d97706); }
}

.stat-value {
  font-family: 'JetBrains Mono', monospace;
  font-size: 36px;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.03em;
  line-height: 1;
}
</style>
