/**
 * 音频工具：ASR（语音转文字）+ TTS 播放
 *
 * ASR 有两条通道，自动择优、失败互备：
 *  A. 服务端识别（主力）：录音 → 编码 WAV → 上传 /voice/asr → 阿里云百炼 Paraformer
 *  B. 浏览器原生 Web Speech API（兜底）：零延迟、免费，但国内手机基本不可用
 *
 * 为什么必须有 A：
 *  - Android Chrome/Edge 的 SpeechRecognition 把音频送到 Google 服务器，
 *    国内网络连不上，表现为「按住说话 → 转圈 → network 错误 / 没反应」；
 *    而 API 检测本身是 true，按钮照常显示，所以问题看起来像"代码 bug"。
 *  - 微信 / QQ / UC 内置浏览器根本没有这个 API。
 *  - iOS 上 App 内置 WKWebView（微信等）同样不可用。
 * 改成服务端识别后，只要浏览器能给麦克风权限（HTTPS 下基本都行），就能用。
 *
 * TTS 播放：调用后端 Edge-TTS 返回 blob URL，<audio> 播放；失败降级浏览器语音
 */

import { speechToText, textToSpeech } from '@/api/voice'

// ============ 通道 B：浏览器原生识别 ============
let recognition = null
let isRecognizing = false

/** 浏览器是否提供 Web Speech API（注意：有 API ≠ 能用，国内 Android 多为此情况） */
export function isWebSpeechSupported() {
  return (
    typeof window !== 'undefined' &&
    ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)
  )
}

/** 浏览器能否录音（HTTPS + 麦克风 + Web Audio） */
export function canRecordAudio() {
  if (typeof window === 'undefined' || typeof navigator === 'undefined') return false
  const hasGUM = !!(
    (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) ||
    navigator.getUserMedia ||
    navigator.webkitGetUserMedia ||
    navigator.mozGetUserMedia
  )
  const hasAudioCtx = !!(window.AudioContext || window.webkitAudioContext)
  return hasGUM && hasAudioCtx
}

/** 语音输入是否可用（两条通道任一可用即可，UI 用它决定要不要显示麦克风按钮） */
export function isASRSupported() {
  return canRecordAudio() || isWebSpeechSupported()
}

/** 是否处于安全上下文（http://192.168.x.x 这类局域网地址拿不到麦克风） */
export function isSecureContext() {
  return typeof window !== 'undefined' && (window.isSecureContext || location.protocol === 'https:')
}

// ============ 通道 A：录音 + 服务端识别 ============
let micStream = null
let audioCtx = null
let processor = null
let pcmChunks = []
let srcSampleRate = 16000
let recording = false
let recordStartedAt = 0

/** 统一 getUserMedia（兼容老版微信 X5 / Safari 的前缀写法） */
function getUserMediaCompat(constraints) {
  if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
    return navigator.mediaDevices.getUserMedia(constraints)
  }
  const legacy =
    navigator.getUserMedia || navigator.webkitGetUserMedia || navigator.mozGetUserMedia
  if (legacy) {
    return new Promise((resolve, reject) => legacy.call(navigator, constraints, resolve, reject))
  }
  return Promise.reject(new Error('浏览器不支持录音'))
}

/** 线性插值降采样到 16kHz：减小上传体积，ASR 只需 16k */
function resampleTo16k(input, srcRate) {
  if (!srcRate || srcRate === 16000 || input.length === 0) return input
  const ratio = srcRate / 16000
  const outLen = Math.floor(input.length / ratio)
  const out = new Float32Array(outLen)
  for (let i = 0; i < outLen; i++) {
    const pos = i * ratio
    const i0 = Math.floor(pos)
    const i1 = Math.min(i0 + 1, input.length - 1)
    const frac = pos - i0
    out[i] = input[i0] * (1 - frac) + input[i1] * frac
  }
  return out
}

/** 把多段 Float32 PCM 编码成 16bit 单声道 WAV（后端零依赖即可解析） */
function encodeWav(chunks, sampleRate) {
  let total = 0
  for (const c of chunks) total += c.length
  const buffer = new ArrayBuffer(44 + total * 2)
  const view = new DataView(buffer)

  const writeStr = (offset, s) => {
    for (let i = 0; i < s.length; i++) view.setUint8(offset + i, s.charCodeAt(i))
  }

  writeStr(0, 'RIFF')
  view.setUint32(4, 36 + total * 2, true)
  writeStr(8, 'WAVE')
  writeStr(12, 'fmt ')
  view.setUint32(16, 16, true)
  view.setUint16(20, 1, true) // PCM
  view.setUint16(22, 1, true) // 单声道
  view.setUint32(24, sampleRate, true)
  view.setUint32(28, sampleRate * 2, true) // byteRate
  view.setUint16(32, 2, true) // blockAlign
  view.setUint16(34, 16, true) // bits
  writeStr(36, 'data')
  view.setUint32(40, total * 2, true)

  let offset = 44
  for (const c of chunks) {
    for (let i = 0; i < c.length; i++) {
      const s = Math.max(-1, Math.min(1, c[i]))
      view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7fff, true)
      offset += 2
    }
  }
  return new Blob([buffer], { type: 'audio/wav' })
}

function cleanupRecording() {
  try {
    processor?.disconnect()
  } catch {
    /* 已断开 */
  }
  try {
    micStream?.getTracks().forEach((t) => t.stop())
  } catch {
    /* noop */
  }
  try {
    audioCtx?.close()
  } catch {
    /* noop */
  }
  processor = null
  micStream = null
  audioCtx = null
  recording = false
}

/**
 * 开始录音（必须在用户手势中同步调用，否则 iOS Safari 不解锁音频）
 * @returns {Promise<void>} reject 表示拿不到麦克风
 */
export async function startRecording() {
  if (recording) return
  if (!canRecordAudio()) throw new Error('当前浏览器不支持录音')
  if (!isSecureContext()) {
    throw new Error('录音需要 HTTPS 环境，请用 https 地址打开本页')
  }

  // ⚠️ 顺序很重要，实测过：先 new AudioContext() 再 await getUserMedia()，
  // ScriptProcessor 的 onaudioprocess 会一次都不触发（录出来永远 0 字节）。
  // 所以必须先拿到麦克风流，再建音频上下文。
  micStream = await getUserMediaCompat({
    audio: {
      channelCount: 1,
      echoCancellation: true,
      noiseSuppression: true,
      autoGainControl: true,
    },
  })

  const Ctx = window.AudioContext || window.webkitAudioContext
  audioCtx = new Ctx({ sampleRate: 16000 })
  if (audioCtx.state === 'suspended') await audioCtx.resume()
  // Safari 未必认 sampleRate 参数，统一以 ctx.sampleRate 真实值为准
  srcSampleRate = audioCtx.sampleRate || 16000

  const source = audioCtx.createMediaStreamSource(micStream)
  processor = audioCtx.createScriptProcessor(4096, 1, 1)
  pcmChunks = []

  processor.onaudioprocess = (e) => {
    if (!recording) return
    // Web Audio 复用同一块 buffer，必须拷贝，否则录到的是最后一段的重复数据
    pcmChunks.push(new Float32Array(e.inputBuffer.getChannelData(0)))
  }

  source.connect(processor)
  // iOS Safari：不连到 destination 就不会触发 onaudioprocess；
  // 串一个 0 增益节点避免把麦克风声音回放出去（啸叫）
  const silentGain = audioCtx.createGain()
  silentGain.gain.value = 0
  processor.connect(silentGain)
  silentGain.connect(audioCtx.destination)

  recording = true
  recordStartedAt = Date.now()
}

/**
 * 结束录音并上传识别
 * @returns {Promise<{text:string, isDemo:boolean}>}
 */
export async function stopAndTranscribe() {
  if (!recording) return { text: '', isDemo: false }
  recording = false
  const chunks = pcmChunks
  const rate = srcSampleRate
  const durationMs = Date.now() - recordStartedAt

  // 先停硬件，再慢慢编码上传，避免多占麦克风
  const ctx = audioCtx
  processor = null
  audioCtx = null
  try {
    processor?.disconnect()
  } catch {
    /* noop */
  }
  try {
    micStream?.getTracks().forEach((t) => t.stop())
  } catch {
    /* noop */
  }
  micStream = null
  try {
    ctx?.close()
  } catch {
    /* noop */
  }

  if (!chunks.length) {
    return { text: '', isDemo: false, tooShort: true }
  }
  // 太短的录音（误触）直接丢弃，不打扰用户
  if (durationMs < 400) {
    return { text: '', isDemo: false, tooShort: true }
  }
  // 全程几乎没声音（没说话 / 麦克风被静音）：本地就能判断，别白跑一趟识别接口
  let maxAmp = 0
  for (const c of chunks) {
    for (let i = 0; i < c.length; i++) {
      const v = c[i] < 0 ? -c[i] : c[i]
      if (v > maxAmp) maxAmp = v
    }
  }
  if (maxAmp < 0.008) {
    return { text: '', isDemo: false, silent: true, maxAmp }
  }

  let data = chunks
  if (rate !== 16000) {
    // 分段降采样后拼接
    const parts = chunks.map((c) => resampleTo16k(c, rate))
    let total = 0
    for (const p of parts) total += p.length
    const merged = new Float32Array(total)
    let off = 0
    for (const p of parts) {
      merged.set(p, off)
      off += p.length
    }
    data = [merged]
  }

  const wav = encodeWav(data, 16000)
  const res = await speechToText(wav)
  return { text: res?.text || '', isDemo: !!res?.is_demo }
}

/** 取消录音（不上传） */
export function cancelRecording() {
  recording = false
  pcmChunks = []
  cleanupRecording()
}

// ============ 浏览器原生识别（通道 B）============
function startWebSpeech({ lang, onResult, onEnd, onError }) {
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
    // 国内 Android / 微信最常见的就是 network：接口在 Google，连不通
    const msg =
      e.error === 'network'
        ? '浏览器自带识别不可用（需访问 Google 服务），已改用文字输入'
        : `语音识别失败: ${e.error}`
    onError?.(new Error(msg))
  }
  recognition.start()
  isRecognizing = true
}

export function stopRecognition() {
  if (recognition && isRecognizing) {
    try {
      recognition.stop()
    } catch {
      /* noop */
    }
    isRecognizing = false
  }
}

let audioUnlocked = false

/**
 * 解锁浏览器音频会话（iOS Safari 专用）
 *
 * iOS 规定音频能力必须由用户手势解锁：非手势上下文里创建的 AudioContext
 * 会一直停在 suspended，onaudioprocess 永远不触发 —— 表现就是"按住说话，
 * 松手后什么都没发生"。解法：在按下的瞬间先播一段静音，
 * 把整个页面的音频会话解锁掉（解锁后新建的 AudioContext 才能正常 running）。
 *
 * 必须在用户手势的**同步**调用栈里调用，不能放在 await 之后。
 */
export function unlockAudio() {
  if (audioUnlocked) return
  if (!canRecordAudio()) return
  try {
    const Ctx = window.AudioContext || window.webkitAudioContext
    const ctx = new Ctx()
    // 播一个 1 采样的静音 buffer，这是 iOS 上最稳的解锁方式
    const buf = ctx.createBuffer(1, 1, 22050)
    const src = ctx.createBufferSource()
    src.buffer = buf
    src.connect(ctx.destination)
    src.start(0)
    ctx.resume?.()
    audioUnlocked = true
    setTimeout(() => {
      try {
        ctx.close()
      } catch {
        /* noop */
      }
    }, 1500)
  } catch {
    /* 解锁失败不阻塞主流程 */
  }
}

// ============ 统一语音输入入口 ============
/**
 * 按住说话：自动选通道
 *
 * @param {object} opts
 * @param {function} opts.onResult - (text, meta) => void，meta.isDemo 表示演示数据
 * @param {function} [opts.onError] - (err) => void
 * @param {function} [opts.onStatus] - (status) => void，'recording' | 'transcribing' | 'idle'
 * @param {function} [opts.onStart] - () => void，录音真正开始（拿到麦克风）后回调
 */
export function startVoiceInput({ lang = 'zh-CN', onResult, onError, onStatus, onStart } = {}) {
  // 同步执行：还在用户手势栈里，趁这个时机解锁 iOS 的音频能力
  unlockAudio()
  const useCloud = canRecordAudio()

  if (useCloud) {
    onStatus?.('recording')
    startRecording()
      .then(() => {
        onStart?.()
      })
      .catch((e) => {
        cleanupRecording()
        onStatus?.('idle')
        // 录音拿不到（无权限 / 非 HTTPS）→ 退回浏览器原生识别
        if (isWebSpeechSupported()) {
          onStatus?.('recording')
          startWebSpeech({ lang, onResult, onEnd: () => onStatus?.('idle'), onError })
          return
        }
        const msg =
          e && /NotAllowed|Permission|拒绝|权限/i.test(e.message || '')
            ? '麦克风权限被拒绝，请在浏览器设置里允许使用麦克风'
            : e?.message || '无法开始录音'
        onError?.(new Error(msg))
      })
    return
  }

  if (isWebSpeechSupported()) {
    onStatus?.('recording')
    startWebSpeech({
      lang,
      onResult,
      onEnd: () => onStatus?.('idle'),
      onError: (e) => {
        onStatus?.('idle')
        onError?.(e)
      },
    })
    return
  }

  onError?.(new Error('当前浏览器不支持语音输入，请直接输入文字'))
}

/**
 * 松开手：结束录音并识别
 * @returns {Promise<void>}
 */
export async function finishVoiceInput({ onResult, onError, onStatus } = {}) {
  // 浏览器原生通道：直接 stop，结果走 onresult
  if (isRecognizing) {
    stopRecognition()
    return
  }
  if (!recording) return

  onStatus?.('transcribing')
  try {
    const { text, isDemo, tooShort, silent } = await stopAndTranscribe()
    onStatus?.('idle')
    if (tooShort) {
      onError?.(new Error('说话时间太短，请按住后说完整句话'))
      return
    }
    if (silent) {
      onError?.(new Error('没听到声音，请靠近手机再说一次'))
      return
    }
    if (!text) {
      onError?.(new Error('没听清，请再说一次'))
      return
    }
    onResult?.(text, { isDemo })
  } catch (e) {
    onStatus?.('idle')
    // 服务端识别失败 → 提示明确原因，不要静默
    const status = e?.response?.status
    const detail = e?.response?.data?.detail
    let msg = '语音识别失败，请改用文字输入'
    if (status === 503) msg = detail || '语音识别服务暂不可用，请改用文字输入'
    else if (status === 413) msg = '录音太长，请简短一些'
    else if (e?.message) msg = e.message
    onError?.(new Error(msg))
  }
}

/** 取消当前语音输入 */
export function cancelVoiceInput() {
  if (isRecognizing) stopRecognition()
  else cancelRecording()
}

// ============ TTS ============
/** 播放 TTS 音频（接收后端返回的 blob URL） */
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

let speechUnlocked = false
/**
 * 解锁 iOS Safari 的语音播报
 *
 * iOS 规定 speechSynthesis.speak() 必须由用户手势**直接**触发。
 * 我们的播报发生在 await 后端返回之后（已脱离手势上下文），会被静默丢弃 ——
 * 这正是"手机上只有文字、没有声音"的原因。解法：在用户按下按钮时先播一句空话术，
 * 把这个能力提前解锁。
 */
export function unlockSpeech() {
  if (speechUnlocked || !isTTSSupported()) return
  try {
    const u = new SpeechSynthesisUtterance('')
    u.volume = 0
    window.speechSynthesis.speak(u)
    speechUnlocked = true
  } catch {
    /* noop */
  }
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
    // 服务端返回 204（无音频）→ 直接用浏览器语音，不打扰用户
    if (!url) {
      if (!browserSpeak(text, { lang, onEnd })) onError?.(new Error('语音播报不可用'))
      return null
    }
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
