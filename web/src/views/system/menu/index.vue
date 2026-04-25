<template>
  <div class="placeholder-page">
    <h2>菜单管理</h2>
    <p class="placeholder-text">功能开发中...</p>
  </div>
</template>

<style scoped lang="scss">
.placeholder-page {
  position: relative;
  z-index: 1;
  padding: 40px 20px;
}

h2 {
  font-size: 24px;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--text-primary);
  margin-bottom: 12px;
  animation: fadeUp 0.5s cubic-bezier(0.16, 1, 0.3, 1) both;
}

.placeholder-text {
  color: var(--text-tertiary);
  font-size: 14px;
  animation: fadeUp 0.5s cubic-bezier(0.16, 1, 0.3, 1) 0.1s both;
}
</style>
