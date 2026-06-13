"""LLM 指令解析器 - 自然语言转 JSON 指令"""
import json
import logging
from typing import Optional
import httpx

from app.config import settings
from app.models import Command, OperationType, ShapeType

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """你是一个绘图指令解析器。将用户输入的自然语言指令解析为 JSON 格式。

输出格式（严格 JSON，无多余文字）：
{
  "operation": "create|delete|move|resize|setColor|setText|undo|redo",
  "shape_type": "rect|circle|ellipse|triangle|diamond|line|arrow",
  "target_id": "可选，目标图形ID",
  "properties": {
    "x": 数值,
    "y": 数值,
    "width": 数值,
    "height": 数值,
    "fill": "#颜色代码",
    "stroke": "#颜色代码",
    "text": "文本内容",
    "scale": 缩放比例
  }
}

规则：
1. create 操作必须包含 shape_type
2. move/resize/setColor/setText 可包含 target_id
3. undo/redo 不需要 shape_type 和 target_id
4. 未指定的属性使用默认值
5. 颜色使用十六进制代码

示例：
输入：创建红色长方形
输出：{"operation":"create","shape_type":"rect","properties":{"fill":"#FF0000"}}

输入：删除圆形
输出：{"operation":"delete","shape_type":"circle","properties":{}}

输入：移动到右边
输出：{"operation":"move","properties":{"x":500}}

输入：撤销
输出：{"operation":"undo","properties":{}}"""


async def parse_command(text: str) -> Optional[Command]:
    """将自然语言解析为 Command 对象"""
    if not text or not text.strip():
        return None

    # 本地快速解析（常见简单指令）
    local_result = _try_local_parse(text)
    if local_result:
        return local_result

    # LLM 解析
    return await _llm_parse(text)


def _try_local_parse(text: str) -> Optional[Command]:
    """尝试本地快速解析简单指令"""
    text = text.strip()

    # 撤销/重做
    if text in ("撤销", "undo"):
        return Command(operation=OperationType.UNDO, properties={})
    if text in ("重做", "redo"):
        return Command(operation=OperationType.REDO, properties={})

    # 简单删除
    if text in ("删除", "delete", "删除选中"):
        return Command(operation=OperationType.DELETE, properties={})

    return None


async def _llm_parse(text: str) -> Optional[Command]:
    """调用 LLM 解析指令"""
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                f"{settings.LLM_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.LLM_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.LLM_MODEL,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": text},
                    ],
                    "temperature": 0.1,
                    "max_tokens": 200,
                },
            )
            response.raise_for_status()
            result = response.json()
            content = result["choices"][0]["message"]["content"].strip()

            # 提取 JSON
            if "```" in content:
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]

            data = json.loads(content)

            # 构造 Command
            operation = OperationType(data["operation"])
            shape_type = None
            if data.get("shape_type"):
                shape_type = ShapeType(data["shape_type"])

            return Command(
                operation=operation,
                shape_type=shape_type,
                target_id=data.get("target_id"),
                properties=data.get("properties", {}),
            )
    except Exception as e:
        logger.error(f"LLM 解析失败: {e}")
        return None
