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
export async function textToSpeech(text, voice) {
  const res = await request.post(
    '/voice/tts',
    { text, voice },
    { responseType: 'blob', silent: true } // 失败由调用方静默降级浏览器语音
  )
  return URL.createObjectURL(res)
}

/**
 * 获取可选 TTS 声音列表
 */
export function listVoices() {
  return request.get('/voice/voices')
}