<template>
  <div class="zyt-empty-state">
    <div class="empty-illustration">
      <span class="emoji">{{ emoji }}</span>
    </div>
    <p class="empty-text">{{ text }}</p>
    <p class="empty-hint" v-if="hint">{{ hint }}</p>
  </div>
</template>

<script setup>
defineProps({
  text: { type: String, default: '暂无内容' },
  hint: { type: String, default: '' },
  emoji: { type: String, default: '💊' },
})
</script>

<style scoped>
.zyt-empty-state {
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 6px 20px rgba(31, 45, 61, 0.07);
  padding: 34px 20px;
  text-align: center;
  margin-bottom: 12px;
}
.empty-illustration {
  width: 96px;
  height: 96px;
  margin: 0 auto 14px;
  border-radius: 28px;
  background: linear-gradient(135deg, #eef4ff 0%, #e3f7f2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}
.emoji {
  font-size: 44px;
}
.empty-text {
  margin: 0;
  font-size: 16px;
  color: #6b7787;
}
.empty-hint {
  margin: 6px 0 0;
  font-size: 14px;
  color: #a7b0bd;
}
</style>
