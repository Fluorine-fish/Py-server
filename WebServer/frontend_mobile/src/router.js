 import { createRouter, createWebHistory } from 'vue-router'

// 导入页面组件
import Home from './pages/Home.vue'
import Guardian from './pages/Guardian.vue'
import Remote from './pages/Remote.vue'
import Settings from './pages/Settings.vue'
import Posture from './pages/Posture.vue'
import Eye from './pages/Eye.vue'
import Emotion from './pages/Emotion.vue'
import SettingsAccount from './pages/SettingsAccount.vue'
import SettingsMonitor from './pages/SettingsMonitor.vue'
import SettingsNotifications from './pages/SettingsNotifications.vue'
import SettingsSystem from './pages/SettingsSystem.vue'
import ReminderInterval from './pages/ReminderInterval.vue'
import NotFound from './pages/NotFound.vue'

const routes = [
  {
    path: '/',
    redirect: '/home'
  },
  {
    path: '/home',
    name: 'home',
    component: Home,
    meta: { title: '首页 - 曈灵智能台灯' }
  },
  {
    path: '/guardian',
    name: 'guardian',
    component: Guardian,
    meta: { title: '家长监护 - 曈灵智能台灯' }
  },
  {
    path: '/remote',
    name: 'remote',
    component: Remote,
    meta: { title: '远程控制 - 曈灵智能台灯' }
  },
  {
    path: '/settings',
    name: 'settings',
    component: Settings,
    meta: { title: '设置 - 曈灵智能台灯' }
  },
  {
    path: '/posture',
    name: 'posture',
    component: Posture,
    meta: { title: '坐姿检测 - 曈灵智能台灯' }
  },
  {
    path: '/eye',
    name: 'eye',
    component: Eye,
    meta: { title: '用眼监护 - 曈灵智能台灯' }
  },
  {
    path: '/emotion',
    name: 'emotion',
    component: Emotion,
    meta: { title: '情绪监测 - 曈灵智能台灯' }
  },
  {
    path: '/settings/account',
    name: 'settingsAccount',
    component: SettingsAccount,
    meta: { title: '账号设置 - 曈灵智能台灯' }
  },
  {
    path: '/settings/monitor',
    name: 'settingsMonitor',
    component: SettingsMonitor,
    meta: { title: '监护设置 - 曈灵智能台灯' }
  },
  {
    path: '/settings/notifications',
    name: 'settingsNotifications',
    component: SettingsNotifications,
    meta: { title: '通知设置 - 曈灵智能台灯' }
  },
  {
    path: '/settings/system',
    name: 'settingsSystem',
    component: SettingsSystem,
    meta: { title: '系统设置 - 曈灵智能台灯' }
  },
  {
    path: '/settings/reminder-interval',
    name: 'reminderInterval',
    component: ReminderInterval,
    meta: { title: '设置提醒间隔 - 曈灵智能台灯' }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'notFound',
    component: NotFound,
    meta: { title: '页面未找到 - 曈灵智能台灯' }
  }
]

const router = createRouter({
  history: createWebHistory('/mobile/'), // 使用History模式，基础路径为/mobile/
  routes
})

// 全局前置守卫，设置页面标题
router.beforeEach((to, from, next) => {
  if (to.meta.title) {
    document.title = to.meta.title
  }
  next()
})

export default router
