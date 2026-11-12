<template>
  <div class="app-root">
    <!-- 演示模式提示：未配置 API Key 时展示，保证评审老师知情 -->
    <div v-if="demoMode && !bannerClosed" class="demo-banner">
      <span class="demo-badge">演示</span>
      <span class="demo-text">未配置 API Key，识药 / 问答返回预置示例数据</span>
      <span class="demo-close" @click="bannerClosed = true">×</span>
    </div>

    <!-- 有 TabBar 的页面必须留出底部空间，否则页面底部的按钮被固定栏压住点不到 -->
    <div class="page-wrap" :class="{ 'has-tabbar': showTabbar }">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </div>

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
import request from '@/api/request'

const route = useRoute()
const activeTab = ref(0)
const reminderStore = useReminderStore()

// 演示模式标记（后端未配置 API Key 时为 true）
const demoMode = ref(false)
const bannerClosed = ref(false)

onMounted(async () => {
  // 启动即预热 + 探测演示模式：
  // 1) APK 里页面源是 https://localhost，绝不能用相对路径 /api/health（会打到壳内部）；
  // 2) 云托管 min instance=0，空闲后缩容——开机先打一次 health 把实例唤醒，
  //    用户真正用识药/问答时就不会吃冷启动 503（axios 层还有 5xx 自动重试兜底）。
  try {
    const data = await request.get('/health', { silent: true })
    demoMode.value = !!data?.demo_mode
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
/* TabBar 是 fixed 定位，页面底部内容需要让位，否则按钮被压住无法点击 */
.page-wrap.has-tabbar {
  padding-bottom: 70px;
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