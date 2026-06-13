"""优化器单元测试"""
import pytest
from app.optimizer import VoiceOptimizer
from app.models import OptimizeResult


class TestOptimize:
    """optimize 主入口测试"""

    def setup_method(self):
        self.opt = VoiceOptimizer()

    @pytest.mark.asyncio
    async def test_empty_input(self):
        """空输入"""
        result = await self.opt.optimize("")
        assert result.original == ""
        assert result.final == ""
        assert result.used_llm is False

    @pytest.mark.asyncio
    async def test_returns_optimize_result(self):
        """返回 OptimizeResult 结构"""
        result = await self.opt.optimize("画一个红色的长方形")
        assert isinstance(result, OptimizeResult)
        assert result.original == "画一个红色的长方形"
        assert result.final != ""
        assert isinstance(result.used_llm, bool)

    @pytest.mark.asyncio
    async def test_no_llm_returns_original(self):
        """无 LLM 时返回原文（无 API KEY 时）"""
        result = await self.opt.optimize("画一个红色的长方形")
        # 如果没有配置 LLM_API_KEY，应该返回原文
        if not result.used_llm:
            assert result.final == "画一个红色的长方形"

    @pytest.mark.asyncio
    async def test_whitespace_input(self):
        """纯空格输入"""
        result = await self.opt.optimize("   ")
        assert result.final == ""
