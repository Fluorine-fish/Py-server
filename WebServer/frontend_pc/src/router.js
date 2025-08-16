import { createRouter, createWebHistory } from 'vue-router';
import Posture from './pages/Posture.vue';
import PostureGallery from './pages/PostureGallery.vue';
import Eye from './pages/Eye.vue';
import Emotion from './pages/Emotion.vue';
import Monitor from './pages/Monitor.vue';
import Control from './pages/Control.vue';
import Voice from './pages/Voice.vue';
import Debug from './pages/Debug.vue';

const routes = [
  { 
    path: '/', 
    redirect: '/posture' 
  },
  {
    path: '/posture',
    component: Posture,
    name: 'posture'
  },
  {
    path: '/posture/gallery',
    component: PostureGallery,
    name: 'posture-gallery'
  },
  {
    path: '/eye',
    component: Eye,
    name: 'eye'
  },
  {
    path: '/emotion',
    component: Emotion,
    name: 'emotion'
  },
  {
    path: '/monitor',
    component: Monitor,
    name: 'monitor'
  },
  {
    path: '/control',
    component: Control,
    name: 'control'
  },
  {
    path: '/voice',
    component: Voice,
    name: 'voice'
  },
  {
    path: '/debug',
    component: Debug,
    name: 'debug'
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

// 添加路由导航守卫，确保页面切换时图表能正确初始化
router.beforeEach((to, from, next) => {
  // 在每次路由切换前，延迟触发图表重新初始化
  next();
});

router.afterEach((to, from) => {
  // 页面切换完成后，延迟执行图表初始化逻辑
  setTimeout(() => {
    // 触发窗口调整事件，帮助图表库重新计算尺寸
    window.dispatchEvent(new Event('resize'));
    
    // 根据页面类型执行特定的图表初始化
    if (to.name === 'posture' || to.name === 'eye') {
      // 再次触发可见性变化事件，强制图表重新渲染
      setTimeout(() => {
        document.dispatchEvent(new Event('visibilitychange'));
      }, 200);
    }
  }, 100);
});

export default router;
