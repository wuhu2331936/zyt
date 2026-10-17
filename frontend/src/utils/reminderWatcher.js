/**
 * 服药提醒定时器
 *
 * 每 20 秒比对一次当前时间与提醒时间，命中且今日未标记已服时：
 * 1) 页面内 Toast 提示
 * 2) 浏览器系统通知（已授权时）
 * 3) Edge-TTS 语音播报（老年人场景的核心体验）
 *
 * 同一条提醒在同一分钟内只触发一次（fired 去重）。
 */
import { showToast } from 'vant'
import { today } from '@/utils/time'
import { speakText } from '@/utils/audio'

let timer = null
const fired = new Set()

function hhmm(d = new Date()) {
  const p = (n) => String(n).padStart(2, '0')
  return `${p(d.getHours())}:${p(d.getMinutes())}`
}

/** 请求系统通知权限（需在用户手势中调用，这里放在首次进入页面时调用即可） */
export function requestNotifyPermission() {
  if (typeof window === 'undefined' || !('Notification' in window)) return
  if (Notification.permission === 'default') {
    const p = Notification.requestPermission()
    if (p && typeof p.catch === 'function') p.catch(() => {})
  }
}

function notify(text) {
  if (typeof window !== 'undefined' && 'Notification' in window) {
    if (Notification.permission === 'granted') {
      try {
        new Notification('智药通 · 用药提醒', {
          body: text,
          icon: '/pwa-icons/icon-192.png',
        })
      } catch (e) {
        /* 部分浏览器不支持带 icon 的构造，忽略 */
      }
    }
  }
}

function speak(text, voice) {
  // 后端 Edge-TTS 或浏览器内置语音，任一可用即可出声
  speakText(text, { voice }).catch(() => {})
}

function check(store) {
  const dateKey = today()
  const now = hhmm()
  for (const r of store.reminders) {
    if (!r.enabled || !r.time || !r.medicineName) continue
    if (String(r.time) !== now) continue
    if (store.isTaken(r)) continue

    const fireKey = `${dateKey}|${r.id}|${now}`
    if (fired.has(fireKey)) continue
    fired.add(fireKey)

    const text = `该吃药了，${r.medicineName}，请按时服用`
    showToast({ message: '⏰ ' + text, duration: 5000 })
    notify(text)
    speak(text, r.voice)
  }
}

/** 启动全局提醒监听（在 App.vue onMounted 调用一次即可） */
export function startReminderWatcher(store, intervalMs = 20000) {
  if (timer) return
  check(store)
  timer = setInterval(() => check(store), intervalMs)
}

export function stopReminderWatcher() {
  if (timer) {
    clearInterval(timer)
    timer = null
  }
}
