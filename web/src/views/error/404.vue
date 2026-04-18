<template>
  <div class="error-container">
    <div class="error-content">
      <h1 class="error-code">404</h1>
      <p class="error-msg">页面不存在，请检查网址</p>
      <el-button type="primary" @click="$router.push('/')">返回首页</el-button>
    </div>
  </div>
</template>

<style scoped lang="scss">
.error-container {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f0f2f5;
}

.error-content {
  text-align: center;

  .error-code {
    font-size: 120px;
    font-weight: 700;
    color: #409eff;
    margin-bottom: 16px;
  }

  .error-msg {
    font-size: 18px;
    color: #999;
    margin-bottom: 32px;
  }
}
</style>
