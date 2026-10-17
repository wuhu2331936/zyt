<template>
  <div class="home">
    <van-nav-bar title="智药通" fixed safe-area-inset-top>
      <template #right>
        <van-icon name="setting-o" size="20" @click="$router.push('/reminder')" />
      </template>
    </van-nav-bar>

    <div class="home-content">
      <!-- 顶部问候 + 今日概览 -->
      <div class="hero-card">
        <div class="hero-top">
          <div class="hero-left">
            <p class="hero-greeting">{{ greeting }}</p>
            <h1 class="hero-title">今日记得按时吃药</h1>
          </div>
          <div class="hero-badge">💊</div>
        </div>
        <div class="hero-stats">
          <div class="stat">
            <span class="stat-num">{{ medicines.length }}</span>
            <span class="stat-label">在用药品</span>
          </div>
          <div class="stat-divider"></div>
          <div class="stat">
            <span class="stat-num warning">{{ pendingCount }}</span>
            <span class="stat-label">待服用</span>
          </div>
          <div class="stat-divider"></div>
          <div class="stat">
            <span class="stat-num success">{{ takenCount }}</span>
            <span class="stat-label">已服用</span>
          </div>
        </div>
      </div>

      <!-- 快捷入口 -->
      <div class="quick-actions">
        <div class="action-card" @click="$router.push('/scan')">
          <div class="action-icon scan">📸</div>
          <div class="action-text">
            <b>拍照识药</b>
            <span>对准药盒正面</span>
          </div>
        </div>
        <div class="action-card" @click="$router.push('/voice')">
          <div class="action-icon voice">🎙️</div>
          <div class="action-text">
            <b>语音问答</b>
            <span>问用法与禁忌</span>
          </div>
        </div>
      </div>

      <!-- 今日提醒（只展示已启用的；可就地标记已服） -->
      <div class="zyt-card" v-if="todayReminders.length">
        <div class="card-title">
          <van-icon name="alarm-o" color="#f5483b" size="18" />
          <span>今日服药提醒</span>
        </div>
        <div
          v-for="r in todayReminders"
          :key="r.id"
          class="remind-row"
        >
          <div class="remind-time">{{ r.time }}</div>
          <div class="remind-name">{{ r.medicineName }}</div>
          <van-tag :type="reminderStore.isTaken(r) ? 'success' : 'danger'" round>
            {{ reminderStore.isTaken(r) ? '已服' : '待服' }}
          </van-tag>
          <van-button
            v-if="!reminderStore.isTaken(r)"
            size="mini"
            type="success"
            round
            icon="success"
            @click="markTaken(r.id)"
          >
            吃了
          </van-button>
          <van-button
            v-else
            size="mini"
            plain
            round
            @click="unmarkTaken(r.id)"
          >
            撤销
          </van-button>
        </div>
      </div>

      <!-- 我的用药清单 -->
      <div class="section-header">
        <h2>我的用药清单</h2>
        <span class="count-badge">{{ medicines.length }}</span>
        <van-button
          class="add-btn"
          size="small"
          type="primary"
          round
          icon="plus"
          @click="$router.push('/scan')"
        >
          添加药品
        </van-button>
      </div>

      <EmptyState v-if="!medicines.length" text="还没有添加药品，点击上方按钮添加" />
      <MedicineCard
        v-for="m in medicines"
        :key="m.id"
        :medicine="m"
        @click="goDetail(m)"
        @remove="removeMedicine(m.id)"
      />

      <!-- 检查相互作用 -->
      <div v-if="medicines.length >= 2" class="interaction-btn">
        <van-button
          block
          type="warning"
          round
          icon="warning"
          size="large"
          @click="checkInteraction"
          :loading="checking"
        >
          检查 {{ medicines.length }} 种药物相互作用
        </van-button>
      </div>

      <!-- 相互作用结果：结构化卡片，不再是一坨纯文本 -->
      <van-dialog
        v-model:show="showInteraction"
        title="⚠️ 药物相互作用"
        confirm-button-text="知道了"
        close-on-click-overlay
      >
        <div class="risk-box">
          <p class="risk-summary">{{ interactionSummary }}</p>
          <div
            v-for="(r, i) in interactionRisks"
            :key="i"
            class="risk-item"
            :class="'lv-' + r.level"
          >
            <div class="risk-head">
              <span class="risk-level">{{ levelText(r) }}</span>
              <span class="risk-pair">{{ (r.pair || []).join(' + ') }}</span>
            </div>
            <p class="risk-desc">{{ r.description }}</p>
            <p class="risk-sug">建议：{{ r.suggestion }}</p>
          </div>
        </div>
      </van-dialog>

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

// 直接用 store 的 getter：已按 enabled 过滤并按时间排序
const todayReminders = computed(() => reminderStore.todayReminders)

const pendingCount = computed(() => reminderStore.pendingCount)
const takenCount = computed(() => reminderStore.takenCount)

function markTaken(id) {
  reminderStore.markTaken(id)
  showToast('已标记为已服用')
}
function unmarkTaken(id) {
  reminderStore.unmarkTaken(id)
  showToast('已撤销')
}

const greeting = computed(() => {
  const h = new Date().getHours()
  if (h < 6) return '夜深了，注意休息'
  if (h < 11) return '早上好'
  if (h < 14) return '中午好'
  if (h < 18) return '下午好'
  return '晚上好'
})

const checking = ref(false)
const showInteraction = ref(false)
const interactionSummary = ref('')
const interactionRisks = ref([])

// 风险等级中文（后端可能没给 level_cn，这里兜底）
const LEVEL_CN = {
  critical: '严禁',
  major: '较严重',
  moderate: '中等',
  minor: '轻微',
}
function levelText(r) {
  return r.level_cn || LEVEL_CN[String(r.level || '').toLowerCase()] || '中等'
}

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
    interactionRisks.value = res.risks || []
    interactionSummary.value =
      res.summary ||
      (interactionRisks.value.length
        ? '以下组合存在需要注意的相互作用：'
        : '✅ 未发现明显的药物相互作用风险。')
    showInteraction.value = true
  } catch (e) {
    showToast('检查失败：' + (e.message || '网络异常'))
  } finally {
    checking.value = false
  }
}

onMounted(() => {
  reminderStore.checkAndMarkTaken()
})
</script>

<style scoped>
.home {
  padding-top: 46px;
}
.home-content {
  padding: 12px 12px 0;
}

/* 顶部渐变卡 */
.hero-card {
  background: linear-gradient(135deg, #3b8dff 0%, #22c1a4 100%);
  border-radius: 20px;
  padding: 20px 18px;
  color: #fff;
  box-shadow: 0 12px 28px rgba(47, 126, 247, 0.28);
  margin-bottom: 14px;
}
.hero-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
}
.hero-greeting {
  margin: 0 0 4px;
  font-size: 15px;
  opacity: 0.92;
}
.hero-title {
  margin: 0;
  font-size: 22px;
  font-weight: 700;
  letter-spacing: 0.5px;
}
.hero-badge {
  width: 48px;
  height: 48px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.22);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 26px;
}
.hero-stats {
  display: flex;
  align-items: center;
  margin-top: 18px;
  padding-top: 14px;
  border-top: 1px solid rgba(255, 255, 255, 0.28);
}
.stat {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}
.stat-num {
  font-size: 24px;
  font-weight: 700;
  line-height: 1.1;
}
.stat-num.warning {
  color: #ffe08a;
}
.stat-num.success {
  color: #c8ffe9;
}
.stat-label {
  font-size: 13px;
  opacity: 0.9;
}
.stat-divider {
  width: 1px;
  height: 28px;
  background: rgba(255, 255, 255, 0.3);
}

/* 快捷入口 */
.quick-actions {
  display: flex;
  gap: 12px;
  margin-bottom: 14px;
}
.action-card {
  flex: 1;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 6px 20px rgba(31, 45, 61, 0.07);
  padding: 16px 14px;
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  transition: transform 0.15s ease;
}
.action-card:active {
  transform: scale(0.97);
}
.action-icon {
  width: 44px;
  height: 44px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
}
.action-icon.scan {
  background: linear-gradient(135deg, #e3f0ff 0%, #d3e8ff 100%);
}
.action-icon.voice {
  background: linear-gradient(135deg, #e0f8f1 0%, #d2f3ea 100%);
}
.action-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.action-text b {
  font-size: 16px;
  color: #1f2733;
}
.action-text span {
  font-size: 13px;
  color: #97a1b0;
}

/* 提醒列表 */
.card-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 600;
  font-size: 17px;
  margin-bottom: 10px;
}
.remind-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 0;
  border-top: 1px solid #f2f5f9;
}
.remind-time {
  font-size: 15px;
  font-weight: 700;
  color: #2f7ef7;
  min-width: 48px;
}
.remind-name {
  flex: 1;
  font-size: 16px;
}

/* 区块头 */
.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 4px 12px;
}
.section-header h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
}
.count-badge {
  min-width: 22px;
  height: 22px;
  padding: 0 7px;
  border-radius: 11px;
  background: #e9f2ff;
  color: #2f7ef7;
  font-size: 13px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}
.add-btn {
  margin-left: auto;
}

/* 相互作用结果卡片 */
.risk-box {
  padding: 4px 20px 16px;
  max-height: 52vh;
  overflow-y: auto;
}
.risk-summary {
  margin: 0 0 12px;
  font-size: 14px;
  line-height: 1.6;
  color: #1f2733;
}
.risk-item {
  border-radius: 12px;
  padding: 10px 12px;
  margin-bottom: 10px;
  background: #fff8e6;
  border-left: 4px solid #ff9f1c;
}
.risk-item.lv-critical {
  background: #fdecea;
  border-left-color: #ee0a24;
}
.risk-item.lv-major {
  background: #fff1e8;
  border-left-color: #ff6b35;
}
.risk-item.lv-moderate {
  background: #fff8e6;
  border-left-color: #ff9f1c;
}
.risk-item.lv-minor {
  background: #f2f8ff;
  border-left-color: #3b8dff;
}
.risk-head {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}
.risk-level {
  flex: none;
  padding: 1px 8px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
  color: #fff;
  background: #ff9f1c;
}
.lv-critical .risk-level {
  background: #ee0a24;
}
.lv-major .risk-level {
  background: #ff6b35;
}
.lv-minor .risk-level {
  background: #3b8dff;
}
.risk-pair {
  font-size: 15px;
  font-weight: 600;
  color: #1f2733;
}
.risk-desc,
.risk-sug {
  margin: 4px 0 0;
  font-size: 13px;
  line-height: 1.6;
  color: #4a5568;
}
.risk-sug {
  color: #2f7ef7;
}

.interaction-btn {
  margin-top: 18px;
}
/* 底部留白已由 App.vue 的 .page-wrap.has-tabbar 统一处理 */
.bottom-spacer {
  height: 8px;
}
</style>
