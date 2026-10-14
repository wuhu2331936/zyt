import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', redirect: '/home' },
  {
    path: '/home',
    name: 'Home',
    component: () => import('@/views/HomeView.vue'),
  },
  {
    path: '/scan',
    name: 'Scan',
    component: () => import('@/views/ScanView.vue'),
  },
  {
    path: '/detail',
    name: 'Detail',
    component: () => import('@/views/DetailView.vue'),
  },
  {
    path: '/reminder',
    name: 'Reminder',
    component: () => import('@/views/ReminderView.vue'),
  },
  {
    path: '/voice',
    name: 'Voice',
    component: () => import('@/views/VoiceQAView.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router