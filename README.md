# AI 语音绘图工具

纯语音控制的绘图工具，支持语音创建、编辑、导出图形。

## 核心功能

- 语音创建图形（矩形、圆形、三角形等）
- 语音指令优化（去除口头禅、补全语句）
- 图形编辑（移动、删除、颜色修改）
- 撤销/重做
- 导出 PNG/SVG

## 技术栈

- 前端：React 18 + TypeScript + Vite
- 后端：Python 3.10+ + FastAPI
- 语音识别：FunASR (paraformer-zh)
- LLM：mimo-v2.5-pro (OpenAI 兼容接口)

## 快速启动

### 环境要求

- Node.js >= 18
- Python >= 3.10
- FunASR 模型（首次运行自动下载，约 1GB）

### 启动步骤

```bash
# 后端
cd backend
pip install -r requirements.txt
export LLM_API_KEY="your-api-key"
export LLM_BASE_URL="your-api-url"
python main.py

# 前端
cd frontend
npm install
npm run dev
```

### 配置说明

| 环境变量 | 说明 | 示例 |
|---|---|---|
| LLM_API_KEY | LLM 服务 API Key | sk-xxx |
| LLM_BASE_URL | LLM 服务地址 | https://api.example.com/v1 |
| ASR_MODEL_PATH | FunASR 模型路径 | 默认自动下载 |

## 依赖列表

### 前端

- react ^18.2.0
- react-dom ^18.2.0
- typescript ^5.0.0
- vite ^5.0.0

### 后端

- fastapi ^0.104.0
- uvicorn ^0.24.0
- funasr ^1.0.0
- httpx ^0.25.0
- websockets ^12.0

## 原创功能说明

本项目的原创部分为"语音指令优化器"，采用规则预处理 + LLM 语义优化的两层架构。其他功能（SVG 渲染、WebSocket 通信等）使用标准技术实现，不涉及第三方代码复用。

## Demo

视频链接：（bilibili 链接，待补充）

## 项目结构

```
AI-voice-draw/
├── frontend/          # React 前端
├── backend/           # Python 后端
├── docs/              # 设计文档
├── README.md
└── .gitignore
```
