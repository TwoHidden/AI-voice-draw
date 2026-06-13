"""FastAPI 应用入口"""
import json
import logging
from typing import Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.models import CanvasState, Command
from app.executor import CommandExecutor
from app.agent import agent
from app.asr import asr_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局实例
executor = CommandExecutor()


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.on_event("startup")
async def startup():
    """应用启动时初始化 ASR"""
    await asr_service.initialize()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket 端点 - 处理语音和文本指令"""
    await websocket.accept()
    logger.info("WebSocket 连接建立")

    try:
        while True:
            message = await websocket.receive()

            if "bytes" in message:
                # 音频数据 → ASR → Agent → 执行
                audio_bytes = message["bytes"]
                await _handle_audio(websocket, audio_bytes)

            elif "text" in message:
                text = message["text"]
                data = json.loads(text)

                msg_type = data.get("type", "text")

                if msg_type == "text":
                    # 文本指令 → Agent → 执行
                    await _handle_text(websocket, data.get("data", ""))
                elif msg_type == "ping":
                    await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        logger.info("WebSocket 断开")
    except Exception as e:
        logger.error(f"WebSocket 错误: {e}")
        await websocket.send_json({"type": "error", "data": str(e)})


async def _handle_audio(websocket: WebSocket, audio_bytes: bytes):
    """处理音频数据"""
    logger.info(f"收到音频数据: {len(audio_bytes)} bytes")

    # 1. ASR 识别
    text = await asr_service.transcribe(audio_bytes)
    if not text:
        logger.warning(f"ASR 返回空结果，音频大小: {len(audio_bytes)} bytes")
        await websocket.send_json({"type": "error", "data": "语音识别失败，请重试"})
        return

    logger.info(f"ASR 识别成功: {text}")
    # 返回 ASR 结果
    await websocket.send_json({"type": "asr_result", "data": text})

    # 2. 处理文本
    await _process_and_execute(websocket, text)


async def _handle_text(websocket: WebSocket, text: str):
    """处理文本指令"""
    await _process_and_execute(websocket, text)


async def _process_and_execute(websocket: WebSocket, raw_text: str):
    """处理文本指令：Agent → 执行 → 响应"""
    # 获取当前画布状态摘要
    canvas_state = executor.get_state_summary()

    # 调用 LLM Agent
    result = await agent.process(raw_text, canvas_state)

    # 如果 LLM 有文字回复，发送给前端
    if result.text_response:
        await websocket.send_json({
            "type": "agent_response",
            "data": result.text_response,
        })

    # 执行工具调用
    if not result.tool_calls:
        await websocket.send_json({"type": "error", "data": "无法理解指令，请重试"})
        return

    for tool_call in result.tool_calls:
        new_state = executor.execute_tool_call(tool_call)
        # 发送更新后的画布状态
        await websocket.send_json({
            "type": "state_update",
            "data": new_state.model_dump(),
        })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, reload=settings.DEBUG)
