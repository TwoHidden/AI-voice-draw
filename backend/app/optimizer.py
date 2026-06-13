"""语音指令优化器 - LLM 语义优化"""
import logging
import re
from typing import Optional
from app.models import OptimizeResult

logger = logging.getLogger(__name__)


class VoiceOptimizer:
    """语音指令优化器 — LLM 语义优化（无规则引擎，避免字符串替换破坏文本）"""

    async def optimize(self, raw_text: str, canvas_state=None) -> OptimizeResult:
        """主入口：有 LLM 用 LLM 优化，否则直接返回原文"""
        if not raw_text or not raw_text.strip():
            return OptimizeResult(
                original=raw_text or "",
                rule_processed="",
                final="",
                used_llm=False,
                confidence=0.0,
            )

        original = raw_text.strip()

        # 尝试 LLM 优化
        llm_result = await self._llm_optimize(original)

        if llm_result:
            return OptimizeResult(
                original=original,
                rule_processed=original,
                final=llm_result,
                used_llm=True,
                confidence=0.0,
            )

        # 无 LLM 或 LLM 失败，直接返回原文
        return OptimizeResult(
            original=original,
            rule_processed=original,
            final=original,
            used_llm=False,
            confidence=0.0,
        )

    async def _llm_optimize(self, raw_text: str) -> Optional[str]:
        """LLM 语义优化 — 将口语化文本转为标准指令"""
        import httpx
        from app.config import settings

        if not settings.LLM_API_KEY:
            return None

        system_prompt = self._build_system_prompt()

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
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
                            {"role": "user", "content": raw_text},
                        ],
                        "temperature": 0.1,
                        "max_tokens": 200,
                    },
                )
                response.raise_for_status()
                result = response.json()
                return result["choices"][0]["message"]["content"].strip()
        except Exception as e:
            logger.warning(f"LLM 优化失败: {e}")
            return None

    def _build_system_prompt(self) -> str:
        return """你是一个语音绘图指令优化器。将口语化的语音输入转换为简洁的标准绘图指令。

规则：
1. 去除语气词、重复、口误、客套话
2. 保留核心意图和参数
3. 输出简洁的指令文本

支持的操作：创建、删除、移动、放大、缩小、改颜色、加文字、撤销、重做
支持的形状：长方形、圆形、椭圆、三角形、菱形、线条、箭头

示例：
输入：嗯那个帮我画一个红色的长方形就是那种大一点的
输出：画一个红色的长方形，大一点

输入：把那个蓝色的圆弄掉
输出：删除蓝色圆形

输入：emmm就是把那个方块移到右边去
输出：移动方块到右边

输入：刚才那个变大一点
输出：刚才那个放大

输入：画个粉红色的三角形放在中间
输出：画一个粉红色的三角形放在中间

输入：我们来一个蓝色的圆形
输出：画一个蓝色的圆形"""
