import { defineStore } from 'pinia'
import { getItem, setItem } from '@/utils/storage'
import { today } from '@/utils/time'

const KEY = 'reminders'
const HISTORY_KEY = 'reminder_history'

export const useReminderStore = defineStore('reminder', {
  state: () => ({
    reminders: getItem(KEY, []),
    history: getItem(HISTORY_KEY, {}), // { 'YYYY-MM-DD': [{medicineName, time, takenAt}] }
  }),
  getters: {
    /** 今日启用的提醒，按时间升序 */
    todayReminders: (s) =>
      s.reminders
        .filter((r) => r.enabled && r.time && r.medicineName)
        .sort((a, b) => String(a.time).localeCompare(String(b.time))),

    /** 是否已服用（用 takenDate 记录，跨天自动失效，无需定时任务清理） */
    isTaken: (s) => (r) => !!r && r.takenDate === today(),

    /** 今日统计 */
    pendingCount(s) {
      return this.todayReminders.filter((r) => !this.isTaken(r)).length
    },
    takenCount(s) {
      return this.todayReminders.filter((r) => this.isTaken(r)).length
    },
  },
  actions: {
    addReminder(reminder) {
      const id = 'rem_' + Date.now()
      this.reminders.push({
        id,
        medicineName: reminder.medicineName || '',
        time: reminder.time || '08:00',
        repeat: reminder.repeat || 'daily',
        voice: reminder.voice || 'zh-CN-XiaoxiaoNeural',
        enabled: true,
        takenDate: null,
        createdAt: Date.now(),
      })
      this._persist()
      return id
    },
    toggleReminder(id) {
      const r = this.reminders.find((x) => x.id === id)
      if (r) {
        r.enabled = !r.enabled
        this._persist()
      }
    },
    removeReminder(id) {
      this.reminders = this.reminders.filter((r) => r.id !== id)
      this._persist()
    },
    /** 标记已服用：写入当日状态 + 追加历史记录 */
    markTaken(id) {
      const r = this.reminders.find((x) => x.id === id)
      if (!r) return
      const dateKey = today()
      r.takenDate = dateKey
      if (!this.history[dateKey]) this.history[dateKey] = []
      this.history[dateKey].push({
        medicineName: r.medicineName,
        time: r.time,
        takenAt: Date.now(),
      })
      setItem(HISTORY_KEY, this.history)
      this._persist()
    },
    /** 取消已服用标记（误触可撤销） */
    unmarkTaken(id) {
      const r = this.reminders.find((x) => x.id === id)
      if (!r) return
      r.takenDate = null
      this._persist()
    },
    /** 兼容旧调用：真正的到点提醒由 utils/reminderWatcher.js 全局定时触发 */
    checkAndMarkTaken() {},
    /** 外部直接改了 enabled 等字段后手动落盘（v-model 直改 store 不会自动持久化） */
    persist() {
      this._persist()
    },
    _persist() {
      setItem(KEY, this.reminders)
    },
  },
})
