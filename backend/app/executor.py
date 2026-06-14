"""指令执行器 - 执行解析后的图形操作"""
import json
import logging
import uuid
from typing import Any, Optional
from app.models import Shape, Command, CanvasState, OperationType, ShapeType

logger = logging.getLogger(__name__)


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

    def get_state_summary(self) -> str:
        """返回画布状态的文字摘要，供 LLM 理解当前状态"""
        if not self.state.shapes:
            return "画布为空，没有任何图形。"

        lines = [f"画布上有 {len(self.state.shapes)} 个图形："]
        for i, shape in enumerate(self.state.shapes, 1):
            color = shape.fill or "无填充"
            lines.append(f"{i}. {shape.type.value} (ID: {shape.id}), 颜色: {color}, 位置: ({shape.x}, {shape.y}), 大小: {shape.width}x{shape.height}")
        if self.state.selected_id:
            lines.append(f"当前选中: {self.state.selected_id}")
        return "\n".join(lines)

    def execute_tool_call(self, tool_call: dict[str, Any]) -> CanvasState:
        """执行单个工具调用，返回新状态"""
        func = tool_call.get("function", {})
        name = func.get("name", "")
        args_str = func.get("arguments", "{}")

        try:
            args = json.loads(args_str) if isinstance(args_str, str) else args_str
        except json.JSONDecodeError:
            args = {}

        logger.info(f"执行工具: {name}({args})")

        if name == "create_shape":
            return self._tool_create(args)
        elif name == "create_star_with_lines":
            return self._tool_create_star_with_lines(args)
        elif name == "delete_shape":
            return self._tool_delete(args)
        elif name == "move_shape":
            return self._tool_move(args)
        elif name == "resize_shape":
            return self._tool_resize(args)
        elif name == "set_color":
            return self._tool_set_color(args)
        elif name == "set_text":
            return self._tool_set_text(args)
        elif name == "undo":
            return self.undo()
        elif name == "redo":
            return self.redo()
        else:
            logger.warning(f"未知工具: {name}")
            return self.state

    def _tool_create(self, args: dict) -> CanvasState:
        """工具调用：创建图形"""
        shape_type_str = args.get("shape_type", "rect")
        try:
            shape_type = ShapeType(shape_type_str)
        except ValueError:
            shape_type = ShapeType.RECT

        # 根据形状类型设置默认大小
        default_sizes = {
            "rect": (200.0, 150.0),
            "circle": (150.0, 150.0),
            "ellipse": (200.0, 120.0),
            "triangle": (180.0, 160.0),
            "diamond": (150.0, 150.0),
            "line": (200.0, 100.0),
            "arrow": (200.0, 100.0),
            "star": (150.0, 150.0),
            "curve": (200.0, 100.0),
        }
        default_w, default_h = default_sizes.get(shape_type_str, (200.0, 150.0))

        command = Command(
            operation=OperationType.CREATE,
            shape_type=shape_type,
            properties={
                "x": args.get("x", 100.0),
                "y": args.get("y", 80.0),
                "width": args.get("width", default_w),
                "height": args.get("height", default_h),
                "fill": args.get("fill", "#4A90D9"),
                "stroke": args.get("stroke", "#2C3E50"),
            }
        )
        return self.execute(command)

    def _tool_create_star_with_lines(self, args: dict) -> CanvasState:
        """工具调用：用5条线段画五角星"""
        from app.tools import calculate_star_lines

        cx = args.get("x", 175.0)
        cy = args.get("y", 155.0)
        size = args.get("size", 75.0)
        stroke = args.get("stroke", "#000000")

        # 计算5条线段
        lines = calculate_star_lines(cx, cy, size)

        # 保存当前状态用于撤销
        saved_state = self.state.model_copy(deep=True)

        # 创建5条线段
        for line in lines:
            shape = Shape(
                id=str(uuid.uuid4()),
                type=ShapeType.LINE,
                x=line["x"],
                y=line["y"],
                width=line["width"],
                height=line["height"],
                fill="none",
                stroke=stroke,
                text="",
            )
            self.state.shapes.append(shape)

        # 推入 undo 栈
        if self.state.model_dump() != saved_state.model_dump():
            self.undo_stack.append(saved_state)
            self.redo_stack.clear()

        return self.state

    def _tool_delete(self, args: dict) -> CanvasState:
        """工具调用：删除图形"""
        target_id = args.get("target_id")
        shape_type_str = args.get("shape_type")

        # 如果没有指定 target_id，按形状类型删除最近一个
        if not target_id and shape_type_str:
            for shape in reversed(self.state.shapes):
                if shape.type.value == shape_type_str:
                    target_id = shape.id
                    break

        command = Command(
            operation=OperationType.DELETE,
            target_id=target_id or self.state.selected_id,
            properties={}
        )
        return self.execute(command)

    def _tool_move(self, args: dict) -> CanvasState:
        """工具调用：移动图形"""
        command = Command(
            operation=OperationType.MOVE,
            target_id=args.get("target_id"),
            properties={"x": args.get("x"), "y": args.get("y")}
        )
        return self.execute(command)

    def _tool_resize(self, args: dict) -> CanvasState:
        """工具调用：调整大小"""
        target_id = args.get("target_id")
        width = args.get("width")
        height = args.get("height")
        scale = args.get("scale")

        # 如果指定了缩放比例，计算新的宽高
        if scale and target_id:
            shape = self._find_shape(target_id)
            if shape:
                width = shape.width * scale
                height = shape.height * scale

        command = Command(
            operation=OperationType.RESIZE,
            target_id=target_id,
            properties={"width": width, "height": height}
        )
        return self.execute(command)

    def _tool_set_color(self, args: dict) -> CanvasState:
        """工具调用：设置颜色"""
        command = Command(
            operation=OperationType.SET_COLOR,
            target_id=args.get("target_id"),
            properties={"fill": args.get("fill"), "stroke": args.get("stroke")}
        )
        return self.execute(command)

    def _tool_set_text(self, args: dict) -> CanvasState:
        """工具调用：设置文字"""
        command = Command(
            operation=OperationType.SET_TEXT,
            target_id=args.get("target_id"),
            properties={"text": args.get("text", "")}
        )
        return self.execute(command)
