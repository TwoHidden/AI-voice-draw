"""LLM Agent - 使用 Function Calling 调用绘图工具"""
import logging
from dataclasses import dataclass
from typing import Optional

import httpx

from app.config import settings
from app.tools import TOOLS_SCHEMA, get_system_prompt

logger = logging.getLogger(__name__)


@dataclass
class AgentResult:
    """Agent 处理结果"""
    tool_calls: list  # 工具调用列表
    text_response: Optional[str] = None  # LLM 的文字回复（可选）


class Agent:
    """LLM Agent - 使用 Function Calling 调用绘图工具"""

    async def process(self, user_input: str, canvas_state: str = "") -> AgentResult:
        """
        处理用户输入，返回工具调用列表

        Args:
            user_input: 用户的语音或文字指令
            canvas_state: 当前画布状态摘要

        Returns:
            AgentResult 包含 tool_calls 和可选的 text_response
        """
        if not user_input or not user_input.strip():
            return AgentResult(tool_calls=[])

        if not settings.LLM_API_KEY:
            logger.warning("LLM_API_KEY 未配置，无法调用 LLM")
            return AgentResult(tool_calls=[])

        system_prompt = get_system_prompt(canvas_state)

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{settings.LLM_BASE_URL}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.LLM_API_KEY}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": settings.LLM_MODEL,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_input},
                        ],
                        "tools": TOOLS_SCHEMA,
                        "tool_choice": "auto",
                        "temperature": 0.1,
                        "max_tokens": 1000,
                    },
                )
                response.raise_for_status()
                result = response.json()

                message = result["choices"][0]["message"]

                # 提取 tool_calls
                tool_calls = message.get("tool_calls", []) or []

                # 提取文字回复（如果有）
                content = message.get("content") or message.get("reasoning_content") or ""
                text_response = content.strip() if content else None

                logger.info(f"Agent 返回 {len(tool_calls)} 个工具调用")
                for tc in tool_calls:
                    func = tc.get("function", {})
                    logger.info(f"  - {func.get('name')}({func.get('arguments')})")

                return AgentResult(
                    tool_calls=tool_calls,
                    text_response=text_response,
                )

        except httpx.TimeoutException:
            logger.error("LLM API 超时")
            return AgentResult(tool_calls=[])
        except httpx.HTTPStatusError as e:
            logger.error(f"LLM API 错误: {e.response.status_code}")
            return AgentResult(tool_calls=[])
        except Exception as e:
            logger.error(f"Agent 处理失败: {e}")
            return AgentResult(tool_calls=[])


# 全局实例
agent = Agent()
