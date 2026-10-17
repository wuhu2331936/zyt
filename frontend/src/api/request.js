import axios from 'axios'
import { showToast } from 'vant'

// 从 .env 读取 baseURL（VITE_API_BASE_URL=http://localhost:8000/api）
// 默认同源 /api：手机通过局域网 IP 访问时，请求打到页面自身的服务器
// （再由 dev/preview 的 proxy 转发到后端），而不是手机自己的 localhost，
// 否则手机端所有 AI 接口都会失败。
const baseURL = import.meta.env.VITE_API_BASE_URL || '/api'

const request = axios.create({
  baseURL,
  timeout: 30000, // 30s（大模型调用可能稍慢）
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
  (error) => {
    if (!error.config?.silent) {
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