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
    width: float = Field(default=100.0, ge=0)
    height: float = Field(default=100.0, ge=0)
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
