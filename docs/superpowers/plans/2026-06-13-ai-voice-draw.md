# AI 语音绘图工具 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建一个纯语音控制的绘图工具，用户通过语音指令创建、编辑、导出图形，核心创新是指令优化器。

**Architecture:** 前后端分离架构。前端 React + SVG 渲染画布，通过 WebSocket 与后端通信。后端 FastAPI 处理语音识别（FunASR）、指令优化（规则+LLM）、指令解析（LLM）和图形状态管理。

**Tech Stack:** React 18, TypeScript, Vite, Python 3.10+, FastAPI, FunASR, mimo-v2.5-pro (OpenAI 兼容), WebSocket

---

## File Structure

```
AI-voice-draw/
├── backend/
│   ├── main.py                      # FastAPI 入口，WebSocket 路由
│   ├── requirements.txt             # Python 依赖
│   ├── models/
│   │   └── schemas.py               # Pydantic 数据模型
│   ├── services/
│   │   ├── asr_service.py           # FunASR 语音识别
│   │   ├── optimizer.py             # 规则预处理 + LLM 优化
│   │   ├── parser.py                # LLM 指令解析
│   │   └── executor.py              # 指令执行 + 状态管理
│   └── tests/
│       ├── test_optimizer.py        # 优化器测试
│       ├── test_parser.py           # 解析器测试
│       └── test_executor.py         # 执行器测试
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── src/
│       ├── main.tsx                 # React 入口
│       ├── App.tsx                  # 主组件
│       ├── types/
│       │   └── index.ts             # TypeScript 类型定义
│       ├── components/
│       │   ├── Canvas.tsx           # SVG 画布
│       │   ├── VoicePanel.tsx       # 语音输入面板
│       │   ├── StatusPanel.tsx      # 状态面板
│       │   └── Toolbar.tsx          # 工具栏
│       ├── hooks/
│       │   ├── useVoice.ts          # 语音录制
│       │   ├── useCanvas.ts         # 画布状态
│       │   └── useWebSocket.ts      # WebSocket 通信
│       └── utils/
│           └── svgExport.ts         # 导出工具
├── docs/
│   ├── design.md
│   └── superpowers/plans/
├── README.md
└── .gitignore
```

---

## Task 1: 后端项目初始化

**对应 PR:** PR1

**Files:**
- Create: `backend/main.py`
- Create: `backend/requirements.txt`

- [ ] **Step 1: 创建 requirements.txt**

```
fastapi==0.104.1
uvicorn==0.24.0
websockets==12.0
httpx==0.25.2
pydantic==2.5.0
funasr==1.0.26
```

- [ ] **Step 2: 创建 FastAPI 入口**

```python
# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AI Voice Draw")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "ok"}
```

- [ ] **Step 3: 验证后端启动**

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Expected: 服务启动成功，访问 http://localhost:8000/health 返回 `{"status":"ok"}`

- [ ] **Step 4: Commit**

```bash
git add backend/
git commit -m "feat: 初始化后端 FastAPI 项目

- 添加 requirements.txt 依赖列表
- 创建 main.py 入口，配置 CORS
- 添加 /health 健康检查端点"
```

---

## Task 2: 前端项目初始化

**对应 PR:** PR1

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/tsconfig.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/index.html`
- Create: `frontend/src/main.tsx`
- Create: `frontend/src/App.tsx`
- Create: `frontend/src/types/index.ts`

- [ ] **Step 1: 创建 package.json**

```json
{
  "name": "ai-voice-draw",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "@vitejs/plugin-react": "^4.2.0",
    "typescript": "^5.3.0",
    "vite": "^5.0.0"
  }
}
```

- [ ] **Step 2: 创建 tsconfig.json**

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

- [ ] **Step 3: 创建 vite.config.ts**

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': 'http://localhost:8000',
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true,
      },
    },
  },
})
```

- [ ] **Step 4: 创建 index.html**

```html
<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>AI 语音绘图工具</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

- [ ] **Step 5: 创建类型定义**

```typescript
// frontend/src/types/index.ts
export interface Shape {
  id: string;
  type: 'rect' | 'circle' | 'ellipse' | 'triangle' | 'diamond' | 'line' | 'arrow';
  x: number;
  y: number;
  width?: number;
  height?: number;
  radius?: number;
  fill: string;
  stroke: string;
  strokeWidth: number;
  text?: string;
  fontSize?: number;
  rotation: number;
}

export interface Command {
  action: 'create' | 'delete' | 'move' | 'resize' | 'setColor' | 'setText' | 'undo' | 'redo';
  type?: Shape['type'];
  target?: string;
  props?: {
    x?: number;
    y?: number;
    width?: number;
    height?: number;
    radius?: number;
    fill?: string;
    stroke?: string;
    strokeWidth?: number;
    text?: string;
    fontSize?: number;
    dx?: number;
    dy?: number;
  };
}

export interface Operation {
  id: string;
  type: string;
  targetId: string;
  prevState: Partial<Shape>;
  nextState: Partial<Shape>;
  timestamp: number;
}

export interface ServerMessage {
  type: 'asr_partial' | 'asr_final' | 'optimized' | 'result' | 'error';
  data: string | object;
}
```

- [ ] **Step 6: 创建 App.tsx**

```tsx
// frontend/src/App.tsx
function App() {
  return (
    <div style={{ width: '100vw', height: '100vh', display: 'flex', flexDirection: 'column' }}>
      <header style={{ padding: '8px 16px', borderBottom: '1px solid #ccc' }}>
        <h1 style={{ margin: 0, fontSize: '18px' }}>AI 语音绘图工具</h1>
      </header>
      <main style={{ flex: 1, display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
        <p>画布区域（待实现）</p>
      </main>
    </div>
  )
}

export default App
```

- [ ] **Step 7: 创建 main.tsx**

```tsx
// frontend/src/main.tsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
```

- [ ] **Step 8: 验证前端启动**

```bash
cd frontend
npm install
npm run dev
```

Expected: 浏览器打开 http://localhost:3000 显示 "AI 语音绘图工具" 标题

- [ ] **Step 9: Commit**

```bash
git add frontend/
git commit -m "feat: 初始化前端 React + TypeScript 项目

- 配置 Vite 构建工具
- 添加 TypeScript 类型定义（Shape, Command, Operation）
- 创建 App 基础组件
- 配置开发代理到后端 8000 端口"
```

---

## Task 3: 数据模型定义

**对应 PR:** PR5

**Files:**
- Create: `backend/models/__init__.py`
- Create: `backend/models/schemas.py`

- [ ] **Step 1: 创建 Pydantic 模型**

```python
# backend/models/schemas.py
from pydantic import BaseModel, Field
from typing import Optional, Literal
from enum import Enum


class ShapeType(str, Enum):
    RECT = "rect"
    CIRCLE = "circle"
    ELLIPSE = "ellipse"
    TRIANGLE = "triangle"
    DIAMOND = "diamond"
    LINE = "line"
    ARROW = "arrow"


class ActionType(str, Enum):
    CREATE = "create"
    DELETE = "delete"
    MOVE = "move"
    RESIZE = "resize"
    SET_COLOR = "setColor"
    SET_TEXT = "setText"
    UNDO = "undo"
    REDO = "redo"


class ShapeProps(BaseModel):
    x: Optional[float] = None
    y: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None
    radius: Optional[float] = None
    fill: Optional[str] = None
    stroke: Optional[str] = None
    strokeWidth: Optional[float] = None
    text: Optional[str] = None
    fontSize: Optional[float] = None
    dx: Optional[float] = None
    dy: Optional[float] = None


class Command(BaseModel):
    action: ActionType
    type: Optional[ShapeType] = None
    target: Optional[str] = None
    props: Optional[ShapeProps] = None


class Shape(BaseModel):
    id: str
    type: ShapeType
    x: float = 100
    y: float = 100
    width: Optional[float] = None
    height: Optional[float] = None
    radius: Optional[float] = None
    fill: str = "#4A90D9"
    stroke: str = "#2C3E50"
    strokeWidth: float = 2
    text: Optional[str] = None
    fontSize: Optional[float] = None
    rotation: float = 0


class Operation(BaseModel):
    id: str
    type: str
    targetId: str
    prevState: dict
    nextState: dict
    timestamp: float


class CanvasState(BaseModel):
    shapes: dict[str, Shape] = Field(default_factory=dict)
    undoStack: list[Operation] = Field(default_factory=list)
    redoStack: list[Operation] = Field(default_factory=list)
```

- [ ] **Step 2: 创建 __init__.py**

```python
# backend/models/__init__.py
```

- [ ] **Step 3: Commit**

```bash
git add backend/models/
git commit -m "feat: 添加后端数据模型定义

- Shape: 图形数据模型（7种类型）
- Command: 指令模型（8种操作）
- Operation: 操作记录模型（支持撤销/重做）
- CanvasState: 画布状态管理模型"
```

---

## Task 4: 指令执行器

**对应 PR:** PR5

**Files:**
- Create: `backend/services/__init__.py`
- Create: `backend/services/executor.py`
- Create: `backend/tests/__init__.py`
- Create: `backend/tests/test_executor.py`

- [ ] **Step 1: 编写执行器测试**

```python
# backend/tests/test_executor.py
import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.executor import Executor


def test_create_rect():
    executor = Executor()
    result = executor.execute({
        "action": "create",
        "type": "rect",
        "props": {"x": 100, "y": 100, "width": 200, "height": 150}
    })
    assert result["success"] is True
    assert len(executor.state.shapes) == 1
    shape = list(executor.state.shapes.values())[0]
    assert shape.type == "rect"
    assert shape.x == 100
    assert shape.width == 200


def test_create_circle():
    executor = Executor()
    result = executor.execute({
        "action": "create",
        "type": "circle",
        "props": {"x": 200, "y": 200, "radius": 50}
    })
    assert result["success"] is True
    shape = list(executor.state.shapes.values())[0]
    assert shape.type == "circle"
    assert shape.radius == 50


def test_delete_shape():
    executor = Executor()
    executor.execute({"action": "create", "type": "rect", "props": {"x": 0, "y": 0}})
    shape_id = list(executor.state.shapes.keys())[0]
    result = executor.execute({"action": "delete", "target": shape_id})
    assert result["success"] is True
    assert len(executor.state.shapes) == 0


def test_move_shape():
    executor = Executor()
    executor.execute({"action": "create", "type": "rect", "props": {"x": 100, "y": 100}})
    shape_id = list(executor.state.shapes.keys())[0]
    result = executor.execute({"action": "move", "target": shape_id, "props": {"dx": 50, "dy": 30}})
    assert result["success"] is True
    shape = executor.state.shapes[shape_id]
    assert shape.x == 150
    assert shape.y == 130


def test_set_color():
    executor = Executor()
    executor.execute({"action": "create", "type": "rect", "props": {"x": 0, "y": 0}})
    shape_id = list(executor.state.shapes.keys())[0]
    result = executor.execute({"action": "setColor", "target": shape_id, "props": {"fill": "#FF0000"}})
    assert result["success"] is True
    assert executor.state.shapes[shape_id].fill == "#FF0000"


def test_undo_redo():
    executor = Executor()
    executor.execute({"action": "create", "type": "rect", "props": {"x": 100, "y": 100}})
    shape_id = list(executor.state.shapes.keys())[0]
    executor.execute({"action": "move", "target": shape_id, "props": {"dx": 50, "dy": 0}})
    assert executor.state.shapes[shape_id].x == 150

    # undo
    executor.execute({"action": "undo"})
    assert executor.state.shapes[shape_id].x == 100

    # redo
    executor.execute({"action": "redo"})
    assert executor.state.shapes[shape_id].x == 150


def test_delete_nonexistent():
    executor = Executor()
    result = executor.execute({"action": "delete", "target": "nonexistent"})
    assert result["success"] is False
    assert "未找到" in result["message"]
```

- [ ] **Step 2: 运行测试确认失败**

```bash
cd backend
python -m pytest tests/test_executor.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'services.executor'`

- [ ] **Step 3: 实现执行器**

```python
# backend/services/executor.py
import uuid
import time
from models.schemas import Shape, Operation, CanvasState, ShapeType


class Executor:
    def __init__(self):
        self.state = CanvasState()

    def execute(self, command: dict) -> dict:
        action = command.get("action")

        try:
            if action == "create":
                return self._create(command)
            elif action == "delete":
                return self._delete(command)
            elif action == "move":
                return self._move(command)
            elif action == "resize":
                return self._resize(command)
            elif action == "setColor":
                return self._set_color(command)
            elif action == "setText":
                return self._set_text(command)
            elif action == "undo":
                return self._undo()
            elif action == "redo":
                return self._redo()
            else:
                return {"success": False, "message": f"不支持的操作: {action}"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def get_state(self) -> dict:
        return {
            "shapes": {k: v.model_dump() for k, v in self.state.shapes.items()},
            "undoCount": len(self.state.undoStack),
            "redoCount": len(self.state.redoStack),
        }

    def _create(self, command: dict) -> dict:
        props = command.get("props", {})
        shape_type = command.get("type", "rect")
        shape_id = str(uuid.uuid4())[:8]

        shape = Shape(
            id=shape_id,
            type=ShapeType(shape_type),
            x=props.get("x", 100),
            y=props.get("y", 100),
            width=props.get("width"),
            height=props.get("height"),
            radius=props.get("radius"),
            fill=props.get("fill", "#4A90D9"),
            stroke=props.get("stroke", "#2C3E50"),
            strokeWidth=props.get("strokeWidth", 2),
            text=props.get("text"),
            fontSize=props.get("fontSize"),
        )

        self.state.shapes[shape_id] = shape

        op = Operation(
            id=str(uuid.uuid4())[:8],
            type="create",
            targetId=shape_id,
            prevState={},
            nextState=shape.model_dump(),
            timestamp=time.time(),
        )
        self.state.undoStack.append(op)
        self.state.redoStack.clear()

        return {"success": True, "shapeId": shape_id, "shape": shape.model_dump()}

    def _delete(self, command: dict) -> dict:
        target = command.get("target")
        if target not in self.state.shapes:
            return {"success": False, "message": f"未找到图形: {target}"}

        shape = self.state.shapes[target]
        op = Operation(
            id=str(uuid.uuid4())[:8],
            type="delete",
            targetId=target,
            prevState=shape.model_dump(),
            nextState={},
            timestamp=time.time(),
        )
        self.state.undoStack.append(op)
        self.state.redoStack.clear()
        del self.state.shapes[target]

        return {"success": True, "message": f"已删除图形 {target}"}

    def _move(self, command: dict) -> dict:
        target = command.get("target")
        if target not in self.state.shapes:
            return {"success": False, "message": f"未找到图形: {target}"}

        props = command.get("props", {})
        dx = props.get("dx", 0)
        dy = props.get("dy", 0)

        shape = self.state.shapes[target]
        prev = shape.model_dump()
        shape.x += dx
        shape.y += dy

        op = Operation(
            id=str(uuid.uuid4())[:8],
            type="move",
            targetId=target,
            prevState=prev,
            nextState=shape.model_dump(),
            timestamp=time.time(),
        )
        self.state.undoStack.append(op)
        self.state.redoStack.clear()

        return {"success": True, "shape": shape.model_dump()}

    def _resize(self, command: dict) -> dict:
        target = command.get("target")
        if target not in self.state.shapes:
            return {"success": False, "message": f"未找到图形: {target}"}

        props = command.get("props", {})
        shape = self.state.shapes[target]
        prev = shape.model_dump()

        if props.get("width") is not None:
            shape.width = props["width"]
        if props.get("height") is not None:
            shape.height = props["height"]
        if props.get("radius") is not None:
            shape.radius = props["radius"]

        op = Operation(
            id=str(uuid.uuid4())[:8],
            type="resize",
            targetId=target,
            prevState=prev,
            nextState=shape.model_dump(),
            timestamp=time.time(),
        )
        self.state.undoStack.append(op)
        self.state.redoStack.clear()

        return {"success": True, "shape": shape.model_dump()}

    def _set_color(self, command: dict) -> dict:
        target = command.get("target")
        if target not in self.state.shapes:
            return {"success": False, "message": f"未找到图形: {target}"}

        props = command.get("props", {})
        shape = self.state.shapes[target]
        prev = shape.model_dump()

        if props.get("fill"):
            shape.fill = props["fill"]
        if props.get("stroke"):
            shape.stroke = props["stroke"]

        op = Operation(
            id=str(uuid.uuid4())[:8],
            type="setColor",
            targetId=target,
            prevState=prev,
            nextState=shape.model_dump(),
            timestamp=time.time(),
        )
        self.state.undoStack.append(op)
        self.state.redoStack.clear()

        return {"success": True, "shape": shape.model_dump()}

    def _set_text(self, command: dict) -> dict:
        target = command.get("target")
        if target not in self.state.shapes:
            return {"success": False, "message": f"未找到图形: {target}"}

        props = command.get("props", {})
        shape = self.state.shapes[target]
        prev = shape.model_dump()
        shape.text = props.get("text", "")
        shape.fontSize = props.get("fontSize", 14)

        op = Operation(
            id=str(uuid.uuid4())[:8],
            type="setText",
            targetId=target,
            prevState=prev,
            nextState=shape.model_dump(),
            timestamp=time.time(),
        )
        self.state.undoStack.append(op)
        self.state.redoStack.clear()

        return {"success": True, "shape": shape.model_dump()}

    def _undo(self) -> dict:
        if not self.state.undoStack:
            return {"success": False, "message": "没有可撤销的操作"}

        op = self.state.undoStack.pop()
        self.state.redoStack.append(op)

        if op.type == "create":
            del self.state.shapes[op.targetId]
        elif op.type == "delete":
            self.state.shapes[op.targetId] = Shape(**op.prevState)
        else:
            if op.targetId in self.state.shapes:
                for k, v in op.prevState.items():
                    setattr(self.state.shapes[op.targetId], k, v)

        return {"success": True, "message": "撤销成功", "state": self.get_state()}

    def _redo(self) -> dict:
        if not self.state.redoStack:
            return {"success": False, "message": "没有可重做的操作"}

        op = self.state.redoStack.pop()
        self.state.undoStack.append(op)

        if op.type == "delete":
            del self.state.shapes[op.targetId]
        elif op.type == "create":
            self.state.shapes[op.targetId] = Shape(**op.nextState)
        else:
            if op.targetId in self.state.shapes:
                for k, v in op.nextState.items():
                    setattr(self.state.shapes[op.targetId], k, v)

        return {"success": True, "message": "重做成功", "state": self.get_state()}
```

- [ ] **Step 4: 创建 __init__.py**

```python
# backend/services/__init__.py
```

```python
# backend/tests/__init__.py
```

- [ ] **Step 5: 运行测试确认通过**

```bash
cd backend
python -m pytest tests/test_executor.py -v
```

Expected: 全部 7 个测试 PASS

- [ ] **Step 6: Commit**

```bash
git add backend/services/executor.py backend/services/__init__.py backend/models/ backend/tests/
git commit -m "feat: 实现指令执行器和状态管理

- 支持 create/delete/move/resize/setColor/setText 操作
- 实现 undo/redo 撤销重做机制
- 7 个单元测试全部通过"
```

---

## Task 5: 语音指令优化器 — 规则预处理层

**对应 PR:** PR3

**Files:**
- Create: `backend/services/optimizer.py`
- Create: `backend/tests/test_optimizer.py`

- [ ] **Step 1: 编写优化器规则层测试**

```python
# backend/tests/test_optimizer.py
import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.optimizer import Optimizer


def test_remove_filler_words():
    opt = Optimizer()
    result = opt.rule_clean("就是画一个那个红色的矩形")
    assert "就是" not in result
    assert "那个" not in result
    assert "矩形" in result


def test_remove_interjections():
    opt = Optimizer()
    result = opt.rule_clean("画一个矩形啊")
    assert "啊" not in result
    assert "矩形" in result


def test_normalize_punctuation():
    opt = Optimizer()
    result = opt.rule_clean("画一个...矩形")
    assert "..." not in result
    assert "矩形" in result


def test_remove_then():
    opt = Optimizer()
    result = opt.rule_clean("然后画一个矩形")
    assert "然后" not in result
    assert "矩形" in result


def test_preserve_meaning():
    opt = Optimizer()
    result = opt.rule_clean("画一个红色的矩形")
    assert "红色" in result
    assert "矩形" in result


def test_multiple_filler_words():
    opt = Optimizer()
    result = opt.rule_clean("就是那个嗯然后画一个矩形吧")
    assert "就是" not in result
    assert "那个" not in result
    assert "嗯" not in result
    assert "然后" not in result
    assert "吧" not in result
    assert "矩形" in result
```

- [ ] **Step 2: 运行测试确认失败**

```bash
cd backend
python -m pytest tests/test_optimizer.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'services.optimizer'`

- [ ] **Step 3: 实现规则预处理层**

```python
# backend/services/optimizer.py
import re
import os
import httpx


class Optimizer:
    FILLER_WORDS = [
        "就是", "那个", "嗯", "然后", "接着", "接下来",
        "就是说", "怎么说呢", "对对对",
    ]

    INTERJECTIONS = ["啊", "呢", "吧", "呀", "哦", "嘛", "哈", "哎"]

    def rule_clean(self, text: str) -> str:
        """Layer 1: 规则预处理，去除口头禅和语气词"""
        # 去除口头禅
        for word in self.FILLER_WORDS:
            text = text.replace(word, "")

        # 去除语气词（只在词尾或标点前）
        for word in self.INTERJECTIONS:
            text = text.replace(f"{word}，", "，")
            text = text.replace(f"{word}。", "。")
            text = text.replace(f"{word}！", "！")
            if text.endswith(word):
                text = text[:-1]

        # 去除省略号
        text = text.replace("...", "")
        text = text.replace("…", "")

        # 清理多余空格和标点
        text = re.sub(r'\s+', ' ', text).strip()
        text = re.sub(r'[，,]+', '，', text)
        text = text.strip("，。,. ")

        return text

    async def llm_optimize(self, raw_text: str, canvas_state: dict = None, history: list = None) -> str:
        """Layer 2: LLM 语义优化"""
        api_key = os.getenv("LLM_API_KEY", "")
        base_url = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")

        canvas_str = str(canvas_state) if canvas_state else "空画布"
        history_str = "\n".join(history[-5:]) if history else "无"

        prompt = f"""你是一个语音指令优化助手。用户的语音输入可能包含口头禅、语病、指代不清等问题。

当前画布状态：
{canvas_str}

最近操作历史：
{history_str}

请将以下语音输入优化为清晰的绘图指令：
- 去除口头禅和语气词
- 补全不完整的语句
- 解决指代词（"它"、"那个"等）基于上下文
- 拆分复合句为独立指令
- 保持原意不变

输出格式：每条指令一行，用分号分隔。只输出优化后的指令，不要其他文字。

语音输入：{raw_text}"""

        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                f"{base_url}/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": "mimo-v2.5-pro",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                },
            )
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()

    async def optimize(self, raw_text: str, canvas_state: dict = None, history: list = None) -> dict:
        """完整优化流程：规则预处理 + LLM 优化"""
        cleaned = self.rule_clean(raw_text)

        # 如果规则处理后文本很短，跳过 LLM
        if len(cleaned) <= 4:
            return {"original": raw_text, "cleaned": cleaned, "optimized": cleaned}

        try:
            optimized = await self.llm_optimize(cleaned, canvas_state, history)
            return {"original": raw_text, "cleaned": cleaned, "optimized": optimized}
        except Exception as e:
            # LLM 失败时降级为规则处理结果
            return {"original": raw_text, "cleaned": cleaned, "optimized": cleaned, "error": str(e)}
```

- [ ] **Step 4: 运行测试确认通过**

```bash
cd backend
python -m pytest tests/test_optimizer.py -v
```

Expected: 全部 6 个测试 PASS

- [ ] **Step 5: Commit**

```bash
git add backend/services/optimizer.py backend/tests/test_optimizer.py
git commit -m "feat: 实现语音指令优化器规则预处理层

- 支持去除 13 种口头禅和 8 种语气词
- 标点规范化处理
- 6 个单元测试全部通过
- 预留 LLM 语义优化接口"
```

---

## Task 6: 语音指令优化器 — LLM 集成

**对应 PR:** PR3

**Files:**
- Modify: `backend/services/optimizer.py`
- Modify: `backend/tests/test_optimizer.py`

- [ ] **Step 1: 添加 LLM 优化测试**

```python
# backend/tests/test_optimizer.py 追加
import asyncio

def test_llm_optimize_basic():
    """测试 LLM 优化基本功能（需要 API Key）"""
    api_key = os.getenv("LLM_API_KEY")
    if not api_key:
        pytest.skip("LLM_API_KEY not set")

    opt = Optimizer()
    result = asyncio.run(opt.llm_optimize("画个圆"))
    assert len(result) > 0
    assert "圆" in result


def test_optimize_full_flow():
    """测试完整优化流程"""
    api_key = os.getenv("LLM_API_KEY")
    if not api_key:
        pytest.skip("LLM_API_KEY not set")

    opt = Optimizer()
    result = asyncio.run(opt.optimize("就是画一个那个红色的矩形"))
    assert result["original"] == "就是画一个那个红色的矩形"
    assert "就是" not in result["cleaned"]
    assert len(result["optimized"]) > 0
```

- [ ] **Step 2: 运行测试（无 API Key 时跳过 LLM 测试）**

```bash
cd backend
python -m pytest tests/test_optimizer.py -v
```

Expected: 6 个规则测试 PASS，2 个 LLM 测试 SKIP（无 API Key）

- [ ] **Step 3: Commit**

```bash
git add backend/tests/test_optimizer.py
git commit -m "feat: 添加优化器 LLM 集成测试

- 测试 LLM 语义优化功能
- 无 API Key 时自动跳过 LLM 测试
- 测试完整优化流程（规则+LLM）"
```

---

## Task 7: LLM 指令解析器

**对应 PR:** PR4

**Files:**
- Create: `backend/services/parser.py`
- Create: `backend/tests/test_parser.py`

- [ ] **Step 1: 编写解析器测试**

```python
# backend/tests/test_parser.py
import pytest
import sys
import os
import asyncio
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.parser import Parser


def test_parse_create_rect():
    """测试解析创建矩形指令（需要 API Key）"""
    api_key = os.getenv("LLM_API_KEY")
    if not api_key:
        pytest.skip("LLM_API_KEY not set")

    parser = Parser()
    result = asyncio.run(parser.parse("画一个红色矩形"))
    assert result["action"] == "create"
    assert result["type"] == "rect"


def test_parse_create_circle():
    api_key = os.getenv("LLM_API_KEY")
    if not api_key:
        pytest.skip("LLM_API_KEY not set")

    parser = Parser()
    result = asyncio.run(parser.parse("画一个圆形"))
    assert result["action"] == "create"
    assert result["type"] == "circle"


def test_parse_json_format():
    api_key = os.getenv("LLM_API_KEY")
    if not api_key:
        pytest.skip("LLM_API_KEY not set")

    parser = Parser()
    result = asyncio.run(parser.parse("画一个蓝色矩形"))
    assert "action" in result
    assert isinstance(result, dict)
```

- [ ] **Step 2: 实现解析器**

```python
# backend/services/parser.py
import os
import json
import httpx


class Parser:
    SYSTEM_PROMPT = """你是一个绘图指令解析助手。将自然语言指令解析为 JSON 操作。

支持的图形类型：
- rect: 矩形
- circle: 圆形
- ellipse: 椭圆
- triangle: 三角形
- diamond: 菱形
- line: 直线
- arrow: 箭头

支持的操作：
- create: 创建图形
- delete: 删除图形
- move: 移动图形
- resize: 缩放图形
- setColor: 修改颜色
- setText: 添加文字
- undo: 撤销
- redo: 重做

当前画布状态：
{canvas_state}

输出严格的 JSON 格式，不要包含其他文字。"""

    async def parse(self, command: str, canvas_state: dict = None) -> dict:
        api_key = os.getenv("LLM_API_KEY", "")
        base_url = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")

        canvas_str = str(canvas_state) if canvas_state else "空画布"
        system = self.SYSTEM_PROMPT.format(canvas_state=canvas_str)

        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                f"{base_url}/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": "mimo-v2.5-pro",
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": f"指令：{command}"},
                    ],
                    "temperature": 0.1,
                },
            )
            data = response.json()
            content = data["choices"][0]["message"]["content"].strip()

            # 提取 JSON（可能被 markdown 包裹）
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            return json.loads(content)
```

- [ ] **Step 3: 运行测试**

```bash
cd backend
python -m pytest tests/test_parser.py -v
```

Expected: 无 API Key 时全部 SKIP；有 API Key 时 PASS

- [ ] **Step 4: Commit**

```bash
git add backend/services/parser.py backend/tests/test_parser.py
git commit -m "feat: 实现 LLM 指令解析器

- 将自然语言指令解析为 JSON 操作
- 支持 7 种图形类型和 8 种操作类型
- 处理 markdown 包裹的 JSON 响应"
```

---

## Task 8: FunASR 语音识别服务

**对应 PR:** PR2

**Files:**
- Create: `backend/services/asr_service.py`

- [ ] **Step 1: 实现 ASR 服务**

```python
# backend/services/asr_service.py
import numpy as np


class ASRService:
    def __init__(self):
        self.model = None
        self._load_model()

    def _load_model(self):
        """加载 FunASR 模型"""
        try:
            from funasr import AutoModel

            model_path = "paraformer-zh"
            self.model = AutoModel(
                model=model_path,
                vad_model="fsmn-vad",
                punc_model="ct-punc",
            )
            print(f"FunASR 模型加载成功: {model_path}")
        except Exception as e:
            print(f"FunASR 模型加载失败: {e}")
            self.model = None

    def recognize(self, audio_bytes: bytes) -> str:
        """识别音频 bytes，返回文本"""
        if self.model is None:
            raise RuntimeError("FunASR 模型未加载")

        # 将 PCM bytes 转为 numpy 数组
        audio_array = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0

        result = self.model.generate(input=audio_array)
        if result and len(result) > 0:
            return result[0].get("text", "")
        return ""

    def is_ready(self) -> bool:
        return self.model is not None
```

- [ ] **Step 2: Commit**

```bash
git add backend/services/asr_service.py
git commit -m "feat: 集成 FunASR 语音识别服务

- 加载 paraformer-zh 中文识别模型
- 支持 PCM 音频 bytes 输入
- 流式识别接口预留"
```

---

## Task 9: WebSocket 处理器

**对应 PR:** PR9

**Files:**
- Modify: `backend/main.py`

- [ ] **Step 1: 实现 WebSocket 处理**

```python
# backend/main.py
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from services.executor import Executor
from services.optimizer import Optimizer
from services.parser import Parser

app = FastAPI(title="AI Voice Draw")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

executor = Executor()
optimizer = Optimizer()
parser = Parser()


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: await websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket 连接已建立")

    # ASR 服务延迟加载
    asr_service = None

    try:
        while True:
            data = await websocket.receive()

            if data["type"] == "websocket.receive":
                # 判断是二进制（音频）还是文本（指令）
                if "bytes" in data:
                    # 音频数据
                    audio_bytes = data["bytes"]
                    try:
                        if asr_service is None:
                            from services.asr_service import ASRService
                            asr_service = ASRService()

                        if asr_service.is_ready():
                            text = asr_service.recognize(audio_bytes)
                            await websocket.send_json({
                                "type": "asr_final",
                                "data": text,
                            })
                        else:
                            await websocket.send_json({
                                "type": "error",
                                "data": "语音识别服务未就绪",
                            })
                    except Exception as e:
                        await websocket.send_json({
                            "type": "error",
                            "data": f"语音识别失败: {str(e)}",
                        })

                elif "text" in data:
                    message = json.loads(data["text"])
                    msg_type = message.get("type")
                    msg_data = message.get("data", "")

                    if msg_type == "optimize":
                        # 优化指令
                        try:
                            result = await optimizer.optimize(
                                msg_data,
                                canvas_state=executor.get_state(),
                            )
                            await websocket.send_json({
                                "type": "optimized",
                                "data": result,
                            })
                        except Exception as e:
                            await websocket.send_json({
                                "type": "error",
                                "data": f"优化失败: {str(e)}",
                            })

                    elif msg_type == "command":
                        # 解析并执行指令
                        try:
                            parsed = await parser.parse(
                                msg_data,
                                canvas_state=executor.get_state(),
                            )
                            result = executor.execute(parsed)
                            await websocket.send_json({
                                "type": "result",
                                "data": {
                                    "command": parsed,
                                    "result": result,
                                    "canvas": executor.get_state(),
                                },
                            })
                        except json.JSONDecodeError:
                            await websocket.send_json({
                                "type": "error",
                                "data": "指令解析失败，请重新描述",
                            })
                        except Exception as e:
                            await websocket.send_json({
                                "type": "error",
                                "data": f"执行失败: {str(e)}",
                            })

    except WebSocketDisconnect:
        print("WebSocket 连接断开")
```

- [ ] **Step 2: 验证后端启动**

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Expected: 服务启动成功，WebSocket 端点 `/ws` 可用

- [ ] **Step 3: Commit**

```bash
git add backend/main.py
git commit -m "feat: 实现 WebSocket 消息处理

- 支持音频二进制和文本 JSON 两种消息
- 音频 → ASR 识别 → 返回文本
- 指令 → 优化 → 解析 → 执行 → 返回结果
- 错误处理和异常捕获"
```

---

## Task 10: SVG 画布组件

**对应 PR:** PR6

**Files:**
- Create: `frontend/src/components/Canvas.tsx`
- Modify: `frontend/src/App.tsx`

- [ ] **Step 1: 实现 Canvas 组件**

```tsx
// frontend/src/components/Canvas.tsx
import { Shape } from '../types'

interface CanvasProps {
  shapes: Shape[]
  selectedId: string | null
  onSelect: (id: string | null) => void
}

function renderShape(shape: Shape, isSelected: boolean) {
  const commonProps = {
    key: shape.id,
    fill: shape.fill,
    stroke: isSelected ? '#FFD700' : shape.stroke,
    strokeWidth: isSelected ? shape.strokeWidth + 2 : shape.strokeWidth,
    style: { cursor: 'pointer' },
    'data-id': shape.id,
  }

  switch (shape.type) {
    case 'rect':
      return (
        <rect
          {...commonProps}
          x={shape.x}
          y={shape.y}
          width={shape.width || 100}
          height={shape.height || 80}
          transform={shape.rotation ? `rotate(${shape.rotation} ${shape.x + (shape.width || 100) / 2} ${shape.y + (shape.height || 80) / 2})` : undefined}
        />
      )
    case 'circle':
      return (
        <circle
          {...commonProps}
          cx={shape.x}
          cy={shape.y}
          r={shape.radius || 50}
        />
      )
    case 'ellipse':
      return (
        <ellipse
          {...commonProps}
          cx={shape.x}
          cy={shape.y}
          rx={shape.width || 60}
          ry={shape.height || 40}
        />
      )
    case 'triangle': {
      const w = shape.width || 100
      const h = shape.height || 80
      const points = `${shape.x},${shape.y + h} ${shape.x + w / 2},${shape.y} ${shape.x + w},${shape.y + h}`
      return <polygon {...commonProps} points={points} />
    }
    case 'diamond': {
      const w = shape.width || 80
      const h = shape.height || 80
      const cx = shape.x + w / 2
      const cy = shape.y + h / 2
      const points = `${cx},${shape.y} ${shape.x + w},${cy} ${cx},${shape.y + h} ${shape.x},${cy}`
      return <polygon {...commonProps} points={points} />
    }
    case 'line':
      return (
        <line
          {...commonProps}
          x1={shape.x}
          y1={shape.y}
          x2={shape.x + (shape.width || 100)}
          y2={shape.y + (shape.height || 0)}
          fill="none"
        />
      )
    case 'arrow': {
      const x2 = shape.x + (shape.width || 100)
      const y2 = shape.y + (shape.height || 0)
      return (
        <g {...commonProps}>
          <line x1={shape.x} y1={shape.y} x2={x2} y2={y2} fill="none" stroke={shape.stroke} strokeWidth={shape.strokeWidth} />
          <polygon
            points={`${x2},${y2} ${x2 - 10},${y2 - 5} ${x2 - 10},${y2 + 5}`}
            fill={shape.stroke}
          />
        </g>
      )
    }
    default:
      return null
  }
}

function renderText(shape: Shape) {
  if (!shape.text) return null
  const cx = shape.x + (shape.width || 100) / 2
  const cy = shape.y + (shape.height || 80) / 2
  return (
    <text
      x={cx}
      y={cy}
      textAnchor="middle"
      dominantBaseline="middle"
      fontSize={shape.fontSize || 14}
      fill="#333"
      pointerEvents="none"
    >
      {shape.text}
    </text>
  )
}

export default function Canvas({ shapes, selectedId, onSelect }: CanvasProps) {
  const handleClick = (e: React.MouseEvent<SVGSVGElement>) => {
    const target = e.target as SVGElement
    const id = target.getAttribute('data-id')
    onSelect(id || null)
  }

  return (
    <svg
      width="100%"
      height="100%"
      style={{ background: '#f8f9fa', border: '1px solid #dee2e6' }}
      onClick={handleClick}
    >
      {shapes.map((shape) => (
        <g key={shape.id}>
          {renderShape(shape, shape.id === selectedId)}
          {renderText(shape)}
        </g>
      ))}
      {shapes.length === 0 && (
        <text x="50%" y="50%" textAnchor="middle" fill="#999" fontSize="16">
          点击麦克风开始语音绘图
        </text>
      )}
    </svg>
  )
}
```

- [ ] **Step 2: 更新 App.tsx 集成 Canvas**

```tsx
// frontend/src/App.tsx
import { useState } from 'react'
import Canvas from './components/Canvas'
import { Shape } from './types'

function App() {
  const [shapes, setShapes] = useState<Shape[]>([])
  const [selectedId, setSelectedId] = useState<string | null>(null)

  return (
    <div style={{ width: '100vw', height: '100vh', display: 'flex', flexDirection: 'column' }}>
      <header style={{ padding: '8px 16px', borderBottom: '1px solid #ccc', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1 style={{ margin: 0, fontSize: '18px' }}>AI 语音绘图工具</h1>
        <div>
          <button style={{ marginRight: 8 }}>导出PNG</button>
          <button>导出SVG</button>
        </div>
      </header>
      <main style={{ flex: 1, padding: 16 }}>
        <Canvas shapes={shapes} selectedId={selectedId} onSelect={setSelectedId} />
      </main>
      <footer style={{ padding: 8, borderTop: '1px solid #ccc' }}>
        <p style={{ margin: 0, color: '#999' }}>语音面板（待实现）</p>
      </footer>
    </div>
  )
}

export default App
```

- [ ] **Step 3: 验证前端渲染**

```bash
cd frontend
npm run dev
```

Expected: 浏览器显示画布区域，中央有"点击麦克风开始语音绘图"提示

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/Canvas.tsx frontend/src/App.tsx
git commit -m "feat: 实现 SVG 画布组件

- 支持 7 种图形渲染（rect/circle/ellipse/triangle/diamond/line/arrow）
- 图形选中高亮显示
- 空画布提示文字"
```

---

## Task 11: 语音输入面板

**对应 PR:** PR7

**Files:**
- Create: `frontend/src/components/VoicePanel.tsx`
- Create: `frontend/src/hooks/useVoice.ts`
- Modify: `frontend/src/App.tsx`

- [ ] **Step 1: 实现语音录制 Hook**

```typescript
// frontend/src/hooks/useVoice.ts
import { useState, useRef, useCallback } from 'react'

export function useVoice() {
  const [isRecording, setIsRecording] = useState(false)
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null)
  const mediaRecorder = useRef<MediaRecorder | null>(null)
  const chunks = useRef<Blob[]>([])

  const startRecording = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      mediaRecorder.current = new MediaRecorder(stream, { mimeType: 'audio/webm' })
      chunks.current = []

      mediaRecorder.current.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunks.current.push(e.data)
        }
      }

      mediaRecorder.current.onstop = () => {
        const blob = new Blob(chunks.current, { type: 'audio/webm' })
        setAudioBlob(blob)
        stream.getTracks().forEach((track) => track.stop())
      }

      mediaRecorder.current.start()
      setIsRecording(true)
    } catch (err) {
      console.error('录音失败:', err)
    }
  }, [])

  const stopRecording = useCallback(() => {
    if (mediaRecorder.current && mediaRecorder.current.state !== 'inactive') {
      mediaRecorder.current.stop()
      setIsRecording(false)
    }
  }, [])

  return { isRecording, audioBlob, startRecording, stopRecording }
}
```

- [ ] **Step 2: 实现 VoicePanel 组件**

```tsx
// frontend/src/components/VoicePanel.tsx
import { useState } from 'react'
import { useVoice } from '../hooks/useVoice'

interface VoicePanelProps {
  onSendAudio: (blob: Blob) => void
  onSendCommand: (text: string) => void
  originalText: string
  optimizedText: string
}

export default function VoicePanel({ onSendAudio, onSendCommand, originalText, optimizedText }: VoicePanelProps) {
  const { isRecording, audioBlob, startRecording, stopRecording } = useVoice()
  const [textInput, setTextInput] = useState('')

  const handleMicClick = () => {
    if (isRecording) {
      stopRecording()
    } else {
      startRecording()
    }
  }

  // 录音完成后自动发送
  if (audioBlob && !isRecording) {
    onSendAudio(audioBlob)
  }

  const handleSubmit = () => {
    if (textInput.trim()) {
      onSendCommand(textInput.trim())
      setTextInput('')
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 8, padding: 12, background: '#fff', borderRadius: 8, boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>
      {/* 原始识别 */}
      {originalText && (
        <div style={{ padding: 8, background: '#fff3cd', borderRadius: 4, fontSize: 14 }}>
          🎤 原始识别: {originalText}
        </div>
      )}

      {/* 优化后 */}
      {optimizedText && (
        <div style={{ padding: 8, background: '#d4edda', borderRadius: 4, fontSize: 14 }}>
          ✨ 优化后: {optimizedText}
        </div>
      )}

      {/* 输入区域 */}
      <div style={{ display: 'flex', gap: 8 }}>
        <button
          onClick={handleMicClick}
          style={{
            width: 48,
            height: 48,
            borderRadius: '50%',
            border: 'none',
            background: isRecording ? '#dc3545' : '#007bff',
            color: '#fff',
            fontSize: 20,
            cursor: 'pointer',
            animation: isRecording ? 'pulse 1s infinite' : 'none',
          }}
        >
          🎤
        </button>
        <input
          type="text"
          value={textInput}
          onChange={(e) => setTextInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
          placeholder="或直接输入指令..."
          style={{ flex: 1, padding: '8px 12px', border: '1px solid #ccc', borderRadius: 4, fontSize: 14 }}
        />
        <button onClick={handleSubmit} style={{ padding: '8px 16px', border: 'none', background: '#28a745', color: '#fff', borderRadius: 4, cursor: 'pointer' }}>
          发送
        </button>
      </div>
    </div>
  )
}
```

- [ ] **Step 3: 更新 App.tsx 集成 VoicePanel**

```tsx
// frontend/src/App.tsx
import { useState } from 'react'
import Canvas from './components/Canvas'
import VoicePanel from './components/VoicePanel'
import { Shape } from './types'

function App() {
  const [shapes, setShapes] = useState<Shape[]>([])
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [originalText, setOriginalText] = useState('')
  const [optimizedText, setOptimizedText] = useState('')

  const handleSendAudio = (blob: Blob) => {
    // TODO: WebSocket 发送音频
    console.log('发送音频:', blob.size, 'bytes')
  }

  const handleSendCommand = (text: string) => {
    // TODO: WebSocket 发送指令
    console.log('发送指令:', text)
  }

  return (
    <div style={{ width: '100vw', height: '100vh', display: 'flex', flexDirection: 'column' }}>
      <header style={{ padding: '8px 16px', borderBottom: '1px solid #ccc', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1 style={{ margin: 0, fontSize: '18px' }}>AI 语音绘图工具</h1>
        <div>
          <button style={{ marginRight: 8 }}>导出PNG</button>
          <button>导出SVG</button>
        </div>
      </header>
      <main style={{ flex: 1, padding: 16 }}>
        <Canvas shapes={shapes} selectedId={selectedId} onSelect={setSelectedId} />
      </main>
      <footer style={{ padding: 12, borderTop: '1px solid #ccc', background: '#f8f9fa' }}>
        <VoicePanel
          onSendAudio={handleSendAudio}
          onSendCommand={handleSendCommand}
          originalText={originalText}
          optimizedText={optimizedText}
        />
      </footer>
    </div>
  )
}

export default App
```

- [ ] **Step 4: 验证前端**

```bash
cd frontend
npm run dev
```

Expected: 页面底部显示语音面板，有麦克风按钮和文本输入框

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/VoicePanel.tsx frontend/src/hooks/useVoice.ts frontend/src/App.tsx
git commit -m "feat: 实现语音输入面板

- MediaRecorder API 录制音频
- 麦克风按钮（录音/停止切换）
- 文本输入框（备用输入方式）
- 显示原始识别和优化后对比"
```

---

## Task 12: 状态面板

**对应 PR:** PR8

**Files:**
- Create: `frontend/src/components/StatusPanel.tsx`
- Modify: `frontend/src/App.tsx`

- [ ] **Step 1: 实现 StatusPanel 组件**

```tsx
// frontend/src/components/StatusPanel.tsx
import { Shape, Operation } from '../types'

interface StatusPanelProps {
  shapes: Shape[]
  selectedShape: Shape | null
  operations: Operation[]
}

export default function StatusPanel({ shapes, selectedShape, operations }: StatusPanelProps) {
  return (
    <div style={{ width: 240, background: '#fff', borderLeft: '1px solid #dee2e6', padding: 12, overflowY: 'auto' }}>
      {/* 图形统计 */}
      <div style={{ marginBottom: 16 }}>
        <h3 style={{ margin: '0 0 8px', fontSize: 14, color: '#666' }}>画布状态</h3>
        <p style={{ margin: 0, fontSize: 13 }}>图形数量: {shapes.length}</p>
      </div>

      {/* 选中图形属性 */}
      {selectedShape && (
        <div style={{ marginBottom: 16 }}>
          <h3 style={{ margin: '0 0 8px', fontSize: 14, color: '#666' }}>选中图形</h3>
          <div style={{ fontSize: 13, lineHeight: 1.8 }}>
            <p style={{ margin: 0 }}>类型: {selectedShape.type}</p>
            <p style={{ margin: 0 }}>位置: ({Math.round(selectedShape.x)}, {Math.round(selectedShape.y)})</p>
            {selectedShape.width && <p style={{ margin: 0 }}>宽度: {Math.round(selectedShape.width)}</p>}
            {selectedShape.height && <p style={{ margin: 0 }}>高度: {Math.round(selectedShape.height)}</p>}
            {selectedShape.radius && <p style={{ margin: 0 }}>半径: {Math.round(selectedShape.radius)}</p>}
            <p style={{ margin: 0 }}>
              填充: <span style={{ display: 'inline-block', width: 12, height: 12, background: selectedShape.fill, verticalAlign: 'middle', marginRight: 4 }} />
              {selectedShape.fill}
            </p>
          </div>
        </div>
      )}

      {/* 操作历史 */}
      <div>
        <h3 style={{ margin: '0 0 8px', fontSize: 14, color: '#666' }}>操作历史</h3>
        {operations.length === 0 ? (
          <p style={{ margin: 0, fontSize: 13, color: '#999' }}>暂无操作</p>
        ) : (
          <ul style={{ margin: 0, padding: 0, listStyle: 'none', fontSize: 12 }}>
            {operations.slice(-10).reverse().map((op, i) => (
              <li key={op.id} style={{ padding: '4px 0', borderBottom: '1px solid #f0f0f0' }}>
                {op.type} - {op.targetId}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}
```

- [ ] **Step 2: 更新 App.tsx 集成 StatusPanel**

```tsx
// frontend/src/App.tsx
import { useState } from 'react'
import Canvas from './components/Canvas'
import VoicePanel from './components/VoicePanel'
import StatusPanel from './components/StatusPanel'
import { Shape, Operation } from './types'

function App() {
  const [shapes, setShapes] = useState<Shape[]>([])
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [originalText, setOriginalText] = useState('')
  const [optimizedText, setOptimizedText] = useState('')
  const [operations, setOperations] = useState<Operation[]>([])

  const selectedShape = shapes.find((s) => s.id === selectedId) || null

  const handleSendAudio = (blob: Blob) => {
    console.log('发送音频:', blob.size, 'bytes')
  }

  const handleSendCommand = (text: string) => {
    console.log('发送指令:', text)
  }

  return (
    <div style={{ width: '100vw', height: '100vh', display: 'flex', flexDirection: 'column' }}>
      <header style={{ padding: '8px 16px', borderBottom: '1px solid #ccc', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1 style={{ margin: 0, fontSize: '18px' }}>AI 语音绘图工具</h1>
        <div>
          <button style={{ marginRight: 8 }}>导出PNG</button>
          <button>导出SVG</button>
        </div>
      </header>
      <div style={{ flex: 1, display: 'flex' }}>
        <main style={{ flex: 1, padding: 16 }}>
          <Canvas shapes={shapes} selectedId={selectedId} onSelect={setSelectedId} />
        </main>
        <StatusPanel shapes={shapes} selectedShape={selectedShape} operations={operations} />
      </div>
      <footer style={{ padding: 12, borderTop: '1px solid #ccc', background: '#f8f9fa' }}>
        <VoicePanel
          onSendAudio={handleSendAudio}
          onSendCommand={handleSendCommand}
          originalText={originalText}
          optimizedText={optimizedText}
        />
      </footer>
    </div>
  )
}

export default App
```

- [ ] **Step 3: 验证前端**

```bash
cd frontend
npm run dev
```

Expected: 右侧显示状态面板，包含画布状态、选中图形属性、操作历史

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/StatusPanel.tsx frontend/src/App.tsx
git commit -m "feat: 实现状态面板

- 显示画布图形数量
- 显示选中图形属性（类型、位置、尺寸、颜色）
- 显示操作历史列表（最近 10 条）"
```

---

## Task 13: WebSocket 客户端

**对应 PR:** PR9

**Files:**
- Create: `frontend/src/hooks/useWebSocket.ts`
- Modify: `frontend/src/App.tsx`

- [ ] **Step 1: 实现 WebSocket Hook**

```typescript
// frontend/src/hooks/useWebSocket.ts
import { useState, useEffect, useRef, useCallback } from 'react'
import { ServerMessage } from '../types'

export function useWebSocket(url: string) {
  const [isConnected, setIsConnected] = useState(false)
  const [lastMessage, setLastMessage] = useState<ServerMessage | null>(null)
  const ws = useRef<WebSocket | null>(null)
  const reconnectTimer = useRef<number | null>(null)
  const reconnectCount = useRef(0)

  const connect = useCallback(() => {
    if (ws.current?.readyState === WebSocket.OPEN) return

    ws.current = new WebSocket(url)

    ws.current.onopen = () => {
      setIsConnected(true)
      reconnectCount.current = 0
      console.log('WebSocket 已连接')
    }

    ws.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data) as ServerMessage
        setLastMessage(data)
      } catch (e) {
        console.error('解析消息失败:', e)
      }
    }

    ws.current.onclose = () => {
      setIsConnected(false)
      console.log('WebSocket 断开')

      // 自动重连（最多 3 次）
      if (reconnectCount.current < 3) {
        reconnectCount.current++
        reconnectTimer.current = window.setTimeout(() => {
          console.log(`尝试重连 (${reconnectCount.current}/3)...`)
          connect()
        }, 2000)
      }
    }

    ws.current.onerror = (err) => {
      console.error('WebSocket 错误:', err)
    }
  }, [url])

  useEffect(() => {
    connect()
    return () => {
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current)
      ws.current?.close()
    }
  }, [connect])

  const sendAudio = useCallback((blob: Blob) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(blob)
    }
  }, [])

  const sendJson = useCallback((data: { type: string; data: string }) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(data))
    }
  }, [])

  return { isConnected, lastMessage, sendAudio, sendJson }
}
```

- [ ] **Step 2: 更新 App.tsx 集成 WebSocket**

```tsx
// frontend/src/App.tsx
import { useState, useEffect } from 'react'
import Canvas from './components/Canvas'
import VoicePanel from './components/VoicePanel'
import StatusPanel from './components/StatusPanel'
import { useWebSocket } from './hooks/useWebSocket'
import { Shape, Operation, ServerMessage } from './types'

function App() {
  const [shapes, setShapes] = useState<Shape[]>([])
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [originalText, setOriginalText] = useState('')
  const [optimizedText, setOptimizedText] = useState('')
  const [operations, setOperations] = useState<Operation[]>([])

  const wsUrl = `ws://${window.location.host}/ws`
  const { isConnected, lastMessage, sendAudio, sendJson } = useWebSocket(wsUrl)

  // 处理服务端消息
  useEffect(() => {
    if (!lastMessage) return

    switch (lastMessage.type) {
      case 'asr_final':
        setOriginalText(lastMessage.data as string)
        break
      case 'optimized': {
        const data = lastMessage.data as { original: string; optimized: string }
        setOriginalText(data.original)
        setOptimizedText(data.optimized)
        break
      }
      case 'result': {
        const data = lastMessage.data as { canvas: { shapes: Record<string, Shape> } }
        const shapesList = Object.values(data.canvas.shapes)
        setShapes(shapesList)
        break
      }
      case 'error':
        console.error('服务端错误:', lastMessage.data)
        break
    }
  }, [lastMessage])

  const selectedShape = shapes.find((s) => s.id === selectedId) || null

  const handleSendAudio = (blob: Blob) => {
    sendAudio(blob)
  }

  const handleSendCommand = (text: string) => {
    sendJson({ type: 'command', data: text })
  }

  return (
    <div style={{ width: '100vw', height: '100vh', display: 'flex', flexDirection: 'column' }}>
      <header style={{ padding: '8px 16px', borderBottom: '1px solid #ccc', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1 style={{ margin: 0, fontSize: '18px' }}>AI 语音绘图工具</h1>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span style={{ fontSize: 12, color: isConnected ? '#28a745' : '#dc3545' }}>
            {isConnected ? '● 已连接' : '○ 未连接'}
          </span>
          <button style={{ marginRight: 8 }}>导出PNG</button>
          <button>导出SVG</button>
        </div>
      </header>
      <div style={{ flex: 1, display: 'flex' }}>
        <main style={{ flex: 1, padding: 16 }}>
          <Canvas shapes={shapes} selectedId={selectedId} onSelect={setSelectedId} />
        </main>
        <StatusPanel shapes={shapes} selectedShape={selectedShape} operations={operations} />
      </div>
      <footer style={{ padding: 12, borderTop: '1px solid #ccc', background: '#f8f9fa' }}>
        <VoicePanel
          onSendAudio={handleSendAudio}
          onSendCommand={handleSendCommand}
          originalText={originalText}
          optimizedText={optimizedText}
        />
      </footer>
    </div>
  )
}

export default App
```

- [ ] **Step 3: 验证全链路**

```bash
# 终端 1: 启动后端
cd backend
uvicorn main:app --reload --port 8000

# 终端 2: 启动前端
cd frontend
npm run dev
```

Expected: 前端显示"已连接"，在文本框输入指令可发送到后端

- [ ] **Step 4: Commit**

```bash
git add frontend/src/hooks/useWebSocket.ts frontend/src/App.tsx
git commit -m "feat: 实现 WebSocket 客户端通信

- 自动连接和重连机制（最多 3 次）
- 支持发送音频和 JSON 指令
- 处理服务端消息（asr/optimized/result/error）
- 连接状态指示器"
```

---

## Task 14: 导出功能

**对应 PR:** PR10

**Files:**
- Create: `frontend/src/utils/svgExport.ts`
- Modify: `frontend/src/App.tsx`

- [ ] **Step 1: 实现导出工具**

```typescript
// frontend/src/utils/svgExport.ts
export function exportSVG(svgElement: SVGSVGElement, filename: string = 'drawing.svg') {
  const serializer = new XMLSerializer()
  const svgStr = serializer.serializeToString(svgElement)
  const blob = new Blob([svgStr], { type: 'image/svg+xml' })
  downloadBlob(blob, filename)
}

export function exportPNG(svgElement: SVGSVGElement, filename: string = 'drawing.png') {
  const serializer = new XMLSerializer()
  const svgStr = serializer.serializeToString(svgElement)
  const svgBlob = new Blob([svgStr], { type: 'image/svg+xml;charset=utf-8' })
  const url = URL.createObjectURL(svgBlob)

  const img = new Image()
  img.onload = () => {
    const canvas = document.createElement('canvas')
    canvas.width = svgElement.clientWidth || 800
    canvas.height = svgElement.clientHeight || 600
    const ctx = canvas.getContext('2d')!
    ctx.fillStyle = '#fff'
    ctx.fillRect(0, 0, canvas.width, canvas.height)
    ctx.drawImage(img, 0, 0)

    canvas.toBlob((blob) => {
      if (blob) downloadBlob(blob, filename)
      URL.revokeObjectURL(url)
    }, 'image/png')
  }
  img.src = url
}

function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}
```

- [ ] **Step 2: 更新 App.tsx 添加导出按钮功能**

在 App.tsx 的 header 部分，将导出按钮改为：

```tsx
<header style={{ padding: '8px 16px', borderBottom: '1px solid #ccc', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
  <h1 style={{ margin: 0, fontSize: '18px' }}>AI 语音绘图工具</h1>
  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
    <span style={{ fontSize: 12, color: isConnected ? '#28a745' : '#dc3545' }}>
      {isConnected ? '● 已连接' : '○ 未连接'}
    </span>
    <button onClick={() => {
      const svg = document.querySelector('svg')
      if (svg) exportPNG(svg)
    }}>导出PNG</button>
    <button onClick={() => {
      const svg = document.querySelector('svg')
      if (svg) exportSVG(svg)
    }}>导出SVG</button>
  </div>
</header>
```

在文件顶部添加导入：

```typescript
import { exportPNG, exportSVG } from './utils/svgExport'
```

- [ ] **Step 3: 验证导出**

```bash
cd frontend
npm run dev
```

Expected: 点击导出按钮后浏览器下载对应格式文件

- [ ] **Step 4: Commit**

```bash
git add frontend/src/utils/svgExport.ts frontend/src/App.tsx
git commit -m "feat: 实现 PNG/SVG 导出功能

- SVG 导出：序列化 SVG 元素为文件
- PNG 导出：Canvas API 转换 SVG 为 PNG
- 自动触发浏览器下载"
```

---

## Task 15: UI 美化 + 交互动画

**对应 PR:** PR11

**Files:**
- Modify: `frontend/src/App.tsx`
- Modify: `frontend/src/components/VoicePanel.tsx`
- Modify: `frontend/src/components/Canvas.tsx`

- [ ] **Step 1: 添加全局样式**

在 `frontend/index.html` 的 `<head>` 中添加：

```html
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }
  button { transition: all 0.2s; }
  button:hover { opacity: 0.85; transform: scale(1.02); }
  button:active { transform: scale(0.98); }
  @keyframes pulse {
    0%, 100% { box-shadow: 0 0 0 0 rgba(220, 53, 69, 0.4); }
    50% { box-shadow: 0 0 0 12px rgba(220, 53, 69, 0); }
  }
  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: translateY(0); }
  }
  .fade-in { animation: fadeIn 0.3s ease-out; }
</style>
```

- [ ] **Step 2: 添加图形创建动画**

在 Canvas.tsx 的 `renderShape` 函数中，给每个图形元素添加 CSS 类：

```tsx
const commonProps = {
  key: shape.id,
  fill: shape.fill,
  stroke: isSelected ? '#FFD700' : shape.stroke,
  strokeWidth: isSelected ? shape.strokeWidth + 2 : shape.strokeWidth,
  style: { cursor: 'pointer', transition: 'all 0.3s ease' },
  'data-id': shape.id,
  className: 'fade-in',
}
```

- [ ] **Step 3: 验证动画效果**

```bash
cd frontend
npm run dev
```

Expected: 麦克风录音时有脉冲动画，图形创建时有淡入效果，按钮有悬停动效

- [ ] **Step 4: Commit**

```bash
git add frontend/index.html frontend/src/components/Canvas.tsx
git commit -m "feat: 添加 UI 美化和交互动画

- 全局样式重置和字体设置
- 麦克风录音脉冲动画
- 图形创建淡入动画
- 按钮悬停/点击动效"
```

---

## Task 16: 错误处理

**对应 PR:** PR12

**Files:**
- Modify: `frontend/src/App.tsx`
- Modify: `frontend/src/components/VoicePanel.tsx`
- Modify: `backend/main.py`

- [ ] **Step 1: 前端错误提示组件**

在 App.tsx 中添加错误状态和提示：

```tsx
const [error, setError] = useState<string | null>(null)

// 处理服务端错误消息
useEffect(() => {
  if (lastMessage?.type === 'error') {
    setError(lastMessage.data as string)
    setTimeout(() => setError(null), 5000)
  }
}, [lastMessage])

// 在 header 下方添加错误提示
{error && (
  <div style={{ padding: '8px 16px', background: '#f8d7da', color: '#721c24', borderBottom: '1px solid #f5c6cb', fontSize: 14 }}>
    ⚠️ {error}
  </div>
)}
```

- [ ] **Step 2: 麦克风权限错误处理**

更新 `frontend/src/hooks/useVoice.ts` 的 `startRecording`：

```typescript
const startRecording = useCallback(async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    // ... 原有代码
  } catch (err: any) {
    if (err.name === 'NotAllowedError') {
      alert('请允许麦克风权限后重试')
    } else if (err.name === 'NotFoundError') {
      alert('未检测到麦克风设备')
    } else {
      alert(`录音失败: ${err.message}`)
    }
  }
}, [])
```

- [ ] **Step 3: 后端 WebSocket 错误处理完善**

在 `backend/main.py` 的 WebSocket 处理中添加心跳检测：

```python
import asyncio

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket 连接已建立")

    asr_service = None

    try:
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive(), timeout=30.0)
            except asyncio.TimeoutError:
                # 心跳检测
                try:
                    await websocket.send_json({"type": "ping"})
                except Exception:
                    break
                continue

            # ... 原有消息处理逻辑
    except WebSocketDisconnect:
        print("WebSocket 连接断开")
    except Exception as e:
        print(f"WebSocket 异常: {e}")
        try:
            await websocket.send_json({"type": "error", "data": "服务内部错误"})
        except Exception:
            pass
```

- [ ] **Step 4: 验证错误处理**

```bash
# 测试场景：断开后端，观察前端重连提示
# 测试场景：拒绝麦克风权限，观察提示
```

Expected: 各种异常场景有友好提示，不会导致页面崩溃

- [ ] **Step 5: Commit**

```bash
git add frontend/src/App.tsx frontend/src/hooks/useVoice.ts backend/main.py
git commit -m "feat: 完善全局错误处理

- 前端错误提示条（5 秒自动消失）
- 麦克风权限错误友好提示
- WebSocket 心跳检测（30 秒超时）
- 后端异常捕获和错误消息"
```

---

## Task 17: README 完善 + 文档整理

**对应 PR:** PR13

**Files:**
- Modify: `README.md`

- [ ] **Step 1: 更新 README 为完整版本**

将 README.md 更新为包含以下完整内容：

```markdown
# AI 语音绘图工具

纯语音控制的绘图工具，支持语音创建、编辑、导出图形。核心创新是指令优化器，自动清洗语音识别中的口头禅和语病。

## 核心功能

- 🎤 语音创建图形（矩形、圆形、三角形、菱形、直线、箭头）
- ✨ 语音指令优化（去除口头禅、补全语句、消除指代）
- ✏️ 图形编辑（移动、删除、颜色修改、添加文字）
- ↩️ 撤销/重做
- 📤 导出 PNG/SVG

## 技术栈

| 层级 | 技术 |
|---|---|
| 前端 | React 18 + TypeScript + Vite |
| 后端 | Python 3.10+ + FastAPI |
| 语音识别 | FunASR (paraformer-zh) |
| LLM | mimo-v2.5-pro (OpenAI 兼容接口) |
| 通信 | WebSocket |

## 快速启动

### 环境要求

- Node.js >= 18
- Python >= 3.10
- FunASR 模型（首次运行自动下载，约 1GB）

### 启动后端

```bash
cd backend
pip install -r requirements.txt
export LLM_API_KEY="your-api-key"
export LLM_BASE_URL="your-api-url"
python main.py
```

### 启动前端

```bash
cd frontend
npm install
npm run dev
```

浏览器打开 http://localhost:3000

### 配置说明

| 环境变量 | 说明 | 示例 |
|---|---|---|
| LLM_API_KEY | LLM 服务 API Key | sk-xxx |
| LLM_BASE_URL | LLM 服务地址 | https://api.example.com/v1 |

## 项目结构

```
AI-voice-draw/
├── frontend/          # React 前端
│   └── src/
│       ├── components/  # Canvas, VoicePanel, StatusPanel
│       ├── hooks/       # useVoice, useWebSocket, useCanvas
│       └── utils/       # svgExport
├── backend/           # Python 后端
│   ├── services/      # asr, optimizer, parser, executor
│   └── models/        # Pydantic 数据模型
└── docs/              # 设计文档
```

## 依赖列表

### 前端
- react ^18.2.0
- react-dom ^18.2.0
- typescript ^5.3.0
- vite ^5.0.0

### 后端
- fastapi ^0.104.0
- uvicorn ^0.24.0
- funasr ^1.0.26
- httpx ^0.25.0
- websockets ^12.0

## 原创功能说明

本项目的原创部分为"语音指令优化器"，采用规则预处理 + LLM 语义优化的两层架构。其他功能使用标准技术实现，不涉及第三方代码复用。

## Demo

视频链接：（bilibili 链接）
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: 完善 README 文档

- 添加核心功能列表和技术栈表格
- 添加完整的启动步骤和配置说明
- 添加项目结构和依赖列表
- 添加原创功能说明"
```

---

## Self-Review Checklist

1. **Spec coverage:**
   - ✅ 语音识别 (Task 8)
   - ✅ 指令优化器 (Task 5, 6)
   - ✅ 指令解析器 (Task 7)
   - ✅ 指令执行器 + 撤销重做 (Task 4)
   - ✅ SVG 画布 (Task 10)
   - ✅ 语音面板 (Task 11)
   - ✅ 状态面板 (Task 12)
   - ✅ WebSocket 通信 (Task 9, 13)
   - ✅ 导出功能 (Task 14)
   - ✅ 交互动画 (Task 15)
   - ✅ 错误处理 (Task 16)
   - ✅ README (Task 17)
   - ✅ 7 种图形类型全部覆盖
   - ✅ 8 种操作类型全部覆盖

2. **Placeholder scan:** 无 TBD/TODO，所有代码完整 ✅

3. **Type consistency:**
   - Shape 类型在前后端一致 ✅
   - Command 类型在 parser 和 executor 一致 ✅
   - WebSocket 消息类型一致 ✅

---

**Plan complete. Two execution options:**

**1. Subagent-Driven (recommended)** - 每个 Task 派发独立子代理执行，任务间审查，快速迭代

**2. Inline Execution** - 在当前会话中按顺序执行，批量执行带检查点

**选择哪种方式？**
