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
        """完整规则预处理管道：指代消解 → 去噪 → 动词 → 形状 → 颜色"""
        result = self.resolve_references(text)
        result = self.denoise(result)
        result = self.standardize_verbs(result)
        result = self.standardize_shapes(result)
        result = self.standardize_colors(result)
        return result

    def calculate_confidence(
        self, original: str, processed: str, matched_rules: list[str]
    ) -> float:
        """计算规则引擎处理的置信度 (0.0 ~ 1.0)"""
        score = 0.0
        if matched_rules:
            score += 0.3
        # 检查是否识别到了形状
        if any(shape in processed for shape in self.SHAPE_MAP.values()):
            score += 0.3
        # 检查是否识别到了操作
        operations = ["创建", "删除", "移动", "resize", "setColor", "setText", "undo", "redo"]
        if any(op in processed for op in operations):
            score += 0.2
        # 检查是否识别到了颜色
        if any(c in processed for c in self.COLOR_MAP.values()):
            score += 0.1
        # 没有大量未识别字符
        if len(processed) <= len(original) * 2:
            score += 0.1
        return min(score, 1.0)

    def resolve_references(self, text: str, canvas_state=None) -> str:
        """指代消解 — 将代词引用转换为具体标识"""
        result = text
        for pattern, target in self.REFERENCE_PATTERNS:
            result = re.sub(pattern, target, result)
        return result

    async def optimize(self, raw_text: str, canvas_state=None) -> OptimizeResult:
        """主入口：规则引擎 → (可选 LLM) → 返回优化结果"""
        if not raw_text or not raw_text.strip():
            return OptimizeResult(
                original=raw_text or "",
                rule_processed="",
                final="",
                used_llm=False,
                confidence=0.0,
            )

        # Layer 1: 规则引擎管道
        matched_rules = []
        original = raw_text.strip()

        # 1. 指代消解
        ref_result = self.resolve_references(original)
        if ref_result != original:
            matched_rules.append("reference")

        # 2. 去噪
        denoised = self.denoise(ref_result)
        if denoised != ref_result:
            matched_rules.append("denoise")

        # 3. 动词标准化
        verb_result = self.standardize_verbs(denoised)
        if verb_result != denoised:
            matched_rules.append("verb")

        # 4. 形状标准化
        shape_result = self.standardize_shapes(verb_result)
        if shape_result != verb_result:
            matched_rules.append("shape")

        # 5. 颜色标准化
        color_result = self.standardize_colors(shape_result)
        if color_result != shape_result:
            matched_rules.append("color")

        rule_processed = color_result

        # 计算置信度
        confidence = self.calculate_confidence(raw_text, rule_processed, matched_rules)

        # Layer 2: 高置信度跳过 LLM
        if confidence >= 0.7:
            logger.info(f"规则引擎置信度 {confidence:.2f} >= 0.7，跳过 LLM")
            return OptimizeResult(
                original=raw_text,
                rule_processed=rule_processed,
                final=rule_processed,
                used_llm=False,
                confidence=confidence,
            )

        # Layer 2: 低置信度，调用 LLM
        logger.info(f"规则引擎置信度 {confidence:.2f} < 0.7，调用 LLM 优化")
        llm_result = await self._llm_optimize(raw_text, rule_processed)
        final = llm_result if llm_result else rule_processed

        return OptimizeResult(
            original=raw_text,
            rule_processed=rule_processed,
            final=final,
            used_llm=llm_result is not None,
            confidence=confidence,
        )

    async def _llm_optimize(self, raw_text: str, rule_processed: str) -> Optional[str]:
        """LLM 语义优化 — 接收规则预处理结果 + 原始文本"""
        import httpx
        from app.config import settings

        if not settings.LLM_API_KEY:
            return None

        system_prompt = self._build_system_prompt()
        user_content = f"[规则预处理结果]\n{rule_processed}\n\n[原始语音]\n{raw_text}"

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
            logger.warning(f"LLM 优化失败: {e}")
            return None

    def _build_system_prompt(self) -> str:
        return """你是一个语音绘图指令优化器。将口语化的语音输入转换为简洁的标准绘图指令。

规则：
1. 去除语气词、重复、口误
2. 保留核心意图和参数
3. 输出简洁的指令文本
4. 颜色使用十六进制代码（如 #FF0000 表示红色）

支持的操作：创建、删除、移动、resize、setColor、setText、undo、redo
支持的形状：rect、circle、ellipse、triangle、diamond、line、arrow

示例：
输入：嗯那个帮我画一个红色的长方形就是那种大一点的
输出：创建红色长方形，放大

输入：把那个蓝色的圆弄掉
输出：删除蓝色圆形

输入：emmm就是把那个方块移到右边去
输出：移动方块到右边

输入：刚才那个变大一点
输出：最后创建的图形放大

输入：画个粉红色的三角形放在中间
输出：创建粉色三角形，放在中间"""

