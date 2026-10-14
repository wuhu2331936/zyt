import dayjs from 'dayjs'

/**
 * 时间格式化工具
 */
export function formatTime(date) {
  return dayjs(date).format('HH:mm')
}

export function formatDateTime(date) {
  return dayjs(date).format('YYYY-MM-DD HH:mm')
}

export function today() {
  return dayjs().format('YYYY-MM-DD')
}

export function isToday(dateStr) {
  return dayjs(dateStr).isSame(dayjs(), 'day')
}