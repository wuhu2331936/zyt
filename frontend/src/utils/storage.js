/**
 * localStorage 封装（前端存储用药清单和提醒）
 */
const PREFIX = 'zhiyaotong:'

export function getItem(key, defaultValue = null) {
  try {
    const raw = localStorage.getItem(PREFIX + key)
    return raw ? JSON.parse(raw) : defaultValue
  } catch {
    return defaultValue
  }
}

export function setItem(key, value) {
  try {
    localStorage.setItem(PREFIX + key, JSON.stringify(value))
  } catch (e) {
    console.warn('localStorage 写入失败', e)
  }
}

export function removeItem(key) {
  localStorage.removeItem(PREFIX + key)
}