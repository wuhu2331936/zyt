<template>
  <div class="home">
    <van-nav-bar title="智药通" fixed safe-area-inset-top>
      <template #right>
        <van-icon name="setting-o" size="20" @click="$router.push('/reminder')" />
      </template>
    </van-nav-bar>

    <div class="home-content">
      <!-- 今日提醒卡片 -->
      <van-cell-group inset class="reminder-card" v-if="todayReminders.length">
        <template #title>
          <div class="card-title">
            <van-icon name="alarm-o" color="#ee0a24" />
            <span>今日服药提醒</span>
          </div>
        </template>
        <van-cell
          v-for="r in todayReminders"
          :key="r.id"
          :title="r.medicineName"
          :label="r.time"
        >
          <template #value>
            <van-tag :type="r.taken ? 'success' : 'danger'">
              {{ r.taken ? '已服' : '待服' }}
            </van-tag>
          </template>
        </van-cell>
      </van-cell-group>

      <!-- 我的用药清单 -->
      <div class="section-header">
        <h2>我的用药清单（{{ medicines.length }}）</h2>
        <van-button size="small" type="primary" round icon="plus" @click="$router.push('/scan')">
          添加
        </van-button>
      </div>

      <EmptyState v-if="!medicines.length" text="还没有添加药品，点击下方按钮添加" />
      <MedicineCard
        v-for="m in medicines"
        :key="m.id"
        :medicine="m"
        @click="goDetail(m)"
        @remove="removeMedicine(m.id)"
      />

      <!-- 检查相互作用按钮 -->
      <div v-if="medicines.length >= 2" class="interaction-btn">
        <van-button
          block
          type="warning"
          round
          icon="warning"
          @click="checkInteraction"
          :loading="checking"
        >
          检查 {{ medicines.length }} 种药物相互作用
        </van-button>
      </div>

      <van-dialog
        v-model:show="showInteraction"
        title="⚠️ 药物相互作用"
        :message="interactionSummary"
        confirm-button-text="知道了"
        close-on-click-overlay
      />

      <div class="bottom-spacer"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { showToast } from 'vant'
import { useMedicineStore } from '@/stores/medicine'
import { useReminderStore } from '@/stores/reminder'
import { checkInteractions } from '@/api/medicine'
import MedicineCard from '@/components/MedicineCard.vue'
import EmptyState from '@/components/EmptyState.vue'

const router = useRouter()
const medicineStore = useMedicineStore()
const reminderStore = useReminderStore()

const { medicines } = storeToRefs(medicineStore)
const { reminders } = storeToRefs(reminderStore)

const todayReminders = computed(() =>
  reminders.value.filter((r) => r.time && r.medicineName).slice(0, 3)
)

const checking = ref(false)
const showInteraction = ref(false)
const interactionSummary = ref('')

function goDetail(m) {
  router.push({ path: '/detail', query: { id: m.id } })
}

function removeMedicine(id) {
  medicineStore.removeMedicine(id)
  showToast('已删除')
}

async function checkInteraction() {
  checking.value = true
  try {
    const names = medicines.value.map((m) => m.name)
    const res = await checkInteractions(names)
    if (res.has_risk && res.risks.length) {
      interactionSummary.value =
        res.summary +
        '\n\n风险详情：\n' +
        res.risks
          .map(
            (r) =>
              `·【${r.level.toUpperCase()}】${r.pair.join(' + ')}\n  ${r.description}\n  建议：${r.suggestion}`
          )
          .join('\n\n')
    } else {
      interactionSummary.value = res.summary || '✅ 未发现明显的药物相互作用风险。'
    }
    showInteraction.value = true
  } catch (e) {
    showToast('检查失败：' + (e.message || '网络异常'))
  } finally {
    checking.value = false
  }
}

onMounted(() => {
  reminderStore.checkAndMarkTaken() // 检查今日提醒
})
</script>

<style scoped>
.home {
  padding-top: 46px;
}
.home-content {
  padding: 12px;
}
.reminder-card {
  margin-bottom: 16px;
}
.card-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 600;
  font-size: 16px;
}
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 4px;
  margin-bottom: 12px;
}
.section-header h2 {
  margin: 0;
  font-size: 18px;
}
.interaction-btn {
  margin-top: 20px;
  padding: 0 16px;
}
.bottom-spacer {
  height: 80px;
}
</style>