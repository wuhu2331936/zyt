<template>
  <div class="app-root">
    <!-- 演示模式提示：未配置 API Key 时展示，保证评审老师知情 -->
    <div v-if="demoMode && !bannerClosed" class="demo-banner">
      <span class="demo-badge">演示</span>
      <span class="demo-text">未配置 API Key，识药 / 问答返回预置示例数据</span>
      <span class="demo-close" @click="bannerClosed = true">×</span>
    </div>

    <router-view v-slot="{ Component }">
      <transition name="fade" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>

    <!-- 底部 TabBar（只在主要页面显示） -->
    <van-tabbar v-if="showTabbar" v-model="activeTab" route safe-area-inset-bottom>
      <van-tabbar-item to="/home" icon="medal-o">首页</van-tabbar-item>
      <van-tabbar-item to="/scan" icon="photograph">识药</van-tabbar-item>
      <van-tabbar-item to="/voice" icon="volume-o">问答</van-tabbar-item>
      <van-tabbar-item to="/reminder" icon="clock-o">提醒</van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useReminderStore } from '@/stores/reminder'
import { requestNotifyPermission, startReminderWatcher } from '@/utils/reminderWatcher'

const route = useRoute()
const activeTab = ref(0)
const reminderStore = useReminderStore()

// 演示模式标记（后端未配置 API Key 时为 true）
const demoMode = ref(false)
const bannerClosed = ref(false)

onMounted(async () => {
  try {
    const res = await fetch('/api/health')
    const data = await res.json()
    demoMode.value = !!data.demo_mode
  } catch {
    demoMode.value = false
  }

  // 到点服药提醒：页面内提示 + 系统通知 + 语音播报（全局，任何页面都生效）
  try {
    requestNotifyPermission()
    startReminderWatcher(reminderStore)
  } catch (e) {
    console.warn('[reminder] 提醒监听启动失败', e)
  }
})

// 哪些路由显示 TabBar
const TABBAR_ROUTES = ['/home', '/scan', '/voice', '/reminder']
const showTabbar = computed(() => TABBAR_ROUTES.includes(route.path))

// 同步 TabBar 高亮
watch(
  () => route.path,
  (p) => {
    const map = { '/home': 0, '/scan': 1, '/voice': 2, '/reminder': 3 }
    activeTab.value = map[p] ?? 0
  },
  { immediate: true }
)
</script>

<style scoped>
.app-root {
  min-height: 100vh;
  padding-bottom: env(safe-area-inset-bottom);
}
.demo-banner {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 7px 12px;
  background: linear-gradient(90deg, #fff4e0 0%, #ffe9c7 100%);
  border-bottom: 1px solid #ffd9a0;
  font-size: 12px;
  color: #8a5a12;
  line-height: 1.4;
}
.demo-badge {
  flex: none;
  padding: 1px 7px;
  border-radius: 999px;
  background: #ff9f1c;
  color: #fff;
  font-weight: 700;
  font-size: 11px;
}
.demo-text {
  flex: 1;
  min-width: 0;
}
.demo-close {
  flex: none;
  width: 20px;
  text-align: center;
  font-size: 18px;
  color: #b07b2a;
  cursor: pointer;
}
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>