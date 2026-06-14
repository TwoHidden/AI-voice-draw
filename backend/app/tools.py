"""绘图工具定义 - 供 LLM Function Calling 使用"""
import logging
from typing import Any

logger = logging.getLogger(__name__)


def calculate_polygon_lines(cx: float, cy: float, r: float, n: int) -> list[dict]:
    """计算正N边形的N条线段坐标"""
    import math

    points = []
    for i in range(n):
        angle = (i * 360 / n - 90) * math.pi / 180
        points.append({
            "x": cx + r * math.cos(angle),
            "y": cy + r * math.sin(angle)
        })

    lines = []
    for i in range(n):
        start = points[i]
        end = points[(i + 1) % n]
        lines.append({
            "x": start["x"],
            "y": start["y"],
            "width": end["x"] - start["x"],
            "height": end["y"] - start["y"]
        })
    return lines


def calculate_star_lines(cx: float, cy: float, outer_r: float, inner_r: float = None) -> list[dict]:
    """计算五角星的5条线段坐标"""
    import math
    if inner_r is None:
        inner_r = outer_r * 0.382  # 黄金比例

    # 计算5个外顶点（不需要内顶点来画五角星）
    outer_points = []
    for i in range(5):
        angle = (i * 72 - 90) * math.pi / 180
        outer_points.append({
            "x": cx + outer_r * math.cos(angle),
            "y": cy + outer_r * math.sin(angle)
        })

    # 五角星连线顺序：0→2→4→1→3→0（跳过一个顶点连接）
    connection_order = [0, 2, 4, 1, 3, 0]

    lines = []
    for i in range(5):
        start = outer_points[connection_order[i]]
        end = outer_points[connection_order[i + 1]]
        lines.append({
            "x": start["x"],
            "y": start["y"],
            "width": end["x"] - start["x"],
            "height": end["y"] - start["y"]
        })
    return lines

# 颜色映射表
COLOR_MAP = {
    "红": "#FF0000", "红色": "#FF0000", "red": "#FF0000",
    "蓝": "#0000FF", "蓝色": "#0000FF", "blue": "#0000FF",
    "绿": "#00FF00", "绿色": "#00FF00", "green": "#00FF00",
    "黄": "#FFFF00", "黄色": "#FFFF00", "yellow": "#FFFF00",
    "紫": "#800080", "紫色": "#800080", "purple": "#800080",
    "橙": "#FFA500", "橙色": "#FFA500", "orange": "#FFA500",
    "粉": "#FFC0CB", "粉色": "#FFC0CB", "pink": "#FFC0CB",
    "黑": "#000000", "黑色": "#000000", "black": "#000000",
    "白": "#FFFFFF", "白色": "#FFFFFF", "white": "#FFFFFF",
    "灰": "#808080", "灰色": "#808080", "gray": "#808080",
    "深蓝": "#00008B", "浅蓝": "#ADD8E6",
    "深红": "#8B0000", "浅红": "#FFB6C1",
    "深绿": "#006400", "浅绿": "#90EE90",
}

# Tools Schema (OpenAI Function Calling 格式)
TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "create_shape",
            "description": "创建一个新的图形。支持长方形、圆形、椭圆、三角形、菱形、线条、箭头、五角星、曲线、六边形。",
            "parameters": {
                "type": "object",
                "properties": {
                    "shape_type": {
                        "type": "string",
                        "enum": ["rect", "circle", "ellipse", "triangle", "diamond", "line", "arrow", "star", "curve", "hexagon"],
                        "description": "图形类型：rect(长方形), circle(圆形), ellipse(椭圆), triangle(三角形), diamond(菱形), line(线条), arrow(箭头), star(五角星), curve(曲线), hexagon(六边形)"
                    },
                    "fill": {
                        "type": "string",
                        "description": "填充颜色，十六进制格式，如 #FF0000"
                    },
                    "stroke": {
                        "type": "string",
                        "description": "边框颜色，十六进制格式"
                    },
                    "x": {
                        "type": "number",
                        "description": "X坐标，默认100"
                    },
                    "y": {
                        "type": "number",
                        "description": "Y坐标，默认80"
                    },
                    "width": {
                        "type": "number",
                        "description": "宽度，默认200"
                    },
                    "height": {
                        "type": "number",
                        "description": "高度，默认150"
                    }
                },
                "required": ["shape_type"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_shape",
            "description": "删除指定图形或最近创建的图形",
            "parameters": {
                "type": "object",
                "properties": {
                    "target_id": {
                        "type": "string",
                        "description": "要删除的图形ID"
                    },
                    "shape_type": {
                        "type": "string",
                        "enum": ["rect", "circle", "ellipse", "triangle", "diamond", "line", "arrow", "star", "curve"],
                        "description": "删除指定类型的最近一个图形"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "move_shape",
            "description": "移动图形到新位置",
            "parameters": {
                "type": "object",
                "properties": {
                    "target_id": {
                        "type": "string",
                        "description": "要移动的图形ID"
                    },
                    "x": {
                        "type": "number",
                        "description": "新的X坐标"
                    },
                    "y": {
                        "type": "number",
                        "description": "新的Y坐标"
                    }
                },
                "required": ["target_id", "x", "y"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "resize_shape",
            "description": "调整图形大小，可以指定具体尺寸或缩放比例",
            "parameters": {
                "type": "object",
                "properties": {
                    "target_id": {
                        "type": "string",
                        "description": "要调整的图形ID"
                    },
                    "width": {
                        "type": "number",
                        "description": "新的宽度"
                    },
                    "height": {
                        "type": "number",
                        "description": "新的高度"
                    },
                    "scale": {
                        "type": "number",
                        "description": "缩放比例，如1.5表示放大50%，0.5表示缩小50%"
                    }
                },
                "required": ["target_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "set_color",
            "description": "修改图形颜色",
            "parameters": {
                "type": "object",
                "properties": {
                    "target_id": {
                        "type": "string",
                        "description": "要修改的图形ID"
                    },
                    "fill": {
                        "type": "string",
                        "description": "新的填充颜色，十六进制格式"
                    },
                    "stroke": {
                        "type": "string",
                        "description": "新的边框颜色，十六进制格式"
                    }
                },
                "required": ["target_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "set_text",
            "description": "为图形添加或修改文字",
            "parameters": {
                "type": "object",
                "properties": {
                    "target_id": {
                        "type": "string",
                        "description": "要添加文字的图形ID"
                    },
                    "text": {
                        "type": "string",
                        "description": "文字内容"
                    }
                },
                "required": ["target_id", "text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_star_with_lines",
            "description": "用5条线段画一个五角星。当用户说'用线段画五角星'、'用线段画星形'时使用此工具。",
            "parameters": {
                "type": "object",
                "properties": {
                    "stroke": {
                        "type": "string",
                        "description": "线段颜色，十六进制格式，默认 #000000"
                    },
                    "x": {
                        "type": "number",
                        "description": "中心点X坐标，默认175"
                    },
                    "y": {
                        "type": "number",
                        "description": "中心点Y坐标，默认155"
                    },
                    "size": {
                        "type": "number",
                        "description": "五角星大小（外接圆半径），默认75"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_polygon_with_lines",
            "description": "用线段画正多边形。当用户说'用线段画六边形'、'用线段画五边形'等时使用此工具。",
            "parameters": {
                "type": "object",
                "properties": {
                    "sides": {
                        "type": "integer",
                        "description": "边数，如3(三角形)、4(四边形)、5(五边形)、6(六边形)"
                    },
                    "stroke": {
                        "type": "string",
                        "description": "线段颜色，十六进制格式，默认 #000000"
                    },
                    "x": {
                        "type": "number",
                        "description": "中心点X坐标，默认200"
                    },
                    "y": {
                        "type": "number",
                        "description": "中心点Y坐标，默认200"
                    },
                    "size": {
                        "type": "number",
                        "description": "大小（外接圆半径），默认100"
                    }
                },
                "required": ["sides"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "undo",
            "description": "撤销上一步操作",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "redo",
            "description": "重做上一步撤销的操作",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    }
]


def get_system_prompt(canvas_state: str = "") -> str:
    """生成 System Prompt"""
    return f"""你是 AI 绘图助手。根据用户的语音或文字指令，调用工具完成绘图操作。

## 能力
- 创建、删除、移动、缩放、改颜色、加文字
- 撤销、重做
- 理解口语化表达

## 颜色映射
当用户提到颜色时，转换为十六进制：
- 红色 → #FF0000
- 蓝色 → #0000FF
- 绿色 → #00FF00
- 黄色 → #FFFF00
- 紫色 → #800080
- 橙色 → #FFA500
- 粉色 → #FFC0CB
- 黑色 → #000000
- 白色 → #FFFFFF
- 灰色 → #808080

如果用户说"深蓝"、"浅蓝"等，使用合理的变体。

## 位置推断
- 左边 → x: 100
- 中间 → x: 400
- 右边 → x: 600
- 上边 → y: 80
- 下边 → y: 400

## 默认位置
- 不指定位置时，使用 x: 100, y: 80（左上角）

## 默认大小
- 长方形: width=200, height=150
- 圆形: width=150, height=150
- 椭圆: width=200, height=120
- 三角形: width=180, height=160
- 五角星: width=150, height=150
- 曲线: width=200, height=100

## 规则
1. 理解口语化表达，去除语气词、重复、口误
2. 支持一次调用多个工具（如"画一个红色长方形和蓝色圆形"）
3. 如果指令模糊，使用合理默认值而非询问
4. 颜色必须是十六进制格式
5. 只调用工具，不要输出额外解释
6. "画五角星"、"画星形" → 使用 create_shape + star 类型
7. "用线段画五角星"、"用线段画星形" → 使用 create_star_with_lines 工具
8. "曲线"、"弧线"、"弯线" → 使用 create_shape + curve 类型
9. "六边形"、"正六边形"、"六角形" → 使用 create_shape + hexagon 类型
10. "用线段画六边形"、"用线段画五边形"等 → 使用 create_polygon_with_lines 工具，sides 参数为边数

## 当前画布状态
{canvas_state}
"""
