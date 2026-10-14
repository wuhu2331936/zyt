<template>
  <div class="app-root">
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
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const activeTab = ref(0)

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
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>