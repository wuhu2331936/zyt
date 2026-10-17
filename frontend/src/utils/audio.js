/**
 * 音频工具：ASR（语音转文字）+ TTS 播放
 *
 * ASR：使用浏览器原生 Web Speech API（webkitSpeechRecognition）
 *      无需后端，免费，但只有 HTTPS / localhost 可用。
 * TTS 播放：调用后端 Edge-TTS 返回 blob URL，<audio> 播放
 */

import { textToSpeech } from '@/api/voice'

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

/** 浏览器是否支持内置语音播报（Web Speech API） */
export function isTTSSupported() {
  return typeof window !== 'undefined' && 'speechSynthesis' in window
}

/**
 * 用浏览器内置语音合成播报（兜底方案）
 *
 * 后端 Edge-TTS 依赖微软接口，近期常返回 403（签名校验变更），
 * 播报失败时必须用浏览器原生 TTS 顶上，否则老年人场景完全没声音。
 */
export function browserSpeak(text, { lang = 'zh-CN', rate = 1, onEnd, onError } = {}) {
  if (!isTTSSupported()) {
    onError?.(new Error('当前浏览器不支持语音播报'))
    return false
  }
  try {
    window.speechSynthesis.cancel()
    const u = new SpeechSynthesisUtterance(String(text || '').slice(0, 200))
    u.lang = lang
    u.rate = rate
    u.onend = () => onEnd?.()
    u.onerror = (e) => onError?.(e)
    window.speechSynthesis.speak(u)
    return true
  } catch (e) {
    onError?.(e)
    return false
  }
}

/**
 * 统一的语音播报入口：后端 Edge-TTS 优先，失败自动降级浏览器播报
 *
 * @param {string} text 要播报的文本
 * @param {object} opts
 * @param {string} [opts.voice] 后端音色
 * @param {function} [opts.onEnd]
 * @param {function} [opts.onError] 两种方式都失败时回调
 */
export async function speakText(text, { voice, lang = 'zh-CN', onEnd, onError } = {}) {
  if (!text) return null

  // 1) 优先后端 Edge-TTS（音色更好）
  try {
    const url = await textToSpeech(text, voice)
    return playAudio(url, {
      onEnd,
      // 音频加载/播放失败时降级，不要静默吞掉
      onError: () => {
        const ok = browserSpeak(text, { lang, onEnd })
        if (!ok) onError?.(new Error('语音播报不可用'))
      },
    })
  } catch (e) {
    // 2) 后端不可用（如微软接口 403）→ 浏览器播报
    const ok = browserSpeak(text, { lang, onEnd })
    if (!ok) onError?.(e)
    return null
  }
}