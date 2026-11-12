import axios from 'axios'
import { showToast } from 'vant'

// 从 .env 读取 baseURL（VITE_API_BASE_URL=http://localhost:8000/api）
// 默认同源 /api：手机通过局域网 IP 访问时，请求打到页面自身的服务器
// （再由 dev/preview 的 proxy 转发到后端），而不是手机自己的 localhost，
// 否则手机端所有 AI 接口都会失败。
const baseURL = import.meta.env.VITE_API_BASE_URL || '/api'

const request = axios.create({
  baseURL,
  timeout: 45000, // 45s：云托管缩容冷启动（10-30s）+ 大模型响应都要时间
})

// 请求拦截器：可加 token
request.interceptors.request.use(
  (config) => config,
  (error) => Promise.reject(error)
)

// 响应拦截器：统一处理错误
// 请求 config 里传 silent: true 可跳过全局错误 Toast（调用方自行降级处理，
// 例如 TTS 失败会静默降级到浏览器语音，弹错误提示反而吓到老人）
request.interceptors.response.use(
  (response) => response.data,
  async (error) => {
    const config = error.config || {}

    // 一次性自动重试：云托管（min instance=0）空闲缩容后，第一个请求常被网关
    // 以 503 拒绝（此时实例正在拉起）。重试一次通常就能成功，老人不必再点一遍。
    // 只对「服务端 5xx」或「完全无响应」重试，且每条请求最多重试一次。
    const status = error.response?.status
    const retryable = !status || status >= 500 || status === 503
    if (retryable && !config._retried && !config.silent) {
      config._retried = true
      await new Promise((r) => setTimeout(r, 2000))
      try {
        return await request.request(config)
      } catch {
        /* 重试失败走下面统一错误提示 */
      }
    }

    if (!config.silent) {
      if (error.code === 'ECONNABORTED') {
        showToast('请求超时，请检查网络')
      } else if (!error.response) {
        showToast('网络异常，请稍后重试')
      } else {
        const msg = error.response.data?.detail || error.response.data?.message || `请求失败 ${error.response.status}`
        showToast(msg)
      }
    }
    return Promise.reject(error)
  }
)

export default request
