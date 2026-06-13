"""指令执行器 - 执行解析后的图形操作"""
import uuid
from typing import Optional
from app.models import Shape, Command, CanvasState, OperationType, ShapeType


class CommandExecutor:
    """执行图形操作指令，维护画布状态和撤销/重做栈"""

    def __init__(self):
        self.state = CanvasState()
        self.undo_stack: list[CanvasState] = []
        self.redo_stack: list[CanvasState] = []

    def execute(self, command: Command) -> CanvasState:
        """执行指令，返回新状态"""
        op = command.operation

        if op == OperationType.UNDO:
            return self.undo()
        elif op == OperationType.REDO:
            return self.redo()

        # 保存当前状态用于撤销
        saved_state = self.state.model_copy(deep=True)

        handlers = {
            OperationType.CREATE: self._create,
            OperationType.DELETE: self._delete,
            OperationType.MOVE: self._move,
            OperationType.RESIZE: self._resize,
            OperationType.SET_COLOR: self._set_color,
            OperationType.SET_TEXT: self._set_text,
        }

        handler = handlers.get(op)
        if handler:
            handler(command)

        # 只有状态实际变化时才推入 undo 栈
        if self.state.model_dump() != saved_state.model_dump():
            self.undo_stack.append(saved_state)
            self.redo_stack.clear()

        return self.state

    def _create(self, command: Command):
        """创建图形"""
        shape_type = command.shape_type or ShapeType.RECT
        props = command.properties
        shape = Shape(
            id=str(uuid.uuid4()),
            type=shape_type,
            x=props.get("x", 100.0),
            y=props.get("y", 100.0),
            width=props.get("width", 100.0),
            height=props.get("height", 100.0),
            fill=props.get("fill", "#4A90D9"),
            stroke=props.get("stroke", "#2C3E50"),
            text=props.get("text", ""),
        )
        self.state.shapes.append(shape)
        self.state.selected_id = shape.id

    def _delete(self, command: Command):
        """删除图形"""
        target = command.target_id or self.state.selected_id
        if target:
            self.state.shapes = [s for s in self.state.shapes if s.id != target]
            if self.state.selected_id == target:
                self.state.selected_id = self.state.shapes[-1].id if self.state.shapes else None

    def _move(self, command: Command):
        """移动图形"""
        target = command.target_id or self.state.selected_id
        shape = self._find_shape(target)
        if shape:
            shape.x = command.properties.get("x", shape.x)
            shape.y = command.properties.get("y", shape.y)

    def _resize(self, command: Command):
        """调整大小"""
        target = command.target_id or self.state.selected_id
        shape = self._find_shape(target)
        if shape:
            shape.width = command.properties.get("width", shape.width)
            shape.height = command.properties.get("height", shape.height)

    def _set_color(self, command: Command):
        """设置颜色"""
        target = command.target_id or self.state.selected_id
        shape = self._find_shape(target)
        if shape:
            shape.fill = command.properties.get("fill", shape.fill)
            shape.stroke = command.properties.get("stroke", shape.stroke)

    def _set_text(self, command: Command):
        """设置文本"""
        target = command.target_id or self.state.selected_id
        shape = self._find_shape(target)
        if shape:
            shape.text = command.properties.get("text", shape.text)

    def undo(self) -> CanvasState:
        """撤销"""
        if self.undo_stack:
            self.redo_stack.append(self.state.model_copy(deep=True))
            self.state = self.undo_stack.pop()
        return self.state

    def redo(self) -> CanvasState:
        """重做"""
        if self.redo_stack:
            self.undo_stack.append(self.state.model_copy(deep=True))
            self.state = self.redo_stack.pop()
        return self.state

    def _find_shape(self, shape_id: Optional[str]) -> Optional[Shape]:
        """查找图形"""
        if not shape_id:
            return None
        for shape in self.state.shapes:
            if shape.id == shape_id:
                return shape
        return None
