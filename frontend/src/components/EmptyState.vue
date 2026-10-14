<template>
  <div class="empty-state">
    <van-empty :description="text">
      <template #image>
        <div style="font-size: 64px;">💊</div>
      </template>
    </van-empty>
  </div>
</template>

<script setup>
defineProps({
  text: { type: String, default: '暂无内容' },
})
</script>

<style scoped>
.empty-state {
  padding: 40px 0;
}
</style>