<template>
  <div class="compare-panel">
    <!-- 格式选择 -->
    <div class="toolbar">
      <div class="format-selector">
        <label for="format-select">格式类型：</label>
        <select id="format-select" v-model="format" @change="resetAll">
          <option value="json">JSON</option>
          <option value="yaml">YAML</option>
        </select>
      </div>
      <div class="actions">
        <button class="btn btn-compare" @click="handleCompare" :disabled="comparing || !leftText.trim() || !rightText.trim()">
          {{ comparing ? '比较中...' : '开始比较' }}
        </button>
        <button class="btn btn-clear" @click="resetAll">清除</button>
      </div>
    </div>

    <!-- 文本输入面板 -->
    <div class="panels">
      <!-- 左面板 -->
      <div class="panel panel-left">
        <div class="panel-header">
          <span class="panel-title">左侧文本</span>
          <label class="upload-btn">
            上传文件
            <input type="file" accept=".json,.yaml,.yml" @change="handleFileUpload($event, 'left')" />
          </label>
        </div>
        <div class="panel-body">
          <textarea
            ref="leftTextarea"
            v-model="leftText"
            placeholder="在此粘贴或上传左侧文本内容..."
            :disabled="hasResult"
            spellcheck="false"
          ></textarea>
        </div>
      </div>

      <!-- 右面板 -->
      <div class="panel panel-right">
        <div class="panel-header">
          <span class="panel-title">右侧文本</span>
          <label class="upload-btn">
            上传文件
            <input type="file" accept=".json,.yaml,.yml" @change="handleFileUpload($event, 'right')" />
          </label>
        </div>
        <div class="panel-body">
          <textarea
            ref="rightTextarea"
            v-model="rightText"
            placeholder="在此粘贴或上传右侧文本内容..."
            :disabled="hasResult"
            spellcheck="false"
          ></textarea>
        </div>
      </div>
    </div>

    <!-- 错误提示 -->
    <div v-if="error" class="error-message">
      <span class="error-icon">⚠</span>
      {{ error }}
    </div>

    <!-- 比较结果 -->
    <DiffView
      v-if="hasResult"
      :diff-data="diffData"
      :format="format"
      @back="backToEdit"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { compareTexts } from '../api/index.js'
import DiffView from './DiffView.vue'

const format = ref('json')
const leftText = ref('')
const rightText = ref('')
const comparing = ref(false)
const error = ref('')
const diffData = ref(null)
const hasResult = ref(false)

const leftTextarea = ref(null)
const rightTextarea = ref(null)

/** 处理文件上传 */
function handleFileUpload(event, side) {
  const file = event.target.files[0]
  if (!file) return

  const reader = new FileReader()
  reader.onload = (e) => {
    const content = e.target.result
    // 根据文件扩展名自动检测格式
    const ext = file.name.split('.').pop().toLowerCase()
    if (ext === 'yaml' || ext === 'yml') {
      format.value = 'yaml'
    } else if (ext === 'json') {
      format.value = 'json'
    }

    if (side === 'left') {
      leftText.value = content
    } else {
      rightText.value = content
    }
    error.value = ''
    hasResult.value = false
    diffData.value = null
  }
  reader.onerror = () => {
    error.value = '文件读取失败'
  }
  reader.readAsText(file)

  // 重置 input 以允许重复选择同一文件
  event.target.value = ''
}

/** 执行比较 */
async function handleCompare() {
  if (!leftText.value.trim() || !rightText.value.trim()) {
    error.value = '请先在左右两侧输入待比较的文本'
    return
  }

  comparing.value = true
  error.value = ''
  hasResult.value = false
  diffData.value = null

  try {
    const result = await compareTexts(leftText.value, rightText.value, format.value)
    diffData.value = result
    hasResult.value = true
  } catch (err) {
    error.value = err.message || '比较请求失败，请检查后端服务是否运行'
  } finally {
    comparing.value = false
  }
}

/** 返回编辑状态 */
function backToEdit() {
  hasResult.value = false
  diffData.value = null
  error.value = ''
}

/** 重置所有内容 */
function resetAll() {
  leftText.value = ''
  rightText.value = ''
  error.value = ''
  hasResult.value = false
  diffData.value = null
}
</script>

<style scoped>
.compare-panel {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

/* 工具栏 */
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  gap: 16px;
  flex-wrap: wrap;
}

.format-selector {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  color: #555;
}

.format-selector select {
  padding: 8px 16px;
  border: 1px solid #d0d5dd;
  border-radius: 6px;
  font-size: 14px;
  background: white;
  color: #333;
  cursor: pointer;
  outline: none;
  transition: border-color 0.2s;
}

.format-selector select:focus {
  border-color: #4a90d9;
  box-shadow: 0 0 0 3px rgba(74, 144, 217, 0.1);
}

.actions {
  display: flex;
  gap: 10px;
}

.btn {
  padding: 10px 24px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-compare {
  background: #4a90d9;
  color: white;
}

.btn-compare:hover:not(:disabled) {
  background: #357abd;
}

.btn-clear {
  background: #e8eaed;
  color: #555;
}

.btn-clear:hover {
  background: #d2d5d9;
}

/* 面板区 */
.panels {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 16px;
}

.panel {
  display: flex;
  flex-direction: column;
  border: 1px solid #d0d5dd;
  border-radius: 8px;
  background: white;
  overflow: hidden;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 16px;
  background: #f8f9fa;
  border-bottom: 1px solid #e8eaed;
}

.panel-title {
  font-weight: 600;
  font-size: 14px;
  color: #333;
}

.upload-btn {
  padding: 5px 12px;
  background: white;
  border: 1px solid #d0d5dd;
  border-radius: 4px;
  font-size: 12px;
  color: #555;
  cursor: pointer;
  transition: all 0.2s;
}

.upload-btn:hover {
  background: #f0f2f5;
  border-color: #b0b5bd;
}

.upload-btn input {
  display: none;
}

.panel-body {
  flex: 1;
}

.panel-body textarea {
  width: 100%;
  height: 400px;
  padding: 16px;
  border: none;
  outline: none;
  font-family: 'SF Mono', 'Fira Code', 'Fira Mono', 'Roboto Mono', 'Consolas', monospace;
  font-size: 13px;
  line-height: 1.6;
  resize: vertical;
  color: #333;
  background: white;
  tab-size: 2;
}

.panel-body textarea:focus {
  background: #fafcff;
}

.panel-body textarea::placeholder {
  color: #b0b5bd;
}

/* 错误消息 */
.error-message {
  margin-bottom: 16px;
  padding: 12px 16px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 6px;
  color: #dc2626;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.error-icon {
  font-size: 16px;
}

/* 响应式 */
@media (max-width: 768px) {
  .panels {
    grid-template-columns: 1fr;
  }
}
</style>
