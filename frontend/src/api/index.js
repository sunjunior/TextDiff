const API_BASE = '/api'

/**
 * 比较两段文本的差异
 * @param {string} leftText - 左文本
 * @param {string} rightText - 右文本
 * @param {'json'|'yaml'} format - 文本格式
 * @returns {Promise<object>} 比较结果
 */
export async function compareTexts(leftText, rightText, format) {
  const response = await fetch(`${API_BASE}/compare`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      left_text: leftText,
      right_text: rightText,
      format: format,
    }),
  })

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw new Error(errorData.detail || `请求失败 (${response.status})`)
  }

  return response.json()
}

/**
 * 健康检查
 * @returns {Promise<object>}
 */
export async function healthCheck() {
  const response = await fetch(`${API_BASE}/health`)
  return response.json()
}
