/**
 * 轻量 Markdown 渲染（安全版）
 *
 * DeepSeek 回答常用 **加粗**、编号列表、短横列表，直接 {{ }} 输出
 * 会把星号原样显示给老人。这里先整体 HTML 转义再替换安全标签，
 * 不引入任何第三方库，杜绝 XSS。
 */
export function mdToHtml(md = '') {
  let html = String(md)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')

  html = html.replace(/\*\*([^*\n]+)\*\*/g, '<strong>$1</strong>')
  html = html.replace(/`([^`\n]+)`/g, '<code>$1</code>')

  const lines = html.split('\n')
  const out = []
  let listOpen = false
  for (const line of lines) {
    const ol = line.match(/^\s*(\d+)[.、)）]\s*(.+)$/)
    const ul = line.match(/^\s*[-•·]\s+(.+)$/)
    if (ol || ul) {
      if (!listOpen) {
        out.push(ol ? '<ol>' : '<ul>')
        listOpen = true
      }
      out.push(`<li>${ol ? ol[2] : ul[1]}</li>`)
    } else {
      if (listOpen) {
        out.push('</ul>')
        listOpen = false
      }
      out.push(line)
    }
  }
  if (listOpen) out.push('</ul>')
  return out.join('\n')
}
