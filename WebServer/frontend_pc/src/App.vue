<template>
  <div class="container">
    <header>
      <h1>曈灵智能台灯家长端</h1>
      <p class="subtitle">全面了解孩子的坐姿习惯及改善效果</p>
    </header>
    
    <van-tabbar route>
      <van-tabbar-item replace to="/posture" icon="chart-trending-o">坐姿检测</van-tabbar-item>
      <van-tabbar-item replace to="/eye" icon="eye-o">用眼情况</van-tabbar-item>
      <van-tabbar-item replace to="/emotion" icon="smile-o">情绪反馈</van-tabbar-item>
      <van-tabbar-item replace to="/monitor" icon="video-o">家长监护</van-tabbar-item>
      <van-tabbar-item replace to="/control" icon="setting-o">远程控制</van-tabbar-item>
    </van-tabbar>
    
    <router-view></router-view>
  </div>
</template>

<script>
export default {
  name: 'App',
  data() {
    return {
      active: 0,
    }
  }
}
</script>

<style>
:root {
  --primary-color: #4285f4;
  --secondary-color: #34a853;
  --warning-color: #fbbc05;
  --danger-color: #ea4335;
  --light-gray: #f5f5f5;
  --dark-gray: #333;
  --text-color: #444;
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

body {
  background-color: #f9f9f9;
  color: var(--text-color);
  line-height: 1.6;
  padding: 20px;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding-bottom: 60px; /* 为底部导航栏留出空间 */
}

header {
  text-align: center;
  margin-bottom: 30px;
  padding: 20px;
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  color: white;
  border-radius: 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  position: relative;
}

h1 {
  font-size: 2.2rem;
  margin-bottom: 10px;
}

.subtitle {
  font-size: 1.1rem;
  opacity: 0.9;
}

.dashboard {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 25px;
  margin-bottom: 30px;
}

.card {
  background: white;
  border-radius: 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  padding: 20px;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.card-title {
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--dark-gray);
}

.chart-container {
  position: relative;
  height: 250px;
  width: 100%;
}

.alert {
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
}

.alert-warning {
  background-color: rgba(251, 188, 5, 0.2);
  border-left: 4px solid var(--warning-color);
}

.alert-info {
  background-color: rgba(66, 133, 244, 0.2);
  border-left: 4px solid var(--primary-color);
}

.dashboard-title {
  font-size: 28px;
  font-weight: bold;
  margin-top: 20px;
  margin-bottom: 20px;
  text-align: center;
  color: #333;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .dashboard {
    grid-template-columns: 1fr;
  }
  
  h1 {
    font-size: 1.8rem;
  }
}
</style>
