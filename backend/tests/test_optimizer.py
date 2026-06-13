"""优化器单元测试"""
import pytest
from app.optimizer import VoiceOptimizer
from app.models import OptimizeResult


class TestDenoiseLayer:
    """去噪层测试"""

    def setup_method(self):
        self.opt = VoiceOptimizer()

    def test_remove_filler_words(self):
        """去除语气词"""
        result = self.opt.denoise("嗯那个帮我画一个红色的长方形")
        assert "嗯" not in result
        assert "那个" not in result
        assert "画一个红色的长方形" in result

    def test_remove_multiple_fillers(self):
        """去除多个语气词"""
        result = self.opt.denoise("emmm就是然后那个画一个圆")
        assert "emmm" not in result
        assert "就是" not in result
        assert "然后" not in result

    def test_preserve_meaningful_content(self):
        """保留有意义的内容"""
        result = self.opt.denoise("画一个红色的长方形")
        assert "画" in result
        assert "红色" in result
        assert "长方形" in result

    def test_empty_input(self):
        """空输入"""
        assert self.opt.denoise("") == ""
        assert self.opt.denoise("   ") == ""

    def test_pure_filler(self):
        """纯语气词"""
        result = self.opt.denoise("嗯嗯嗯啊啊啊")
        assert result.strip() == ""


class TestVerbStandardize:
    """动词标准化测试"""

    def setup_method(self):
        self.opt = VoiceOptimizer()

    def test_create_verbs(self):
        """创建类动词"""
        for verb in ["画一个", "画个", "弄个", "搞个", "来个", "做个"]:
            result = self.opt.standardize_verbs(f"{verb}圆")
            assert "创建" in result, f"'{verb}' 应标准化为 '创建'"

    def test_delete_verbs(self):
        """删除类动词"""
        for verb in ["删掉", "去掉", "弄掉", "搞掉"]:
            result = self.opt.standardize_verbs(f"{verb}那个圆")
            assert "删除" in result, f"'{verb}' 应标准化为 '删除'"

    def test_move_verbs(self):
        """移动类动词"""
        for verb in ["挪一下", "搬到", "放到", "移到"]:
            result = self.opt.standardize_verbs(f"{verb}右边")
            assert "移动" in result, f"'{verb}' 应标准化为 '移动'"

    def test_undo_redo(self):
        """撤销/重做"""
        assert "undo" in self.opt.standardize_verbs("撤销")
        assert "redo" in self.opt.standardize_verbs("恢复")


class TestShapeColorStandardize:
    """形状和颜色标准化测试"""

    def setup_method(self):
        self.opt = VoiceOptimizer()

    def test_shape_standardize_rect(self):
        """长方形→rect"""
        assert "rect" in self.opt.standardize_shapes("长方形")
        assert "rect" in self.opt.standardize_shapes("方块")
        assert "rect" in self.opt.standardize_shapes("矩形")
        assert "rect" in self.opt.standardize_shapes("正方形")

    def test_shape_standardize_circle(self):
        """圆形→circle"""
        assert "circle" in self.opt.standardize_shapes("圆形")
        assert "circle" in self.opt.standardize_shapes("圆")

    def test_shape_standardize_other(self):
        """其他形状"""
        assert "triangle" in self.opt.standardize_shapes("三角形")
        assert "diamond" in self.opt.standardize_shapes("菱形")
        assert "line" in self.opt.standardize_shapes("线条")
        assert "arrow" in self.opt.standardize_shapes("箭头")

    def test_color_standardize(self):
        """颜色标准化"""
        assert "#FF0000" in self.opt.standardize_colors("红色")
        assert "#0000FF" in self.opt.standardize_colors("蓝色")
        assert "#00CC00" in self.opt.standardize_colors("绿色")
        assert "#000000" in self.opt.standardize_colors("黑色")

    def test_full_rule_pipeline(self):
        """完整规则管道端到端"""
        result = self.opt.rule_preprocess("嗯那个画一个红色的长方形")
        assert "嗯" not in result
        assert "创建" in result
        assert "rect" in result


class TestFuzzyExpression:
    """模糊表达测试"""

    def setup_method(self):
        self.opt = VoiceOptimizer()

    def test_relative_position(self):
        """相对位置解析"""
        for pos_key in ["右边", "左边", "上面", "下面", "中间"]:
            assert pos_key in self.opt.POSITION_MAP

    def test_relative_scale(self):
        """相对尺寸解析"""
        assert self.opt.SCALE_MAP["大一点"] > 1.0
        assert self.opt.SCALE_MAP["小一点"] < 1.0
        assert self.opt.SCALE_MAP["放大"] > self.opt.SCALE_MAP["大一点"]

    def test_reference_patterns(self):
        """指代模式存在"""
        assert len(self.opt.REFERENCE_PATTERNS) > 0
        pattern, target = self.opt.REFERENCE_PATTERNS[0]
        assert target == "last_created"


class TestConfidence:
    """置信度评分测试"""

    def setup_method(self):
        self.opt = VoiceOptimizer()

    def test_high_confidence_simple_command(self):
        """简单命令高置信度"""
        result = self.opt.calculate_confidence(
            "画一个红色的长方形",
            "创建红色rect",
            matched_rules=["verb", "color", "shape"],
        )
        assert result >= 0.7

    def test_low_confidence_ambiguous(self):
        """模糊表达低置信度"""
        result = self.opt.calculate_confidence(
            "嗯那个就是那个弄一下",
            "弄一下",
            matched_rules=["filler"],
        )
        assert result < 0.7

    def test_confidence_range(self):
        """置信度在 0-1 范围内"""
        result = self.opt.calculate_confidence("test", "test", [])
        assert 0.0 <= result <= 1.0


class TestReferenceResolution:
    """指代消解测试"""

    def setup_method(self):
        self.opt = VoiceOptimizer()

    def test_last_created_reference(self):
        """'刚才那个'指代最后创建的图形"""
        result = self.opt.resolve_references("刚才那个放大")
        assert "last_created" in result or "放大" in result

    def test_no_reference(self):
        """无指代时原文返回"""
        result = self.opt.resolve_references("画一个红色的长方形")
        assert "画" in result or "创建" in result


class TestOptimizeMain:
    """optimize 主入口测试"""

    def setup_method(self):
        self.opt = VoiceOptimizer()

    @pytest.mark.asyncio
    async def test_high_confidence_skips_llm(self):
        """高置信度时跳过 LLM"""
        result = await self.opt.optimize("画一个红色的长方形")
        assert isinstance(result, OptimizeResult)
        assert result.used_llm is False
        assert result.confidence >= 0.7
        assert "创建" in result.final

    @pytest.mark.asyncio
    async def test_empty_input(self):
        """空输入"""
        result = await self.opt.optimize("")
        assert result.original == ""
        assert result.final == ""
        assert result.used_llm is False

    @pytest.mark.asyncio
    async def test_optimize_result_structure(self):
        """返回结构完整"""
        result = await self.opt.optimize("撤销")
        assert result.original == "撤销"
        assert result.rule_processed != ""
        assert result.final != ""
        assert isinstance(result.used_llm, bool)
        assert 0.0 <= result.confidence <= 1.0


class TestEndToEnd:
    """端到端集成测试"""

    def setup_method(self):
        self.opt = VoiceOptimizer()

    @pytest.mark.asyncio
    async def test_simple_create_command(self):
        """简单创建命令 — 高置信度，不调 LLM"""
        result = await self.opt.optimize("画一个红色的长方形")
        assert result.used_llm is False
        assert result.confidence >= 0.7
        assert "创建" in result.final

    @pytest.mark.asyncio
    async def test_colloquial_with_filler(self):
        """口语化命令带语气词"""
        result = await self.opt.optimize("嗯那个帮我画一个红色的长方形就是那种大一点的")
        assert "嗯" not in result.final
        assert "那个" not in result.final
        assert "创建" in result.final

    @pytest.mark.asyncio
    async def test_delete_command(self):
        """删除命令"""
        result = await self.opt.optimize("把那个蓝色的圆弄掉")
        assert "删除" in result.final

    @pytest.mark.asyncio
    async def test_undo_command(self):
        """撤销命令"""
        result = await self.opt.optimize("撤销")
        assert "undo" in result.final
        assert result.used_llm is False

    @pytest.mark.asyncio
    async def test_reference_resolution(self):
        """指代消解"""
        result = await self.opt.optimize("刚才那个弄大一点")
        assert "last_created" in result.rule_processed or "放大" in result.final

    @pytest.mark.asyncio
    async def test_position_expression(self):
        """相对位置表达"""
        result = await self.opt.optimize("画一个圆放到右边")
        assert "创建" in result.final

    @pytest.mark.asyncio
    async def test_scale_expression(self):
        """相对尺寸表达"""
        result = await self.opt.optimize("画一个大一点的长方形")
        assert "创建" in result.final
