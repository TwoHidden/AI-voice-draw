"""语音指令优化器 - 规则引擎为主 + LLM 兜底"""
import logging
import re
from typing import Optional
from app.models import OptimizeResult

logger = logging.getLogger(__name__)


class VoiceOptimizer:
    """语音指令优化器 — 规则引擎管道 + LLM 优化（逐步构建中）"""

    # 填充词/语气词
    FILLER_WORDS = [
        "嗯", "啊", "呃", "那个", "就是", "emmm", "ummm", "umm",
        "然后", "然后呢", "就是说", "怎么说呢", "对对对", "好的",
        "这个", "呢", "吧", "呀", "嘛",
    ]

    # 动词标准化映射
    VERB_MAP = {
        "画一个": "创建", "画个": "创建", "弄个": "创建",
        "搞个": "创建", "来个": "创建", "做个": "创建", "创建一个": "创建",
        "删掉": "删除", "去掉": "删除", "弄掉": "删除", "搞掉": "删除",
        "拿掉": "删除",
        "挪一下": "移动", "挪到": "移动", "移到": "移动",
        "搬到": "移动", "放到": "移动", "放那": "移动", "放那儿": "移动",
        "放大": "resize", "缩小": "resize", "变大": "resize", "变小": "resize",
        "改成": "setColor", "变成": "setColor", "换颜色": "setColor",
        "写上": "setText", "加上字": "setText", "标注": "setText",
        "撤销": "undo", "后悔了": "undo", "上一步": "undo",
        "重做": "redo", "恢复": "redo",
    }

    # 形状标准化映射
    SHAPE_MAP = {
        "长方形": "rect", "方块": "rect", "方的": "rect", "矩形": "rect",
        "正方形": "rect", "方形": "rect",
        "圆": "circle", "圆形": "circle", "圆圈": "circle", "圆的": "circle",
        "椭圆": "ellipse", "椭圆形": "ellipse",
        "三角": "triangle", "三角形": "triangle", "三角的": "triangle",
        "菱形": "diamond", "菱形的": "diamond",
        "线": "line", "线条": "line", "直线": "line",
        "箭头": "arrow", "箭": "arrow",
    }

    # 颜色标准化映射
    COLOR_MAP = {
        "红色": "#FF0000", "红": "#FF0000", "红的": "#FF0000",
        "蓝色": "#0000FF", "蓝": "#0000FF", "蓝的": "#0000FF",
        "绿色": "#00CC00", "绿": "#00CC00", "绿的": "#00CC00",
        "黄色": "#FFD700", "黄": "#FFD700", "黄的": "#FFD700",
        "紫色": "#9933FF", "紫": "#9933FF", "紫的": "#9933FF",
        "橙色": "#FF6600", "橙": "#FF6600", "橙的": "#FF6600",
        "黑色": "#000000", "黑": "#000000",
        "白色": "#FFFFFF", "白": "#FFFFFF",
        "粉色": "#FF69B4", "粉": "#FF69B4", "粉红": "#FF69B4",
        "灰色": "#808080", "灰": "#808080",
        "棕色": "#8B4513", "棕": "#8B4513", "褐色": "#8B4513",
    }

    # 相对位置映射
    POSITION_MAP = {
        "右边": {"x": "+200"}, "左边": {"x": "-200"},
        "上面": {"y": "-200"}, "下面": {"y": "+200"},
        "右上": {"x": "+200", "y": "-200"}, "左下": {"x": "-200", "y": "+200"},
        "左上": {"x": "-200", "y": "-200"}, "右下": {"x": "+200", "y": "+200"},
        "中间": {"x": "400", "y": "300"}, "居中": {"x": "400", "y": "300"},
        "右边去": {"x": "+200"}, "左边去": {"x": "-200"},
    }

    # 相对尺寸映射
    SCALE_MAP = {
        "大一点": 1.3, "大一些": 1.3, "大点": 1.3, "大一点的": 1.3,
        "小一点": 0.7, "小一些": 0.7, "小点": 0.7, "小一点的": 0.7,
        "放大": 1.5, "缩小": 0.5,
        "很大": 2.0, "很小": 0.3,
        "大两倍": 2.0, "小一半": 0.5, "缩小一半": 0.5,
    }

    # 指代消解模式
    REFERENCE_PATTERNS = [
        (r"刚才那个|最后那个|最后画的|刚才画的", "last_created"),
        (r"第一个", "index:0"),
        (r"第二个", "index:1"),
        (r"第三个", "index:2"),
    ]

    def denoise(self, text: str) -> str:
        """Layer 1.1: 去噪 — 移除语气词和填充词"""
        if not text or not text.strip():
            return ""
        result = text.strip()
        for filler in self.FILLER_WORDS:
            result = result.replace(filler, "")
        # 清理多余空格
        result = re.sub(r'\s+', ' ', result).strip()
        return result

    def standardize_verbs(self, text: str) -> str:
        """Layer 1.2: 动词标准化"""
        result = text
        # 按长度降序排列，优先匹配长的
        for colloquial, standard in sorted(self.VERB_MAP.items(), key=lambda x: -len(x[0])):
            result = result.replace(colloquial, standard)
        return result

    def standardize_shapes(self, text: str) -> str:
        """Layer 1.3: 形状标准化"""
        result = text
        for alias, standard in sorted(self.SHAPE_MAP.items(), key=lambda x: -len(x[0])):
            result = result.replace(alias, standard)
        return result

    def standardize_colors(self, text: str) -> str:
        """Layer 1.4: 颜色标准化"""
        result = text
        for color_cn, color_hex in sorted(self.COLOR_MAP.items(), key=lambda x: -len(x[0])):
            result = result.replace(color_cn, color_hex)
        return result

    def rule_preprocess(self, text: str) -> str:
        """完整规则预处理管道：去噪 → 动词 → 形状 → 颜色"""
        result = self.denoise(text)
        result = self.standardize_verbs(result)
        result = self.standardize_shapes(result)
        result = self.standardize_colors(result)
        return result

    # 临时保留：供 main.py 使用，将在 Task 5 中替换
    def extract_intent_hint(self, text: str) -> Optional[str]:
        """从文本中提取意图提示（临时保留）"""
        keywords = {
            "create": ["创建", "新建", "添加", "画"],
            "delete": ["删除", "清除", "移除"],
            "move": ["移动", "位移", "调整位置"],
            "resize": ["放大", "缩小", "调整大小"],
            "setColor": ["颜色", "变色", "改色"],
            "setText": ["文字", "文本", "标签"],
            "undo": ["撤销", "撤回", "回退"],
            "redo": ["重做", "恢复"],
        }
        for intent, words in keywords.items():
            for word in words:
                if word in text:
                    return intent
        return None

    async def llm_optimize(self, raw_text: str, intent_hint: Optional[str] = None) -> str:
        """LLM 优化（临时保留，将被 optimize 替代）"""
        return self.rule_preprocess(raw_text)
