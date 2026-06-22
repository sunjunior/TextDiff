<template>
  <div class="diff-view">
    <!-- 差异统计摘要 -->
    <div class="diff-summary" :class="{ 'no-diff': !diffData.has_diff }">
      <div class="summary-left">
        <strong>比较结果：</strong>
        <span v-if="!diffData.has_diff" class="badge badge-equal">完全一致</span>
        <template v-else>
          <span class="badge badge-modified">{{ diffData.summary.modified }} 处修改</span>
          <span class="badge badge-added">{{ diffData.summary.added }} 处新增</span>
          <span class="badge badge-removed">{{ diffData.summary.removed }} 处删除</span>
        </template>
      </div>
      <div class="summary-right">
        <span class="badge badge-info">{{ format.toUpperCase() }}</span>
        <button class="btn btn-back" @click="$emit('back')">返回编辑</button>
      </div>
    </div>

    <!-- 差异展示面板 -->
    <div class="diff-panels">
      <!-- 左侧差异 -->
      <div class="diff-side diff-left">
        <div class="diff-header">左侧文本</div>
        <div class="diff-content">
          <table class="diff-table">
            <tbody>
              <tr
                v-for="(entry, idx) in leftDisplayLines"
                :key="'l-' + idx"
                :class="['diff-line', 'line-' + entry.type]"
              >
                <td class="line-num">{{ entry.lineNum || '' }}</td>
                <td class="line-marker">{{ markerSymbol(entry.type) }}</td>
                <td class="line-content">
                  <span v-if="entry.type === 'empty'">&nbsp;</span>
                  <span v-else>{{ entry.content }}</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- 右侧差异 -->
      <div class="diff-side diff-right">
        <div class="diff-header">右侧文本</div>
        <div class="diff-content">
          <table class="diff-table">
            <tbody>
              <tr
                v-for="(entry, idx) in rightDisplayLines"
                :key="'r-' + idx"
                :class="['diff-line', 'line-' + entry.type]"
              >
                <td class="line-num">{{ entry.lineNum || '' }}</td>
                <td class="line-marker">{{ markerSymbol(entry.type) }}</td>
                <td class="line-content">
                  <span v-if="entry.type === 'empty'">&nbsp;</span>
                  <span v-else>{{ entry.content }}</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- 标准化文本折叠区 -->
    <div class="normalized-section">
      <button class="toggle-btn" @click="showNormalized = !showNormalized">
        {{ showNormalized ? '收起' : '展开' }}标准化后文本
        <span class="toggle-icon">{{ showNormalized ? '▲' : '▼' }}</span>
      </button>
      <div v-if="showNormalized" class="normalized-panels">
        <div class="normalized-panel">
          <div class="normalized-header">标准化左侧</div>
          <pre class="normalized-content"><code>{{ diffData.left_normalized }}</code></pre>
        </div>
        <div class="normalized-panel">
          <div class="normalized-header">标准化右侧</div>
          <pre class="normalized-content"><code>{{ diffData.right_normalized }}</code></pre>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  diffData: { type: Object, required: true },
  format: { type: String, required: true },
})

defineEmits(['back'])

const showNormalized = ref(false)

/** 生成左侧显示行（包含空白占位行） */
const leftDisplayLines = computed(() => {
  const entries = props.diffData.diff_entries || []
  const lines = []
  for (const entry of entries) {
    if (entry.type === 'added') {
      // 右侧新增，左侧对应空行
      lines.push({ type: 'empty', lineNum: null, content: '' })
    } else {
      lines.push({
        type: entry.type === 'equal' ? 'equal' : entry.type === 'removed' ? 'removed' : 'modified',
        lineNum: entry.left_line_num,
        content: entry.left_content,
      })
    }
  }
  return lines
})

/** 生成右侧显示行（包含空白占位行） */
const rightDisplayLines = computed(() => {
  const entries = props.diffData.diff_entries || []
  const lines = []
  for (const entry of entries) {
    if (entry.type === 'removed') {
      // 左侧删除，右侧对应空行
      lines.push({ type: 'empty', lineNum: null, content: '' })
    } else {
      lines.push({
        type: entry.type === 'equal' ? 'equal' : entry.type === 'added' ? 'added' : 'modified',
        lineNum: entry.right_line_num,
        content: entry.right_content,
      })
    }
  }
  return lines
})

/** 行标记符号 */
function markerSymbol(type) {
  switch (type) {
    case 'added': return '+'
    case 'removed': return '-'
    case 'modified': return '~'
    case 'empty': return ' '
    default: return ' '
  }
}
</script>

<style scoped>
.diff-view {
  margin-top: 8px;
}

/* 差异统计摘要 */
.diff-summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f8f9fa;
  border: 1px solid #d0d5dd;
  border-radius: 8px;
  margin-bottom: 16px;
}

.diff-summary.no-diff {
  background: #f0fdf4;
  border-color: #bbf7d0;
}

.summary-left {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
}

.summary-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.badge {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.badge-equal { background: #dcfce7; color: #166534; }
.badge-modified { background: #fef9c3; color: #854d0e; }
.badge-added { background: #dcfce7; color: #166534; }
.badge-removed { background: #fee2e2; color: #991b1b; }
.badge-info { background: #dbeafe; color: #1e40af; }

.btn-back {
  padding: 6px 16px;
  background: white;
  border: 1px solid #d0d5dd;
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
  color: #555;
  transition: all 0.2s;
}

.btn-back:hover {
  background: #f0f2f5;
  border-color: #b0b5bd;
}

/* 差异面板 */
.diff-panels {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 16px;
}

.diff-side {
  border: 1px solid #d0d5dd;
  border-radius: 8px;
  overflow: hidden;
  background: white;
}

.diff-header {
  padding: 8px 16px;
  background: #f8f9fa;
  border-bottom: 1px solid #e8eaed;
  font-size: 13px;
  font-weight: 600;
  color: #555;
}

.diff-content {
  overflow-x: auto;
  max-height: 600px;
  overflow-y: auto;
}

.diff-table {
  width: 100%;
  border-collapse: collapse;
  font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
  font-size: 13px;
  line-height: 1.6;
}

.diff-line {
  border-bottom: 1px solid #f0f0f0;
}

.diff-line.line-equal { background: white; }
.diff-line.line-modified { background: #fef9c3; }
.diff-line.line-added { background: #dcfce7; }
.diff-line.line-removed { background: #fee2e2; }
.diff-line.line-empty { background: #f9fafb; color: #d0d5dd; }

.line-num {
  width: 48px;
  padding: 0 8px;
  text-align: right;
  color: #b0b5bd;
  font-size: 12px;
  user-select: none;
  border-right: 1px solid #e8eaed;
}

.line-marker {
  width: 24px;
  padding: 0 4px;
  text-align: center;
  color: #999;
  font-weight: bold;
  font-size: 12px;
  user-select: none;
}

.line-content {
  padding: 0 12px;
  white-space: pre;
  word-break: break-all;
}

/* 标准化文本折叠 */
.normalized-section {
  margin-bottom: 16px;
}

.toggle-btn {
  width: 100%;
  padding: 10px 16px;
  background: #f8f9fa;
  border: 1px solid #d0d5dd;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  color: #555;
  text-align: left;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: background 0.2s;
}

.toggle-btn:hover {
  background: #f0f2f5;
}

.toggle-icon {
  font-size: 12px;
}

.normalized-panels {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-top: 12px;
}

.normalized-panel {
  border: 1px solid #d0d5dd;
  border-radius: 6px;
  overflow: hidden;
}

.normalized-header {
  padding: 6px 12px;
  background: #f0f4f9;
  font-size: 12px;
  font-weight: 600;
  color: #666;
  border-bottom: 1px solid #d0d5dd;
}

.normalized-content {
  padding: 12px;
  margin: 0;
  font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
  font-size: 13px;
  line-height: 1.6;
  background: #fafcff;
  overflow-x: auto;
  max-height: 400px;
  overflow-y: auto;
  white-space: pre;
}

/* 响应式 */
@media (max-width: 768px) {
  .diff-panels {
    grid-template-columns: 1fr;
  }
  .normalized-panels {
    grid-template-columns: 1fr;
  }
}
</style>
