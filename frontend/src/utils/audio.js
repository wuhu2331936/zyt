/**
 * 音频工具：ASR（语音转文字）+ TTS 播放
 *
 * ASR：使用浏览器原生 Web Speech API（webkitSpeechRecognition）
 *      无需后端，免费，但只有 HTTPS / localhost 可用。
 * TTS 播放：调用后端 Edge-TTS 返回 blob URL，<audio> 播放
 */

let recognition = null
let isRecognizing = false

/**
 * 检查浏览器是否支持 ASR
 */
export function isASRSupported() {
  return 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window
}

/**
 * 开始录音识别
 * @param {object} opts
 * @param {string} [opts.lang='zh-CN']
 * @param {function} opts.onResult - (text, isFinal) => void
 * @param {function} [opts.onEnd] - () => void
 * @param {function} [opts.onError] - (err) => void
 */
export function startRecognition({ lang = 'zh-CN', onResult, onEnd, onError } = {}) {
  if (!isASRSupported()) {
    onError?.(new Error('当前浏览器不支持语音识别，请使用 Chrome / Edge 浏览器'))
    return null
  }
  if (isRecognizing) {
    stopRecognition()
  }
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition
  recognition = new SR()
  recognition.lang = lang
  recognition.interimResults = false
  recognition.continuous = false

  recognition.onresult = (e) => {
    const text = e.results[0][0].transcript
    onResult?.(text, true)
  }
  recognition.onend = () => {
    isRecognizing = false
    onEnd?.()
  }
  recognition.onerror = (e) => {
    isRecognizing = false
    onError?.(new Error(`语音识别失败: ${e.error}`))
  }

  recognition.start()
  isRecognizing = true
  return recognition
}

export function stopRecognition() {
  if (recognition && isRecognizing) {
    recognition.stop()
    isRecognizing = false
  }
}

/**
 * 播放 TTS 音频（接收后端返回的 blob URL）
 */
export function playAudio(url, { onEnd, onError } = {}) {
  const audio = new Audio(url)
  audio.onended = () => onEnd?.()
  audio.onerror = () => onError?.(new Error('音频播放失败'))
  audio.play().catch((e) => onError?.(e))
  return audio
}