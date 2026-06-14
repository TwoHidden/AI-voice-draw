"""数据模型定义 - Pydantic schemas"""
from typing import Optional, Any
from pydantic import BaseModel, Field
from enum import Enum


class ShapeType(str, Enum):
    RECT = "rect"
    CIRCLE = "circle"
    ELLIPSE = "ellipse"
    TRIANGLE = "triangle"
    DIAMOND = "diamond"
    LINE = "line"
    ARROW = "arrow"
    STAR = "star"
    CURVE = "curve"


class OperationType(str, Enum):
    CREATE = "create"
    DELETE = "delete"
    MOVE = "move"
    RESIZE = "resize"
    SET_COLOR = "setColor"
    SET_TEXT = "setText"
    UNDO = "undo"
    REDO = "redo"


class Shape(BaseModel):
    id: str
    type: ShapeType
    x: float = 0.0
    y: float = 0.0
    width: float = Field(default=100.0)  # 允许负数（线段方向）
    height: float = Field(default=100.0)  # 允许负数（线段方向）
    fill: str = "#4A90D9"
    stroke: str = "#2C3E50"
    text: str = ""
    rotation: float = 0.0


class Command(BaseModel):
    """LLM 解析后的指令"""
    operation: OperationType
    shape_type: Optional[ShapeType] = None
    target_id: Optional[str] = None
    properties: dict[str, Any] = Field(default_factory=dict)


class CanvasState(BaseModel):
    shapes: list[Shape] = Field(default_factory=list)
    selected_id: Optional[str] = None


class OptimizeResult(BaseModel):
    """语音指令优化结果"""
    original: str           # ASR 原始文本
    rule_processed: str     # 规则预处理结果
    final: str              # 最终优化结果
    used_llm: bool          # 是否调用了 LLM
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)  # 规则引擎置信度
