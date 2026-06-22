# TextDiff 文本比较工具 - 架构设计文档

## 1. 项目概述

TextDiff 是一个基于 C/S 架构的文本比较工具，支持 JSON 和 YAML 两种格式的文本内容比较。工具能够忽略字段大小写以及同一层次字段的先后顺序，准确展示文件或文本之间的差异。

## 2. 系统架构

```
┌──────────────────────────────────────────────┐
│               前端 (Vue 3)                     │
│  ┌─────────────┐  ┌─────────────┐            │
│  │  左文本面板   │  │  右文本面板  │            │
│  │  (粘贴/上传)  │  │  (粘贴/上传) │            │
│  └──────┬──────┘  └──────┬──────┘            │
│         │                │                    │
│         ▼                ▼                    │
│  ┌────────────────────────────────────┐       │
│  │         Diff 结果展示区              │       │
│  │  (行级差异高亮 + 统计摘要)          │       │
│  └────────────────────────────────────┘       │
│              │         ▲                       │
│              ▼         │                       │
│         ┌──────────┐   │ HTTP POST             │
│         │ API 客户端│───┘ /api/compare          │
│         └──────────┘                           │
└─────────────────────┬────────────────────────-┘
                      │ HTTP JSON
                      ▼
┌──────────────────────────────────────────────┐
│           后端 (Python 3.12 + FastAPI)          │
│  ┌────────────────────────────────────┐       │
│  │         diff_engine.py             │       │
│  │  ┌─────────┐  ┌───────────────┐   │       │
│  │  │ 解析器   │→│  标准化器      │   │       │
│  │  │(JSON/   │  │(小写键+排序)   │   │       │
│  │  │ YAML)   │  └───────┬───────┘   │       │
│  │  └─────────┘          │           │       │
│  │                       ▼           │       │
│  │  ┌─────────┐  ┌───────────────┐   │       │
│  │  │差异映射  │←│  diff 引擎     │   │       │
│  │  │(行号定位)│  │(difflib)      │   │       │
│  │  └─────────┘  └───────────────┘   │       │
│  └────────────────────────────────────┘       │
└──────────────────────────────────────────────┘
```

### 2.1 前后端分离

- **前端**: Vue 3 + Vite，提供纯浏览器端交互
- **后端**: Python 3.12 + FastAPI，提供 RESTful API
- **通信**: HTTP/JSON，通过 POST 请求提交比较任务

## 3. 后端设计

### 3.1 技术选型

| 组件 | 技术 | 说明 |
|------|------|------|
| Web 框架 | FastAPI | 高性能异步 Web 框架 |
| JSON 解析 | 内置 json 模块 | Python 标准库 |
| YAML 解析 | PyYAML | 第三方 YAML 解析库 |
| 差异引擎 | difflib | Python 标准库文本差异比较 |
| CORS | fastapi.middleware.cors | 跨域支持 |

### 3.2 API 接口

**`POST /api/compare`**

请求体：
```json
{
  "left_text": "文本内容 A",
  "right_text": "文本内容 B",
  "format": "json | yaml"
}
```

响应体：
```json
{
  "success": true,
  "has_diff": true,
  "format": "json",
  "left_normalized": "标准化后的左文本",
  "right_normalized": "标准化后的右文本",
  "diff_entries": [
    {
      "type": "equal|modified|added|removed",
      "left_line_num": 1,
      "right_line_num": 1,
      "left_content": "行内容A",
      "right_content": "行内容B"
    }
  ],
  "summary": {
    "modified": 0,
    "added": 0,
    "removed": 0,
    "equal": 0
  }
}
```

**`GET /api/health`**

健康检查接口。

### 3.3 核心处理流程

```
输入文本 A,B
    │
    ▼
┌─────────────┐
│  格式解析    │  JSON → json.loads()
│             │  YAML → yaml.safe_load()
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  标准化处理  │
│  • 键名小写  │  递归处理所有 dict 键
│  • 键排序    │  同层 dict 键按字母排序
│  • 保留值原样│  字符串值不转换大小写
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  序列化输出  │  将标准化对象重新格式化为字符串
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  difflib    │  按行比较标准化后的两个字符串
│  差异比较    │  逐行标记 equal/modified/added/removed
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  结果封装    │  生成结构化的 diff 结果响应
│  并返回     │ 
└─────────────┘
```

### 3.4 标准化规则

字段名标准化：
```python
def normalize(obj):
    if isinstance(obj, dict):
        return {
            k.lower(): normalize(v)
            for k, v in sorted(obj.items(), key=lambda x: x[0].lower())
        }
    elif isinstance(obj, list):
        return [normalize(item) for item in obj]
    else:
        return obj
```

- 所有字典键转为小写
- 同一层级的键按字母排序
- 列表保持原有顺序（列表元素位置重要）
- 字符串值、数值、布尔值等保持不变

## 4. 前端设计

### 4.1 技术选型

| 组件 | 技术 |
|------|------|
| 框架 | Vue 3 (Composition API) |
| 构建工具 | Vite |
| 样式 | 原生 CSS (Flexbox/Grid) |

### 4.2 组件结构

```
App.vue (根组件 - 页面布局)
  └── ComparePanel.vue (核心组件)
        ├── 格式选择器 (JSON/YAML 下拉框)
        ├── 左文本面板 (Textarea + 文件上传)
        ├── 右文本面板 (Textarea + 文件上传)
        ├── 操作按钮 (比较 / 清除)
        └── DiffView.vue (差异展示)
              ├── 左差异面板 (行号 + 内容 + 高亮)
              ├── 右差异面板 (行号 + 内容 + 高亮)
              └── 差异统计摘要
```

### 4.3 交互流程

```
1. 用户选择格式 (JSON/YAML)
2. 用户通过粘贴或文件上传在左右面板输入内容
3. 点击"比较"按钮
4. 前端发送 POST /api/compare 请求
5. 后端处理并返回差异结果
6. 前端渲染差异视图：
   - 绿色背景：新增行
   - 红色背景：删除行
   - 黄色背景：修改行
   - 无背景：相同行
7. 显示差异统计摘要（修改/新增/删除行数）
```

## 5. 项目结构

```
TextDiff/
├── README.md                    # 项目说明
├── docs/
│   └── architecture.md          # 架构设计文档
├── backend/
│   ├── requirements.txt         # Python 依赖
│   ├── main.py                  # FastAPI 服务入口
│   └── diff_engine.py           # 核心差异比较引擎
└── frontend/
    ├── package.json             # NPM 依赖
    ├── vite.config.js           # Vite 打包配置
    ├── index.html               # 入口 HTML
    └── src/
        ├── main.js              # Vue 入口
        ├── App.vue              # 根组件
        ├── api/
        │   └── index.js         # API 客户端
        └── components/
            ├── ComparePanel.vue  # 主比较面板
            └── DiffView.vue     # 差异展示组件
```

## 6. 启动方式

### 6.1 后端启动

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 6.2 前端启动

```bash
cd frontend
npm install
npm run dev
```

打开浏览器访问 `http://localhost:5173`。

## 7. 注意事项

- 前端开发模式下 API 代理到 `http://localhost:8000`
- 生产构建后前端静态文件由 Nginx 或其他 Web 服务器托管
- 后端需要启用 CORS 以允许跨域请求
- 比较的内容必须为同一种格式（JSON 或 YAML）
- 列表/数组的顺序比较不忽略元素顺序（仅字典键排序）
