import { createApp } from 'vue'
import App from './App.vue'
import { createRouter, createWebHashHistory } from 'vue-router'
import Posture from './pages/Posture.vue'
import Eye from './pages/Eye.vue'
import Emotion from './pages/Emotion.vue'
import Monitor from './pages/Monitor.vue'
import Control from './pages/Control.vue'

import 'vant/lib/index.css'
import { Tabbar, TabbarItem, NavBar, Button, Slider, Field, Switch } from 'vant'

const routes = [
  { path: '/', redirect: '/posture' },
  { path: '/posture', component: Posture },
  { path: '/eye', component: Eye },
  { path: '/emotion', component: Emotion },
  { path: '/monitor', component: Monitor },
  { path: '/control', component: Control }
]

const router = createRouter({ 
  history: createWebHashHistory(), 
  routes 
})

// 添加路由导航守卫，确保页面切换时图表能正确初始化
router.afterEach((to, from) => {
  // 页面切换完成后，延迟执行图表初始化逻辑
  setTimeout(() => {
    // 触发窗口调整事件，帮助图表库重新计算尺寸
    window.dispatchEvent(new Event('resize'));
    
    // 根据页面类型执行特定的图表初始化
    if (to.path === '/posture' || to.path === '/eye') {
      // 再次触发可见性变化事件，强制图表重新渲染
      setTimeout(() => {
        document.dispatchEvent(new Event('visibilitychange'));
      }, 200);
    }
  }, 100);
});

const app = createApp(App)

// 添加全局混入，用于处理图表页面的初始化
app.mixin({
  activated() {
    // 在 keep-alive 组件激活时重新初始化图表
    if (this.forceReinitializeCharts && typeof this.forceReinitializeCharts === 'function') {
      this.$nextTick(() => {
        setTimeout(() => {
          this.forceReinitializeCharts();
        }, 100);
      });
    }
  },
  mounted() {
    // 页面挂载时，延迟触发图表刷新
    if (this.refreshChartsNTimes && typeof this.refreshChartsNTimes === 'function') {
      this.$nextTick(() => {
        setTimeout(() => {
          this.refreshChartsNTimes(2, 200);
        }, 300);
      });
    }
  }
});

app.use(router)
app.use(Tabbar).use(TabbarItem).use(NavBar).use(Button).use(Slider).use(Field).use(Switch)
app.mount('#app')