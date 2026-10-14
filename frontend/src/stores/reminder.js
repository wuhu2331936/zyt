import { defineStore } from 'pinia'
import { getItem, setItem } from '@/utils/storage'
import { isToday, today } from '@/utils/time'

const KEY = 'reminders'
const HISTORY_KEY = 'reminder_history'

export const useReminderStore = defineStore('reminder', {
  state: () => ({
    reminders: getItem(KEY, []),
    history: getItem(HISTORY_KEY, {}), // { 'YYYY-MM-DD': [{medicineName, time, taken}] }
  }),
  getters: {
    todayReminders: (s) =>
      s.reminders
        .filter((r) => r.enabled)
        .sort((a, b) => a.time.localeCompare(b.time)),
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
    markTaken(id) {
      const r = this.reminders.find((x) => x.id === id)
      if (!r) return
      const dateKey = today()
      if (!this.history[dateKey]) this.history[dateKey] = []
      this.history[dateKey].push({
        medicineName: r.medicineName,
        time: r.time,
        takenAt: Date.now(),
      })
      setItem(HISTORY_KEY, this.history)
    },
    checkAndMarkTaken() {
      // 仅占位：实际由插件前端负责调用 scheduleReminder
    },
    _persist() {
      setItem(KEY, this.reminders)
    },
  },
})