"""数据模型测试"""
from app.models import OptimizeResult


def test_optimize_result_creation():
    result = OptimizeResult(
        original="画一个红色的长方形",
        rule_processed="创建红色rect",
        final="创建红色rect",
        used_llm=False,
        confidence=0.8,
    )
    assert result.original == "画一个红色的长方形"
    assert result.used_llm is False
    assert result.confidence == 0.8


def test_optimize_result_defaults():
    result = OptimizeResult(
        original="test",
        rule_processed="test",
        final="test",
        used_llm=False,
        confidence=0.0,
    )
    assert result.used_llm is False
