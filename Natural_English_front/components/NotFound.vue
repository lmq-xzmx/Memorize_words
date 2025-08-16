<template>
  <div class="not-found-container">
    <div class="not-found-content">
      <div class="error-icon">🔍</div>
      <h1 class="error-title">页面未找到</h1>
      <p class="error-message">抱歉，您访问的页面不存在或已被移除。</p>
      <div class="error-actions">
        <button @click="goBack" class="btn btn-secondary">
          <span class="icon">←</span>
          返回上页
        </button>
        <button @click="goHome" class="btn btn-primary">
          <span class="icon">🏠</span>
          回到首页
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'NotFound',
  methods: {
    goBack() {
      if (window.history.length > 1) {
        this.$router.go(-1)
      } else {
        this.goHome()
      }
    },
    goHome() {
      this.$router.push('/')
    }
  }
}
</script>

