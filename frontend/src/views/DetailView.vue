<template>
  <div class="detail-view">
    <van-nav-bar title="药品详情" left-arrow @click-left="$router.back()" fixed safe-area-inset-top />

    <div v-if="!medicine" class="not-found">
      <EmptyState text="未找到该药品" />
    </div>

    <div v-else class="content">
      <div class="hero">
        <h1>{{ medicine.name }}</h1>
        <van-tag plain type="primary">{{ sourceLabel }}</van-tag>
      </div>

      <van-cell-group inset title="基本信息">
        <van-cell v-if="medicine.spec" title="规格" :value="medicine.spec" />
        <van-cell v-if="medicine.manufacturer" title="生产厂家" :value="medicine.manufacturer" />
        <van-cell v-if="medicine.usage" title="用法用量">
          <template #default>
            <div style="color: #ee0a24; font-weight: 600;">{{ medicine.usage }}</div>
          </template>
        </van-cell>
      </van-cell-group>

      <van-cell-group inset title="适应症" v-if="medicine.indications">
        <div class="text-block">{{ medicine.indications }}</div>
      </van-cell-group>

      <van-cell-group inset title="禁忌" v-if="medicine.contraindications">
        <div class="text-block warn">{{ medicine.contraindications }}</div>
      </van-cell-group>

      <van-cell-group inset title="备注" v-if="medicine.remarks">
        <div class="text-block">{{ medicine.remarks }}</div>
      </van-cell-group>

      <div class="action-bar">
        <van-button type="primary" round icon="clock-o" @click="goReminder">
          设置服药提醒
        </van-button>
        <van-button type="danger" plain round icon="delete-o" @click="confirmRemove">
          删除药品
        </van-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showDialog, showToast } from 'vant'
import { storeToRefs } from 'pinia'
import { useMedicineStore } from '@/stores/medicine'
import EmptyState from '@/components/EmptyState.vue'

const route = useRoute()
const router = useRouter()
const medicineStore = useMedicineStore()
const { medicines } = storeToRefs(medicineStore)

const medicine = computed(() =>
  medicines.value.find((m) => m.id === route.query.id)
)

const sourceLabel = computed(() => {
  const map = { vl: '拍照识别', manual: '手动添加', search: '搜索' }
  return map[medicine.value?.source] || ''
})

function goReminder() {
  router.push({ path: '/reminder', query: { medName: medicine.value.name } })
}

function confirmRemove() {
  showDialog({
    title: '确认删除',
    message: `确定要从清单删除「${medicine.value.name}」吗？`,
    showCancelButton: true,
  })
    .then(() => {
      medicineStore.removeMedicine(medicine.value.id)
      showToast('已删除')
      router.back()
    })
    .catch(() => {})
}
</script>

<style scoped>
.detail-view {
  padding-top: 46px;
}
.content {
  padding: 16px;
}
.hero {
  text-align: center;
  padding: 20px 0;
}
.hero h1 {
  margin: 0 0 12px;
  font-size: 24px;
}
.text-block {
  padding: 12px 16px;
  color: #333;
  line-height: 1.6;
  white-space: pre-wrap;
}
.text-block.warn {
  color: #ee0a24;
}
.action-bar {
  padding: 16px;
  display: flex;
  gap: 12px;
}
.action-bar .van-button {
  flex: 1;
}
.not-found {
  padding-top: 100px;
}
</style>