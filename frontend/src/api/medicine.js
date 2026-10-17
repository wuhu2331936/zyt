import request from './request'

/**
 * 拍照识药
 * @param {File} file - 图片文件（来自 <van-uploader> 或 <input type="file">）
 */
export function recognizeMedicine(file) {
  const fd = new FormData()
  fd.append('file', file)
  return request.post('/medicine/recognize', fd, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

/**
 * 按药名补全详细用药说明（手动添加的药品也能用）
 */
export function enrichMedicine({ name, spec, manufacturer }) {
  return request.post('/medicine/enrich', { name, spec, manufacturer })
}

/**
 * 检查药物相互作用
 * @param {string[]} medicines - 药品通用名列表
 */
export function checkInteractions(medicines) {
  return request.post('/interaction/check', { medicines })
}