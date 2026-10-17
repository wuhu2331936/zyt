<template>
  <div class="med-card" @click="$emit('click', medicine)">
    <div class="med-icon" :class="iconClass">
      {{ iconEmoji }}
    </div>

    <div class="med-body">
      <div class="med-title-row">
        <h3 class="med-name">{{ medicine.name }}</h3>
        <span class="med-delete" @click.stop="$emit('remove', medicine)">删除</span>
      </div>
      <p class="med-desc">{{ desc }}</p>
      <div class="med-tags">
        <van-tag :type="tagType" plain round>{{ tagText }}</van-tag>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  medicine: { type: Object, required: true },
})
defineEmits(['click', 'remove'])

const desc = computed(() => {
  const parts = []
  if (props.medicine.spec) parts.push(props.medicine.spec)
  if (props.medicine.usage) parts.push(props.medicine.usage)
  return parts.join(' · ') || '点击查看详情'
})

// source: vl=真实识别 / manual=手动 / search=搜索 / demo=演示兜底（必须如实标注，不能冒充真实识别）
const iconClass = computed(() => {
  const s = props.medicine.source
  if (s === 'vl' || s === 'search') return 'vl'
  if (s === 'demo') return 'demo'
  return 'manual'
})

const iconEmoji = computed(() => {
  const s = props.medicine.source
  if (s === 'demo') return '🎭'
  if (s === 'vl' || s === 'search') return '📷'
  return '✍️'
})

const tagText = computed(() => {
  const map = { vl: '拍照识别', manual: '手动添加', search: '搜索', demo: '示例数据' }
  return map[props.medicine.source] || '手动添加'
})

const tagType = computed(() => {
  const s = props.medicine.source
  if (s === 'demo') return 'warning'
  return s === 'vl' || s === 'search' ? 'primary' : 'success'
})
</script>

<style scoped>
.med-card {
  display: flex;
  gap: 12px;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 6px 20px rgba(31, 45, 61, 0.07);
  padding: 14px;
  margin-bottom: 12px;
  cursor: pointer;
  transition: transform 0.15s ease;
}
.med-card:active {
  transform: scale(0.985);
}
.med-icon {
  flex: none;
  width: 52px;
  height: 52px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}
.med-icon.vl {
  background: linear-gradient(135deg, #e3f0ff 0%, #d3e8ff 100%);
}
.med-icon.manual {
  background: linear-gradient(135deg, #e0f8f1 0%, #d2f3ea 100%);
}
.med-icon.demo {
  background: linear-gradient(135deg, #fff4e0 0%, #ffe9c2 100%);
}
.med-body {
  flex: 1;
  min-width: 0;
}
.med-title-row {
  display: flex;
  align-items: flex-start;
  gap: 8px;
}
.med-name {
  flex: 1;
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: #1f2733;
  line-height: 1.35;
}
.med-delete {
  flex: none;
  font-size: 14px;
  color: #f5483b;
  padding: 2px 8px;
  border-radius: 10px;
  background: #ffeeec;
}
.med-desc {
  margin: 6px 0 8px;
  font-size: 14px;
  color: #6b7787;
  line-height: 1.5;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.med-tags {
  display: flex;
  gap: 6px;
}
</style>
