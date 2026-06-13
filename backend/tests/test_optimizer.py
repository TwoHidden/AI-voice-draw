"""优化器单元测试"""
import pytest
from app.optimizer import VoiceOptimizer


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
