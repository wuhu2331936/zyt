import { defineStore } from 'pinia'
import { getItem, setItem } from '@/utils/storage'

const KEY = 'medicines'

export const useMedicineStore = defineStore('medicine', {
  state: () => ({
    medicines: getItem(KEY, []),
  }),
  getters: {
    count: (s) => s.medicines.length,
    byId: (s) => (id) => s.medicines.find((m) => m.id === id),
  },
  actions: {
    addMedicine(med) {
      const id = 'med_' + Date.now() + '_' + Math.random().toString(36).slice(2, 7)
      // 注意：必须保留 AI 补全的全部字段（药师叮嘱/成分/不良反应/老年人注意/相互作用/
      // 漏服/储存），否则识药后加入药箱，详情页的详细说明会全部丢失。
      const item = {
        ...med,
        id,
        name: med.name || '未知药品',
        spec: med.spec || '',
        manufacturer: med.manufacturer || '',
        usage: med.usage || '',
        indications: med.indications || '',
        contraindications: med.contraindications || '',
        remarks: med.remarks || '',
        source: med.source || 'manual',
        createdAt: Date.now(),
      }
      this.medicines.push(item)
      this._persist()
      return id
    },
    updateMedicine(id, patch) {
      const idx = this.medicines.findIndex((m) => m.id === id)
      if (idx >= 0) {
        this.medicines[idx] = { ...this.medicines[idx], ...patch }
        this._persist()
      }
    },
    removeMedicine(id) {
      this.medicines = this.medicines.filter((m) => m.id !== id)
      this._persist()
    },
    _persist() {
      setItem(KEY, this.medicines)
    },
  },
})