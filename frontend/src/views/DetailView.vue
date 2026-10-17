<template>
  <div class="detail-view">
    <van-nav-bar title="药品详情" left-arrow @click-left="$router.back()" fixed safe-area-inset-top />

    <div v-if="!medicine" class="not-found">
      <EmptyState text="未找到该药品" />
    </div>

    <div v-else class="content">
      <div class="hero">
        <h1>{{ medicine.name }}</h1>
        <van-tag plain :type="sourceType">{{ sourceLabel }}</van-tag>
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

      <van-cell-group inset title="药师叮嘱" v-if="medicine.summary">
        <div class="text-block summary">
          <van-icon name="volume-o" /> {{ medicine.summary }}
        </div>
      </van-cell-group>

      <van-cell-group inset title="适应症" v-if="medicine.indications">
        <div class="text-block">{{ medicine.indications }}</div>
      </van-cell-group>

      <van-cell-group inset title="主要成分" v-if="medicine.ingredients">
        <div class="text-block">{{ medicine.ingredients }}</div>
      </van-cell-group>

      <van-cell-group inset title="不良反应" v-if="medicine.adverse_reactions">
        <div class="text-block">{{ medicine.adverse_reactions }}</div>
      </van-cell-group>

      <van-cell-group inset title="禁忌" v-if="medicine.contraindications">
        <div class="text-block warn">{{ medicine.contraindications }}</div>
      </van-cell-group>

      <van-cell-group inset title="老年人特别注意" v-if="medicine.elderly_notes">
        <div class="text-block elder">{{ medicine.elderly_notes }}</div>
      </van-cell-group>

      <van-cell-group inset title="与其他药的相互作用" v-if="medicine.interactions">
        <div class="text-block warn">{{ medicine.interactions }}</div>
      </van-cell-group>

      <van-cell-group inset title="漏服了怎么办" v-if="medicine.missed_dose">
        <div class="text-block">{{ medicine.missed_dose }}</div>
      </van-cell-group>

      <van-cell-group inset title="怎么保存" v-if="medicine.storage">
        <div class="text-block">{{ medicine.storage }}</div>
      </van-cell-group>

      <van-cell-group inset title="备注" v-if="medicine.remarks">
        <div class="text-block">{{ medicine.remarks }}</div>
      </van-cell-group>

      <div class="action-bar" v-if="!medicine.summary">
        <van-button
          type="primary"
          block
          round
          icon="search"
          :loading="enriching"
          @click="doEnrich"
        >
          AI 生成详细用药说明
        </van-button>
      </div>

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
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showDialog, showToast } from 'vant'
import { storeToRefs } from 'pinia'
import { useMedicineStore } from '@/stores/medicine'
import { enrichMedicine } from '@/api/medicine'
import EmptyState from '@/components/EmptyState.vue'

const route = useRoute()
const router = useRouter()
const medicineStore = useMedicineStore()
const { medicines } = storeToRefs(medicineStore)

const medicine = computed(() =>
  medicines.value.find((m) => m.id === route.query.id)
)

const sourceLabel = computed(() => {
  const map = { vl: '拍照识别', manual: '手动添加', search: '搜索', demo: '示例数据（非真实识别）' }
  return map[medicine.value?.source] || ''
})

const sourceType = computed(() =>
  medicine.value?.source === 'demo' ? 'warning' : 'primary'
)

const enriching = ref(false)

async function doEnrich() {
  const m = medicine.value
  if (!m) return
  enriching.value = true
  try {
    const detail = await enrichMedicine({
      name: m.name,
      spec: m.spec,
      manufacturer: m.manufacturer,
    })
    medicineStore.updateMedicine(m.id, detail)
    showToast('已生成详细用药说明')
  } catch (e) {
    showToast('生成失败，请稍后再试')
  } finally {
    enriching.value = false
  }
}

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
  padding: 12px 12px 90px;
}
.hero {
  text-align: center;
  padding: 22px 16px;
  background: linear-gradient(135deg, #3b8dff 0%, #22c1a4 100%);
  border-radius: 20px;
  color: #fff;
  box-shadow: 0 12px 28px rgba(47, 126, 247, 0.28);
  margin-bottom: 14px;
}
.hero h1 {
  margin: 0 0 10px;
  font-size: 24px;
  font-weight: 700;
  line-height: 1.35;
}
.hero :deep(.van-tag) {
  color: #fff;
  border-color: rgba(255, 255, 255, 0.6);
  background: rgba(255, 255, 255, 0.18);
}
.text-block {
  font-size: 16px;
}
.text-block.warn {
  color: #f5483b;
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
.text-block.summary {
  background: linear-gradient(135deg, #eef6ff 0%, #e6f7f2 100%);
  border-radius: 14px;
  margin: 10px 12px;
  color: #1f2733;
  font-size: 16px;
  font-weight: 500;
}
.text-block.elder {
  color: #ff8f1f;
  background: #fff8ee;
  border-radius: 14px;
  margin: 10px 12px;
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