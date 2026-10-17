<template>
  <div class="reminder-view">
    <van-nav-bar title="服药提醒" left-arrow @click-left="$router.back()" fixed safe-area-inset-top>
      <template #right>
        <van-icon name="plus" size="20" @click="showAdd = true" />
      </template>
    </van-nav-bar>

    <div class="content">
      <van-cell-group inset>
        <van-cell title="🔊 语音播报">
          <template #right-icon>
            <van-switch v-model="voiceOn" @change="onVoiceToggle" />
          </template>
        </van-cell>
      </van-cell-group>

      <h3 class="section-title">今日提醒（{{ todayReminders.length }}）</h3>
      <EmptyState v-if="!todayReminders.length" text="还没有提醒，点击右上角 + 添加" />

      <van-cell-group v-else inset>
        <van-swipe-cell v-for="r in todayReminders" :key="r.id">
          <van-cell
            :title="r.medicineName"
            :label="r.time + ' · ' + (r.voice === 'zh-CN-XiaoxiaoNeural' ? '晓晓' : '云希')"
            center
          >
            <template #right-icon>
              <van-switch v-model="r.enabled" @change="toggle(r.id)" />
            </template>
          </van-cell>
          <template #right>
            <van-button square type="danger" text="删除" style="height: 100%;" @click="remove(r.id)" />
          </template>
        </van-swipe-cell>
      </van-cell-group>
    </div>

    <!-- 新增提醒弹窗 -->
    <van-popup v-model:show="showAdd" position="bottom" round :style="{ height: '60%' }">
      <div class="popup">
        <h3>添加服药提醒</h3>
        <van-cell-group inset>
          <van-field v-model="newReminder.medicineName" label="药品名" placeholder="如 阿司匹林" />
          <van-field
            v-model="newReminder.time"
            label="服药时间"
            placeholder="点击选择"
            readonly
            is-link
            @click="showTimePicker = true"
          />
          <van-field
            v-model="newReminder.voiceLabel"
            label="语音"
            readonly
            is-link
            @click="showVoicePicker = true"
          />
        </van-cell-group>
        <div style="padding: 16px;">
          <van-button type="primary" block round @click="confirmAdd">保存</van-button>
        </div>
      </div>
    </van-popup>

    <van-popup v-model:show="showTimePicker" position="bottom">
      <van-time-picker
        v-model="timeColumns"
        :title="`选择时间`"
        @confirm="onTimeConfirm"
        @cancel="showTimePicker = false"
      />
    </van-popup>

    <van-popup v-model:show="showVoicePicker" position="bottom">
      <van-picker
        :columns="voiceColumns"
        @confirm="onVoiceConfirm"
        @cancel="showVoicePicker = false"
      />
    </van-popup>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { showToast } from 'vant'
import { useReminderStore } from '@/stores/reminder'
import { useVoiceStore } from '@/stores/voice'
import EmptyState from '@/components/EmptyState.vue'

const route = useRoute()
const router = useRouter()
const reminderStore = useReminderStore()
const voiceStore = useVoiceStore()
const { reminders } = storeToRefs(reminderStore)

const voiceOn = ref(voiceStore.voiceEnabled)
function onVoiceToggle(e) {
  voiceStore.setVoiceEnabled(e)
}

const todayReminders = computed(() =>
  reminders.value.filter((r) => r.enabled).sort((a, b) => a.time.localeCompare(b.time))
)

// 新增弹窗
const showAdd = ref(false)
const newReminder = ref({
  medicineName: '',
  time: '08:00',
  voice: 'zh-CN-XiaoxiaoNeural',
  voiceLabel: '晓晓（女声温柔）',
})
const showTimePicker = ref(false)
const timeColumns = ref(['08', '00'])

function onTimeConfirm({ selectedValues }) {
  newReminder.value.time = selectedValues.join(':')
  showTimePicker.value = false
}

const showVoicePicker = ref(false)
const voiceColumns = [
  { text: '晓晓（女声温柔）', value: 'zh-CN-XiaoxiaoNeural' },
  { text: '云希（男声稳重）', value: 'zh-CN-YunxiNeural' },
  { text: '云扬（男声播报）', value: 'zh-CN-YunyangNeural' },
  { text: '晓伊（女声亲切）', value: 'zh-CN-XiaoyiNeural' },
]

function onVoiceConfirm({ selectedOptions }) {
  newReminder.value.voice = selectedOptions[0].value
  newReminder.value.voiceLabel = selectedOptions[0].text
  showVoicePicker.value = false
}

function confirmAdd() {
  if (!newReminder.value.medicineName) {
    showToast('请填写药品名')
    return
  }
  reminderStore.addReminder(newReminder.value)
  showToast({ type: 'success', message: '已添加' })
  showAdd.value = false
  newReminder.value.medicineName = ''
}

function toggle(id) {
  reminderStore.toggleReminder(id)
}

function remove(id) {
  reminderStore.removeReminder(id)
  showToast('已删除')
}

onMounted(() => {
  // 从详情页跳转过来时预填药品名
  if (route.query.medName) {
    newReminder.value.medicineName = route.query.medName
    showAdd.value = true
  }
})
</script>

<style scoped>
.reminder-view {
  padding-top: 46px;
}
.content {
  padding: 12px;
}
.section-title {
  margin: 18px 12px 10px;
  font-size: 17px;
  font-weight: 700;
  color: #1f2733;
}
.popup h3 {
  font-size: 18px;
  font-weight: 700;
}
.popup {
  padding: 16px;
}
.popup h3 {
  margin: 0 0 16px;
  text-align: center;
}
</style>