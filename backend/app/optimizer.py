"""语音指令优化器 - 规则预处理 + LLM 语义优化"""
import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)


class VoiceOptimizer:
    """语音指令优化器，两层架构：规则预处理 + LLM 语义优化"""

    # 填充词
    FILLER_WORDS = [
        r'(嗯|呃|那个|然后|就是说|怎么说呢)',
        r'(emmm+|umm+|ah+|uh+)',
        r'\s+',
    ]

    # 口语化映射
    COLLOQUIAL_MAP = {
        '画一个': '创建',
        '画个': '创建',
        '弄一个': '创建',
        '搞一个': '创建',
        '整一个': '创建',
        '弄掉': '删除',
        '删掉': '删除',
        '去掉': '删除',
        '拿掉': '删除',
        '挪一下': '移动',
        '挪到': '移动',
        '移到': '移动',
        '放那': '移动',
        '放那儿': '移动',
        '大一点': '放大',
        '小一点': '缩小',
        '大些': '放大',
        '小些': '缩小',
        '变大': '放大',
        '变小': '缩小',
        '整大点': '放大',
        '整小点': '缩小',
    }

    # 标准化形状名映射
    SHAPE_ALIASES = {
        '长方形': 'rect',
        '矩形': 'rect',
        '正方形': 'rect',
        '方块': 'rect',
        '方形': 'rect',
        '圆': 'circle',
        '圆形': 'circle',
        '圈': 'circle',
        '椭圆': 'ellipse',
        '椭圆形': 'ellipse',
        '三角': 'triangle',
        '三角形': 'triangle',
        '菱形': 'diamond',
        '线': 'line',
        '线条': 'line',
        '直线': 'line',
        '箭头': 'arrow',
    }

    # 颜色标准化
    COLOR_MAP = {
        '红色': '#FF0000',
        '红': '#FF0000',
        '蓝色': '#0000FF',
        '蓝': '#0000FF',
        '绿色': '#00FF00',
        '绿': '#00FF00',
        '黄色': '#FFFF00',
        '黄': '#FFFF00',
        '黑色': '#000000',
        '黑': '#000000',
        '白色': '#FFFFFF',
        '白': '#FFFFFF',
        '紫色': '#800080',
        '紫': '#800080',
        '橙色': '#FFA500',
        '橙': '#FFA500',
    }

    def rule_preprocess(self, text: str) -> str:
        """第一层：规则预处理 - 去噪、标准化、意图初判"""
        if not text or not text.strip():
            return ""

        result = text.strip()

        # 1. 去除填充词
        for pattern in self.FILLER_WORDS[:-1]:
            result = re.sub(pattern, '', result)
        result = re.sub(self.FILLER_WORDS[-1], ' ', result).strip()

        # 2. 口语化映射
        for colloquial, standard in self.COLLOQUIAL_MAP.items():
            result = result.replace(colloquial, standard)

        # 3. 形状名标准化
        for alias, standard in self.SHAPE_ALIASES.items():
            result = result.replace(alias, standard)

        # 4. 颜色标准化
        for color_cn, color_hex in self.COLOR_MAP.items():
            result = result.replace(color_cn, color_hex)

        return result

    def extract_intent_hint(self, text: str) -> Optional[str]:
        """从预处理文本中提取意图提示"""
        keywords = {
            'create': ['创建', '新建', '添加', '画'],
            'delete': ['删除', '清除', '移除', '删掉', '弄掉', '去掉', '拿掉'],
            'move': ['移动', '位移', '调整位置', '移到', '挪到', '挪'],
            'resize': ['放大', '缩小', '调整大小', '改变大小'],
            'setColor': ['颜色', '变色', '改色', '变成'],
            'setText': ['文字', '文本', '标签'],
            'undo': ['撤销', '撤回', '回退'],
            'redo': ['重做', '恢复'],
        }

        for intent, words in keywords.items():
            for word in words:
                if word in text:
                    return intent
        return None

    async def llm_optimize(self, raw_text: str, intent_hint: Optional[str] = None) -> str:
        """第二层：LLM 语义优化"""
        import httpx
        from app.config import settings

        if not settings.LLM_API_KEY:
            # 无 API key 时回退到规则预处理
            return self.rule_preprocess(raw_text)

        system_prompt = self._build_system_prompt()
        user_content = raw_text
        if intent_hint:
            user_content = f"[意图提示: {intent_hint}]\n{raw_text}"

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{settings.LLM_BASE_URL}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.LLM_API_KEY}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": settings.LLM_MODEL,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_content},
                        ],
                        "temperature": 0.1,
                        "max_tokens": 200,
                    },
                )
                response.raise_for_status()
                result = response.json()
                return result["choices"][0]["message"]["content"].strip()
        except Exception as e:
            logger.warning(f"LLM 优化失败，回退到规则预处理: {e}")
            return self.rule_preprocess(raw_text)

    def _build_system_prompt(self) -> str:
        return """你是一个语音绘图指令优化器。将用户的口语化语音输入转换为简洁的标准绘图指令。

规则：
1. 去除语气词、重复、口误
2. 保留核心意图和参数
3. 输出简洁的指令文本

示例：
输入：嗯那个帮我画一个红色的长方形就是那种大一点的
输出：创建红色长方形，尺寸放大

输入：把那个蓝色的圆弄掉
输出：删除蓝色圆形

输入：emmm就是把那个方块移到右边去
输出：移动方块到右边"""
