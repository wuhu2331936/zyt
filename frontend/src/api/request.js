import axios from 'axios'
import { showToast } from 'vant'

// 从 .env 读取 baseURL（VITE_API_BASE_URL=http://localhost:8000/api）
const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

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
request.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.code === 'ECONNABORTED') {
      showToast('请求超时，请检查网络')
    } else if (!error.response) {
      showToast('网络异常，请稍后重试')
    } else {
      const msg = error.response.data?.detail || error.response.data?.message || `请求失败 ${error.response.status}`
      showToast(msg)
    }
    return Promise.reject(error)
  }
)

export default request