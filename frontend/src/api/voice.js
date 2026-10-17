import request from './request'

/**
 * 语音问答（文字版）
 * @param {object} params
 * @param {string} params.question - 用户问题
 * @param {string[]} [params.medicineContext] - 当前用药清单
 * @param {Array} [params.history] - 对话历史
 */
export function voiceChat({ question, medicineContext = [], history = [] }) {
  return request.post('/voice/chat', {
    question,
    medicine_context: medicineContext,
    history,
  })
}

/**
 * 文字转语音（Edge-TTS）
 * @param {string} text
 * @returns {string} - 音频 URL（blob URL）
 */
/**
 * 文字转语音（Edge-TTS）
 *
 * 后端合成成功返回 mp3；服务端不可用返回 204（空 body，语义：请走浏览器语音），
 * 这里统一映射成 null，由 speakText 负责降级，全程不弹错误提示。
 *
 * @param {string} text
 * @returns {string|null} 音频 blob URL，服务端无音频时为 null
 */
export async function textToSpeech(text, voice) {
  let res
  try {
    res = await request.post(
      '/voice/tts',
      { text, voice },
      {
        responseType: 'blob',
        silent: true,
        validateStatus: (s) => s < 400, // 204 视为正常（服务端无音频）
      }
    )
  } catch {
    return null
  }
  const isBlob = typeof Blob !== 'undefined' && res instanceof Blob
  if (!isBlob || res.size === 0) return null
  return URL.createObjectURL(res)
}

/**
 * 获取可选 TTS 声音列表
 */
export function listVoices() {
  return request.get('/voice/voices')
}