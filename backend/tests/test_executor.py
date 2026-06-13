"""指令执行器单元测试"""
import pytest
from app.models import Command, OperationType, ShapeType, CanvasState
from app.executor import CommandExecutor


class TestExecutor:
    """指令执行器测试"""

    def setup_method(self):
        self.executor = CommandExecutor()

    def test_create_shape(self):
        """测试创建图形"""
        command = Command(
            operation=OperationType.CREATE,
            shape_type=ShapeType.RECT,
            properties={"x": 100, "y": 200, "width": 150, "height": 80}
        )
        result = self.executor.execute(command)
        assert len(result.shapes) == 1
        assert result.shapes[0].type == ShapeType.RECT
        assert result.shapes[0].x == 100
        assert result.shapes[0].y == 200
        assert result.selected_id == result.shapes[0].id

    def test_create_multiple_shapes(self):
        """测试创建多个图形"""
        for shape_type in [ShapeType.RECT, ShapeType.CIRCLE, ShapeType.TRIANGLE]:
            command = Command(operation=OperationType.CREATE, shape_type=shape_type)
            self.executor.execute(command)
        assert len(self.executor.state.shapes) == 3

    def test_delete_shape(self):
        """测试删除图形"""
        # 先创建
        create_cmd = Command(operation=OperationType.CREATE, shape_type=ShapeType.RECT)
        result = self.executor.execute(create_cmd)
        shape_id = result.shapes[0].id

        # 再删除
        delete_cmd = Command(operation=OperationType.DELETE, target_id=shape_id)
        result = self.executor.execute(delete_cmd)
        assert len(result.shapes) == 0
        assert result.selected_id is None

    def test_move_shape(self):
        """测试移动图形"""
        create_cmd = Command(operation=OperationType.CREATE, shape_type=ShapeType.RECT)
        result = self.executor.execute(create_cmd)
        shape_id = result.shapes[0].id

        move_cmd = Command(
            operation=OperationType.MOVE,
            target_id=shape_id,
            properties={"x": 300, "y": 400}
        )
        result = self.executor.execute(move_cmd)
        assert result.shapes[0].x == 300
        assert result.shapes[0].y == 400

    def test_resize_shape(self):
        """测试调整大小"""
        create_cmd = Command(operation=OperationType.CREATE, shape_type=ShapeType.RECT)
        result = self.executor.execute(create_cmd)
        shape_id = result.shapes[0].id

        resize_cmd = Command(
            operation=OperationType.RESIZE,
            target_id=shape_id,
            properties={"width": 200, "height": 150}
        )
        result = self.executor.execute(resize_cmd)
        assert result.shapes[0].width == 200
        assert result.shapes[0].height == 150

    def test_set_color(self):
        """测试设置颜色"""
        create_cmd = Command(operation=OperationType.CREATE, shape_type=ShapeType.RECT)
        result = self.executor.execute(create_cmd)
        shape_id = result.shapes[0].id

        color_cmd = Command(
            operation=OperationType.SET_COLOR,
            target_id=shape_id,
            properties={"fill": "#FF0000", "stroke": "#00FF00"}
        )
        result = self.executor.execute(color_cmd)
        assert result.shapes[0].fill == "#FF0000"
        assert result.shapes[0].stroke == "#00FF00"

    def test_set_text(self):
        """测试设置文本"""
        create_cmd = Command(operation=OperationType.CREATE, shape_type=ShapeType.RECT)
        result = self.executor.execute(create_cmd)
        shape_id = result.shapes[0].id

        text_cmd = Command(
            operation=OperationType.SET_TEXT,
            target_id=shape_id,
            properties={"text": "Hello"}
        )
        result = self.executor.execute(text_cmd)
        assert result.shapes[0].text == "Hello"

    def test_undo(self):
        """测试撤销"""
        # 创建一个图形
        create_cmd = Command(operation=OperationType.CREATE, shape_type=ShapeType.RECT)
        self.executor.execute(create_cmd)
        assert len(self.executor.state.shapes) == 1

        # 撤销
        undo_cmd = Command(operation=OperationType.UNDO)
        result = self.executor.execute(undo_cmd)
        assert len(result.shapes) == 0

    def test_redo(self):
        """测试重做"""
        # 创建 → 撤销 → 重做
        create_cmd = Command(operation=OperationType.CREATE, shape_type=ShapeType.RECT)
        self.executor.execute(create_cmd)

        self.executor.execute(Command(operation=OperationType.UNDO))
        assert len(self.executor.state.shapes) == 0

        result = self.executor.execute(Command(operation=OperationType.REDO))
        assert len(result.shapes) == 1

    def test_delete_nonexistent(self):
        """测试删除不存在的图形"""
        cmd = Command(operation=OperationType.DELETE, target_id="nonexistent")
        result = self.executor.execute(cmd)
        assert len(result.shapes) == 0
