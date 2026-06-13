# LLM Agent Function Calling 设计文档

## 概述

将绘图工具集成到 LLM 的 Function Calling 能力中，让 LLM 作为 Agent 直接调用绘图 API，替代原有的"优化器+解析器"两步架构。

## 背景

### 当前架构

```
语音 → ASR → 优化器(LLM) → 解析器(LLM) → 执行器 → 画布
```

问题：
1. 两次 LLM 调用，延迟高
2. 解析器返回 `reasoning_content` 而非 `content`，导致解析失败
3. 口语化指令仍无法正确解析执行

### 目标架构

```
语音 → ASR → LLM Agent(带Tools) → 执行器 → 画布
```

优势：
1. 一次 LLM 调用，延迟降低 50%
2. LLM 直接输出结构化 tool_calls，无需额外解析
3. 支持复杂指令（一次调用多个工具）
4. 上下文感知，支持指代消解

## 设计细节

### 1. Tools 定义

#### create_shape

```json
{
  "type": "function",
  "function": {
    "name": "create_shape",
    "description": "创建一个新的图形",
    "parameters": {
      "type": "object",
      "properties": {
        "shape_type": {
          "type": "string",
          "enum": ["rect", "circle", "ellipse", "triangle", "diamond", "line", "arrow"],
          "description": "图形类型"
        },
        "fill": {
          "type": "string",
          "description": "填充颜色，十六进制格式，如 #FF0000"
        },
        "stroke": {
          "type": "string",
          "description": "边框颜色，十六进制格式"
        },
        "x": {
          "type": "number",
          "description": "X坐标，默认400"
        },
        "y": {
          "type": "number",
          "description": "Y坐标，默认300"
        },
        "width": {
          "type": "number",
          "description": "宽度，默认200"
        },
        "height": {
          "type": "number",
          "description": "高度，默认150"
        }
      },
      "required": ["shape_type"]
    }
  }
}
```

#### delete_shape

```json
{
  "type": "function",
  "function": {
    "name": "delete_shape",
    "description": "删除指定图形或最近创建的图形",
    "parameters": {
      "type": "object",
      "properties": {
        "target_id": {
          "type": "string",
          "description": "要删除的图形ID"
        },
        "shape_type": {
          "type": "string",
          "enum": ["rect", "circle", "ellipse", "triangle", "diamond", "line", "arrow"],
          "description": "删除指定类型的最近一个图形"
        }
      }
    }
  }
}
```

#### move_shape

```json
{
  "type": "function",
  "function": {
    "name": "move_shape",
    "description": "移动图形到新位置",
    "parameters": {
      "type": "object",
      "properties": {
        "target_id": {
          "type": "string",
          "description": "要移动的图形ID"
        },
        "x": {
          "type": "number",
          "description": "新的X坐标"
        },
        "y": {
          "type": "number",
          "description": "新的Y坐标"
        }
      },
      "required": ["target_id", "x", "y"]
    }
  }
}
```

#### resize_shape

```json
{
  "type": "function",
  "function": {
    "name": "resize_shape",
    "description": "调整图形大小",
    "parameters": {
      "type": "object",
      "properties": {
        "target_id": {
          "type": "string",
          "description": "要调整的图形ID"
        },
        "width": {
          "type": "number",
          "description": "新的宽度"
        },
        "height": {
          "type": "number",
          "description": "新的高度"
        },
        "scale": {
          "type": "number",
          "description": "缩放比例，如1.5表示放大50%"
        }
      },
      "required": ["target_id"]
    }
  }
}
```

#### set_color

```json
{
  "type": "function",
  "function": {
    "name": "set_color",
    "description": "修改图形颜色",
    "parameters": {
      "type": "object",
      "properties": {
        "target_id": {
          "type": "string",
          "description": "要修改的图形ID"
        },
        "fill": {
          "type": "string",
          "description": "新的填充颜色"
        },
        "stroke": {
          "type": "string",
          "description": "新的边框颜色"
        }
      },
      "required": ["target_id"]
    }
  }
}
```

#### set_text

```json
{
  "type": "function",
  "function": {
    "name": "set_text",
    "description": "为图形添加或修改文字",
    "parameters": {
      "type": "object",
      "properties": {
        "target_id": {
          "type": "string",
          "description": "要添加文字的图形ID"
        },
        "text": {
          "type": "string",
          "description": "文字内容"
        }
      },
      "required": ["target_id", "text"]
    }
  }
}
```

#### undo / redo

```json
{
  "type": "function",
  "function": {
    "name": "undo",
    "description": "撤销上一步操作",
    "parameters": {
      "type": "object",
      "properties": {}
    }
  }
}
```

```json
{
  "type": "function",
  "function": {
    "name": "redo",
    "description": "重做上一步撤销的操作",
    "parameters": {
      "type": "object",
      "properties": {}
    }
  }
}
```

### 2. System Prompt

```
你是 AI 绘图助手。根据用户的语音或文字指令，调用工具完成绘图操作。

## 能力
- 创建、删除、移动、缩放、改颜色、加文字
- 撤销、重做
- 理解口语化表达

## 颜色映射
当用户提到颜色时，转换为十六进制：
- 红色 → #FF0000
- 蓝色 → #0000FF
- 绿色 → #00FF00
- 黄色 → #FFFF00
- 紫色 → #800080
- 橙色 → #FFA500
- 粉色 → #FFC0CB
- 黑色 → #000000
- 白色 → #FFFFFF
- 灰色 → #808080

如果用户说"深蓝"、"浅蓝"等，使用合理的变体。

## 位置推断
- 左边 → x: 150
- 中间/中间 → x: 400
- 右边 → x: 650
- 上边 → y: 150
- 下边 → y: 450

## 默认大小
- 长方形: width=200, height=150
- 圆形: width=150, height=150
- 椭圆: width=200, height=120
- 三角形: width=180, height=160

## 规则
1. 理解口语化表达，去除语气词、重复、口误
2. 支持一次调用多个工具（如"画一个红色长方形和蓝色圆形"）
3. 如果指令模糊，使用合理默认值而非询问
4. 颜色必须是十六进制格式
5. 只调用工具，不要输出额外解释

## 当前画布状态
{canvas_state}
```

### 3. 代码结构

```
backend/app/
├── agent.py        # LLM Agent：调用 LLM with tools，处理 tool_calls
├── tools.py        # 工具定义：TOOLS_SCHEMA, execute_tool_calls()
├── executor.py     # 保留：CommandExecutor，执行具体绘图操作
├── main.py         # 修改：移除 optimizer 和 parser，调用 agent
├── optimizer.py    # 废弃：功能合并到 agent
├── parser.py       # 废弃：功能合并到 agent
```

### 4. 流程

```python
async def _process_and_execute(websocket, raw_text):
    # 1. 获取画布状态
    canvas_state = executor.get_state_summary()

    # 2. 调用 LLM Agent
    result = await agent.process(raw_text, canvas_state)

    # 3. 发送 LLM 回复（可选）
    if result.text_response:
        await websocket.send_json({"type": "agent_response", "data": result.text_response})

    # 4. 执行工具调用
    for tool_call in result.tool_calls:
        new_state = execute_tool_call(tool_call)
        await websocket.send_json({"type": "state_update", "data": new_state})

    # 5. 如果没有工具调用，返回错误
    if not result.tool_calls:
        await websocket.send_json({"type": "error", "data": "无法理解指令"})
```

### 5. 错误处理

| 场景 | 处理方式 |
|------|----------|
| LLM 返回空 tool_calls | 返回错误提示 |
| 工具参数无效 | 使用默认值，记录警告 |
| LLM API 超时 | 返回错误，建议重试 |
| JSON 解析失败 | 重试一次，仍失败则报错 |

### 6. 前端适配

- 移除 `optimizeResults` 相关代码
- 新增 `agentResponse` 显示 LLM 的文字回复（可选）
- 保留 `stateUpdate` 处理画布更新

### 7. 保留的文件

- `executor.py` — 执行器保留，负责实际的画布操作
- `models.py` — 数据模型保留
- `config.py` — 配置保留
- `asr.py` — ASR 服务保留

### 8. 废弃的文件

- `optimizer.py` — 功能合并到 agent
- `parser.py` — 功能合并到 agent

## 测试用例

| 输入 | 预期工具调用 |
|------|-------------|
| "画一个蓝色长方形" | create_shape(shape_type="rect", fill="#0000FF") |
| "创建一个红色的圆" | create_shape(shape_type="circle", fill="#FF0000") |
| "画一个红色正方形和蓝色圆形" | create_shape(...) + create_shape(...) |
| "把那个方块移到右边" | move_shape(target_id="xxx", x=650) |
| "删除圆形" | delete_shape(shape_type="circle") |
| "撤销" | undo() |
| "放大一点" | resize_shape(target_id="xxx", scale=1.5) |
| "改成绿色" | set_color(target_id="xxx", fill="#00FF00") |

## 实施计划

见 `2026-06-13-llm-agent-function-calling.md`
