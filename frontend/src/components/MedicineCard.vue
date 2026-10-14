<template>
  <van-card
    class="medicine-card"
    :title="medicine.name"
    :desc="desc"
    :thumb="thumbUrl"
    @click="$emit('click', medicine)"
  >
    <template #tags>
      <van-tag plain type="primary" v-if="medicine.source === 'vl'">拍照识别</van-tag>
      <van-tag plain type="success" v-else>手动添加</van-tag>
    </template>
    <template #price>
      <van-button
        size="mini"
        type="danger"
        plain
        icon="delete-o"
        @click.stop="$emit('remove', medicine)"
      >
        删除
      </van-button>
    </template>
  </van-card>
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

// 用药品名首字母当占位图标（后续可换真实图）
const thumbUrl = computed(() => {
  return '' // 留空用 Vant 默认占位
})
</script>

<style scoped>
.medicine-card {
  margin-bottom: 12px;
  border-radius: 12px;
  overflow: hidden;
}
:deep(.van-card__title) {
  font-size: 18px;
  font-weight: 600;
}
:deep(.van-card__desc) {
  font-size: 14px;
  color: #666;
}
</style>