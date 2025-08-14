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

export default router;
