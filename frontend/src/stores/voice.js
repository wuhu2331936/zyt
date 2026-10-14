import { defineStore } from 'pinia'
import { getItem, setItem } from '@/utils/storage'

const KEY = 'voice_history'

export const useVoiceStore = defineStore('voice', {
  state: () => ({
    history: getItem(KEY, []),
    voiceEnabled: getItem('voice_enabled', true),
  }),
  actions: {
    addMessage(msg) {
      this.history.push({
        id: Date.now(),
        role: msg.role,
        content: msg.content,
        ts: Date.now(),
      })
      // 最多保留 50 条
      if (this.history.length > 50) this.history = this.history.slice(-50)
      setItem(KEY, this.history)
    },
    clearHistory() {
      this.history = []
      setItem(KEY, [])
    },
    setVoiceEnabled(enabled) {
      this.voiceEnabled = enabled
      setItem('voice_enabled', enabled)
    },
  },
})