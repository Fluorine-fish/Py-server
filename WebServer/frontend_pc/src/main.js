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

const router = createRouter({ history: createWebHashHistory(), routes })

const app = createApp(App)
app.use(router)
app.use(Tabbar).use(TabbarItem).use(NavBar).use(Button).use(Slider).use(Field).use(Switch)
app.mount('#app')