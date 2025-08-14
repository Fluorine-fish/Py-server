<template>
  <div class="app-wrapper">
    <div class="mobile-container">
      <main class="mobile-main">
        <!-- 添加过渡动画效果 -->
        <router-view v-slot="{ Component }">
          <transition name="router-view" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
    
    <!-- 底部导航栏 - 放在外层以避免定位问题 -->
    <nav class="mobile-nav">
      <router-link to="/home" class="nav-item" :class="{ active: $route.path === '/home' }">
        <i class="bi bi-house nav-icon"></i>
        <span>首页</span>
      </router-link>
      <router-link to="/guardian" class="nav-item" :class="{ active: $route.path === '/guardian' }">
        <i class="bi bi-shield-check nav-icon"></i>
        <span>家长监护</span>
      </router-link>
      <router-link to="/remote" class="nav-item" :class="{ active: $route.path === '/remote' }">
        <i class="bi bi-toggles nav-icon"></i>
        <span>远程控制</span>
      </router-link>
      <router-link to="/settings" class="nav-item" :class="{ active: $route.path.includes('/settings') }">
        <i class="bi bi-gear nav-icon"></i>
        <span>设置</span>
      </router-link>
    </nav>
  </div>
</template>

<style>
/* 确保整个应用都应用了正确的背景色 */
.app-wrapper {
  min-height: 100vh;
  background: #E8E3DC;
  position: relative;
}

/* 确保设置页面的内容正确显示 */
.settings-item .settings-icon i {
  color: var(--color-primary-dark) !important;
}

.settings-item {
  transition: all 0.2s ease;
}

.settings-item:active {
  background-color: rgba(143, 180, 160, 0.1);
}

/* 修复导航栏在不同设备上的显示 */
@media (max-width: 375px) {
  .nav-item span {
    font-size: 11px;
  }
}
</style>

<script setup>
import { onMounted, onBeforeUnmount } from 'vue';
import { useMonitorStore } from './stores';
import { realtimeWS } from './api';

const monitorStore = useMonitorStore();

// 连接WebSocket，并监听实时数据
onMounted(() => {
  realtimeWS.connect();
  
  // 监听实时数据并更新到store
  const removeListener = realtimeWS.addListener((data) => {
    monitorStore.updateFromWebSocket(data);
  });
  
  // 组件卸载时移除监听
  onBeforeUnmount(() => {
    removeListener();
  });
});
</script>