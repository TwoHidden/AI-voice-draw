# AI 语音绘图工具

纯语音控制的绘图工具，支持语音创建、编辑、导出图形。

## 核心功能

- 🎤 语音输入：按住说话，实时语音识别
- ✏️ 文本输入：文字指令回退
- 🎨 7种图形：矩形、圆形、椭圆、三角形、菱形、线条、箭头
- 📐 8种操作：创建、删除、移动、缩放、改色、改文字、撤销、重做
- 💾 导出：SVG/PNG 格式

## 技术栈

| 层 | 技术 | 版本 |
|---|---|---|
| 前端 | React 19 + TypeScript + Vite | 19.x |
| 后端 | Python + FastAPI | 0.115.6 |
| 语音识别 | FunASR (paraformer-zh) | 本地部署 |
| LLM | mimo-v2.5-pro (OpenAI 兼容) | API |
| 通信 | WebSocket | - |

## 启动步骤

### 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `LLM_API_KEY` | LLM API 密钥 | 必填 |
| `LLM_BASE_URL` | LLM API 地址 | `https://api.example.com/v1` |
| `LLM_MODEL` | LLM 模型名 | `mimo-v2.5-pro` |
| `DEBUG` | 调试模式 | `false` |
| `PORT` | 服务端口 | `8000` |

### 后端

```bash
cd backend
pip install -r requirements.txt
export LLM_API_KEY="your-api-key"
export LLM_BASE_URL="your-api-url"
python -m app.main
```

### 前端

```bash
cd frontend
npm install
npm run dev
```

## 原创功能说明

本项目的原创部分为"语音指令优化器"，采用规则预处理 + LLM 语义优化的两层架构：

1. **规则预处理层**：去除填充词、口语化映射、形状名标准化、颜色标准化
2. **LLM 语义优化层**：调用大模型理解复杂语义，输出简洁指令

## 第三方依赖

| 依赖 | 原始功能 | 用途 |
|---|---|---|
| FastAPI | Web 框架 | WebSocket + HTTP 服务 |
| uvicorn | ASGI 服务器 | 运行 FastAPI |
| pydantic | 数据验证 | 定义数据模型 |
| httpx | HTTP 客户端 | 调用 LLM API |
| websockets | WebSocket 库 | 实时通信 |
| numpy | 数值计算 | 音频数据处理 |
| FunASR | 语音识别 | 中文语音转文字 |
| React | UI 框架 | 前端界面 |
| Vite | 构建工具 | 前端开发和构建 |

## 项目结构

```
.
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI 入口 + WebSocket
│   │   ├── config.py         # 配置管理
│   │   ├── models.py         # 数据模型
│   │   ├── executor.py       # 指令执行器
│   │   ├── optimizer.py      # 语音指令优化器
│   │   ├── parser.py         # LLM 指令解析器
│   │   └── asr.py            # FunASR 语音识别
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Canvas.tsx     # SVG 画布
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
└── docs/
    └── design.md              # 设计文档
```
