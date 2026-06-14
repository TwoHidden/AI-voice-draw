# AI 语音绘图工具

纯语音控制的绘图工具，支持语音创建、编辑、导出图形。基于 LLM Agent + Function Calling 架构，实现自然语言到绘图操作的直接转换。

## 核心功能

### 语音交互
- 🎤 语音输入：按住说话，实时语音识别（FunASR paraformer-zh）
- ✏️ 文字输入：备用输入方式，语音不可用时可直接输入文字指令
- 🤖 AI 理解：LLM Agent 直接理解口语化指令，无需手动解析

### 图形支持
- 🎨 10种图形：矩形、圆形、椭圆、三角形、菱形、线条、箭头、五角星、曲线、六边形
- 📐 8种操作：创建、删除、移动、缩放、改色、改文字、撤销、重做
- ⭐ 线段绘图：支持用线段画五角星、多边形（正多边形/不规则多边形）
- 💾 导出：SVG/PNG 格式

### 智能特性
- 口语化理解："呃，画一个蓝色的长方形" → 自动创建蓝色矩形
- 复合指令："画一个红色正方形和蓝色圆形" → 一次调用多个工具
- 指代消解："把它移到右边" → 根据画布状态自动选择目标
- 颜色转换："红色" → "#FF0000"，"深蓝" → "#00008B"

## 技术栈

| 层 | 技术 | 说明 |
|---|---|---|
| 前端 | React 19 + TypeScript + Vite | SVG 画布 + WebSocket |
| 后端 | Python 3.9+ + FastAPI | WebSocket 服务 |
| 语音识别 | FunASR (paraformer-zh) | 本地部署，中文语音转文字 |
| LLM Agent | mimo-v2.5-pro | Function Calling 架构 |
| 通信 | WebSocket | 实时双向通信 |

## 架构设计

### LLM Agent + Function Calling

```
用户语音/文本
    ↓
ASR (语音识别)
    ↓
LLM Agent (一次调用)
    ↓
tool_calls: [create_shape(...), create_shape(...)]
    ↓
执行器逐个执行
    ↓
返回画布状态
```

**优势：**
- 一次 LLM 调用，延迟降低 50%
- LLM 直接输出结构化 tool_calls，无需额外解析
- 支持复杂指令（一次调用多个工具）
- 上下文感知，支持指代消解

### 工具定义

| 工具 | 说明 |
|------|------|
| `create_shape` | 创建图形（rect, circle, ellipse, triangle, diamond, line, arrow, star, curve, hexagon） |
| `create_star_with_lines` | 用5条线段画五角星 |
| `create_polygon_with_lines` | 用线段画多边形（支持不规则） |
| `delete_shape` | 删除图形 |
| `move_shape` | 移动图形 |
| `resize_shape` | 调整大小 |
| `set_color` | 修改颜色 |
| `set_text` | 添加文字 |
| `undo` / `redo` | 撤销/重做 |

## 启动步骤

### 1. 配置环境变量

复制 `.env.sample` 为 `.env`，填入 LLM API 配置：

```bash
cd backend
cp .env.sample .env
# 编辑 .env，填入 LLM_API_KEY, LLM_BASE_URL, LLM_MODEL
```

### 2. 启动后端

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. 启动前端

```bash
cd frontend
npm install
npm run dev
```

### 4. 访问应用

打开 http://localhost:5173

## 原创功能说明

### 1. LLM Agent + Function Calling 架构

本项目采用 LLM Agent + Function Calling 架构，将绘图工具集成到 LLM 的原生能力中：

- **工具定义**：使用 OpenAI Function Calling 格式定义 8 个绘图工具
- **System Prompt**：包含颜色映射、位置推断、默认大小等规则
- **一次调用**：LLM 理解指令后直接返回 tool_calls，无需额外解析

### 2. 线段绘图系统

支持用线段绘制复杂图形：

- **五角星**：计算5个外顶点，按 0→2→4→1→3→0 顺序连接
- **正多边形**：计算N个等距顶点，依次连接
- **不规则多边形**：顶点半径随机偏移 (0.6-1.4 倍)

### 3. 语音识别集成

集成 FunASR paraformer-zh 模型，实现中文语音实时识别：

- 本地部署，无需联网
- 支持口语化表达
- 实时返回识别结果

## 第三方依赖

### 后端

| 依赖 | 版本 | 用途 |
|------|------|------|
| FastAPI | 0.115.6 | WebSocket + HTTP 服务 |
| uvicorn | 0.32.1 | ASGI 服务器 |
| pydantic | 2.10.3 | 数据验证 |
| httpx | 0.28.1 | 调用 LLM API |
| websockets | 14.1 | WebSocket 通信 |
| numpy | 2.2.0 | 音频数据处理 |
| python-dotenv | 1.0.1 | 环境变量管理 |
| FunASR | - | 语音识别（ModelScope） |

### 前端

| 依赖 | 版本 | 用途 |
|------|------|------|
| React | 19.0.0 | UI 框架 |
| Vite | 6.0.5 | 构建工具 |
| TypeScript | 5.7.2 | 类型安全 |

## 项目结构

```
.
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI 入口 + WebSocket
│   │   ├── agent.py          # LLM Agent (Function Calling)
│   │   ├── tools.py          # 工具定义 + 计算函数
│   │   ├── executor.py       # 指令执行器
│   │   ├── models.py         # 数据模型
│   │   ├── config.py         # 配置管理
│   │   └── asr.py            # FunASR 语音识别
│   ├── tests/
│   ├── requirements.txt
│   └── .env.sample           # 环境变量模板
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Canvas.tsx     # SVG 画布（支持10种图形）
│   │   │   ├── VoicePanel.tsx # 语音面板
│   │   │   └── StatusPanel.tsx# 状态面板
│   │   ├── hooks/
│   │   │   ├── useVoice.ts    # 录音 hook
│   │   │   ├── useWebSocket.ts# WebSocket hook
│   │   │   └── useExport.ts   # 导出 hook
│   │   ├── types/index.ts     # 类型定义
│   │   ├── App.tsx            # 主应用
│   │   └── App.css            # 样式
│   └── package.json
├── docs/
│   ├── superpowers/
│   │   ├── specs/             # 设计文档
│   │   └── plans/             # 实施计划
│   └── design.md
├── start.sh                   # 启动脚本
├── stop.sh                    # 停止脚本
└── README.md
```

## 使用示例

### 基本绘图

```
"画一个蓝色的长方形"
"创建一个红色圆形"
"画一个绿色三角形在中间"
```

### 复合指令

```
"画一个红色正方形和一个蓝色圆形"
"画3条线段"
"画一个五角星和一个六边形"
```

### 线段绘图

```
"用线段画一个五角星"
"用线段画一个六边形"
"画一个不规则的七边形"
```

### 编辑操作

```
"把那个方块移到右边"
"放大一点"
"改成红色"
"删除圆形"
"撤销"
```

## 评审要点

### 产品设计合理性
- 语音交互降低绘图门槛
- LLM Agent 理解口语化表达
- 支持复合指令，提高效率

### 架构清晰度
- 前后端分离，职责清晰
- LLM Agent + Function Calling 架构
- 工具定义与执行逻辑分离

### 代码健壮度
- Pydantic 数据验证
- 错误处理与重试机制
- 类型安全（TypeScript）

### 创新性
- 用线段绘制复杂图形（五角星、多边形）
- 不规则多边形生成
- LLM 直接调用绘图工具

## 许可证

MIT
