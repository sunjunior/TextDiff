<template>
  <div class="app">
    <!-- 顶部标题 -->
    <header class="app-header">
      <div class="header-content">
        <h1 class="app-title">
          <span class="title-icon">⟷</span>
          TextDiff
          <span class="title-sub">文本比较工具</span>
        </h1>
        <p class="app-desc">
          支持 JSON / YAML 格式，自动忽略字段大小写和同层顺序差异
        </p>
      </div>
    </header>

    <!-- 主内容区 -->
    <main class="app-main">
      <ComparePanel />
    </main>

    <!-- 底部 -->
    <footer class="app-footer">
      <p>TextDiff v1.0 &mdash; Vue 3 + Python FastAPI</p>
    </footer>
  </div>
</template>

<script setup>
import ComparePanel from './components/ComparePanel.vue'
</script>

<style>
/* 全局样式 */
:root {
  --color-bg: #f5f7fa;
  --color-header-bg: #1a2332;
  --color-header-text: #ffffff;
  --color-primary: #4a90d9;
  --color-text: #333;
  --color-text-light: #888;
  --color-border: #d0d5dd;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, 'Noto Sans SC', sans-serif;
  background: var(--color-bg);
  color: var(--color-text);
  min-height: 100vh;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: #c1c5cb;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a0a5ab;
}
</style>

<style scoped>
.app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

/* 顶部 */
.app-header {
  background: var(--color-header-bg);
  padding: 24px 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 20px;
}

.app-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--color-header-text);
  display: flex;
  align-items: center;
  gap: 8px;
}

.title-icon {
  font-size: 24px;
  opacity: 0.8;
}

.title-sub {
  font-size: 16px;
  font-weight: 400;
  opacity: 0.7;
  margin-left: 4px;
}

.app-desc {
  margin-top: 6px;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
}

/* 主内容 */
.app-main {
  flex: 1;
  padding: 0;
}

/* 底部 */
.app-footer {
  text-align: center;
  padding: 16px;
  color: var(--color-text-light);
  font-size: 12px;
  border-top: 1px solid var(--color-border);
  background: white;
}
</style>
