<template>
  <div class="not-found">
    <i class="bi bi-exclamation-circle"></i>
    <h1>404</h1>
    <p>页面未找到</p>
    <router-link to="/" class="back-button">返回首页</router-link>
  </div>
</template>

<script setup>
// 404页面逻辑
</script>

<style scoped>
.not-found {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px;
  text-align: center;
}

.not-found i {
  font-size: 60px;
  color: var(--color-danger);
  margin-bottom: 20px;
}

.not-found h1 {
  font-size: 48px;
  margin-bottom: 12px;
}

.not-found p {
  font-size: 18px;
  color: var(--color-text-secondary);
  margin-bottom: 30px;
}

.back-button {
  display: inline-block;
  padding: 12px 24px;
  background-color: var(--color-primary);
  color: white;
  border-radius: var(--radius);
  text-decoration: none;
  font-weight: 500;
  transition: background-color 0.3s;
}

.back-button:hover {
  background-color: #2563eb;
}
</style>
