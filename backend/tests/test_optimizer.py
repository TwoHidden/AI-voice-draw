"""优化器单元测试"""
import pytest
from app.optimizer import VoiceOptimizer


class TestRulePreprocess:
    """规则预处理测试"""

    def setup_method(self):
        self.optimizer = VoiceOptimizer()

    def test_remove_filler_words(self):
        """测试去除填充词"""
        result = self.optimizer.rule_preprocess("嗯那个画一个圆")
        assert "嗯" not in result
        assert "那个" not in result
        assert "circle" in result

    def test_colloquial_mapping(self):
        """测试口语化映射"""
        result = self.optimizer.rule_preprocess("画一个长方形")
        assert "创建" in result
        assert "rect" in result

    def test_shape_standardization(self):
        """测试形状名标准化"""
        result = self.optimizer.rule_preprocess("画一个圆形")
        assert "circle" in result

    def test_color_standardization(self):
        """测试颜色标准化"""
        result = self.optimizer.rule_preprocess("红色的长方形")
        assert "#FF0000" in result
        assert "rect" in result

    def test_extract_intent(self):
        """测试意图提取"""
        assert self.optimizer.extract_intent_hint("画一个圆") == "create"
        assert self.optimizer.extract_intent_hint("删掉那个") == "delete"
        assert self.optimizer.extract_intent_hint("移到左边") == "move"
        assert self.optimizer.extract_intent_hint("放大一点") == "resize"
        assert self.optimizer.extract_intent_hint("变成红色") == "setColor"
        assert self.optimizer.extract_intent_hint("撤销") == "undo"

    def test_empty_input(self):
        """测试空输入"""
        assert self.optimizer.rule_preprocess("") == ""
        assert self.optimizer.rule_preprocess("   ") == ""
