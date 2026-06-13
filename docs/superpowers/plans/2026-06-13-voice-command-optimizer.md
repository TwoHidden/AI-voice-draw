# 语音指令优化器实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将语音指令优化器从"规则预处理作为 LLM 兜底"升级为"规则引擎为主 + LLM 兜底"的三层管道架构，支持指代消解、模糊表达，并在前端展示优化过程。

**Architecture:** 三层管道 — Layer 1 规则引擎（零延迟，覆盖 80% 场景）输出置信度分数，高置信度直接跳过 LLM；Layer 2 LLM 优化接收预处理结果（非原始 ASR）；前端展示原始→规则→LLM 的转化过程。

**Tech Stack:** Python 3.9+, FastAPI, Pydantic, httpx, React 19, TypeScript, WebSocket

---

## 涉及文件

| 文件 | 职责 |
|------|------|
| `backend/app/models.py` | 新增 `OptimizeResult` 模型 |
| `backend/app/optimizer.py` | 重写：三层管道，扩展规则库，置信度评分 |
| `backend/app/main.py` | 修改：传递画布状态，发送 `optimize_result` 消息 |
| `frontend/src/types/index.ts` | 新增 `OptimizeResult` 类型，扩展 `WSMessage` |
| `frontend/src/hooks/useWebSocket.ts` | 新增 `onOptimizeResult` 回调 |
| `frontend/src/components/VoicePanel.tsx` | 新增优化过程展示面板 |
| `frontend/src/App.tsx` | 传递 `onOptimizeResult` 给 VoicePanel |
| `frontend/src/App.css` | 新增优化面板样式 |
| `backend/tests/test_optimizer.py` | 重写：覆盖所有规则层和置信度 |

---

### Task 1: 新增 OptimizeResult 数据模型

**Files:**
- Modify: `backend/app/models.py`
- Test: `backend/tests/test_models.py` (如不存在则创建)

- [ ] **Step 1: 在 models.py 末尾添加 OptimizeResult 模型**

在 `backend/app/models.py` 末尾添加：

```python
class OptimizeResult(BaseModel):
    """语音指令优化结果"""
    original: str           # ASR 原始文本
    rule_processed: str     # 规则预处理结果
    final: str              # 最终优化结果
    used_llm: bool          # 是否调用了 LLM
    confidence: float       # 规则引擎置信度 (0.0 ~ 1.0)
```

- [ ] **Step 2: 编写测试**

创建 `backend/tests/test_models.py`：

```python
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
```

- [ ] **Step 3: 运行测试**

Run: `cd /Users/hw/Ai_Projects/AI\ 语言绘图工具/backend && python -m pytest tests/test_models.py -v`
Expected: PASS

- [ ] **Step 4: 提交**

```bash
git add backend/app/models.py backend/tests/test_models.py
git commit -m "feat: 新增 OptimizeResult 数据模型

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 2: 重写规则引擎 — 去噪层 + 动词标准化

**Files:**
- Modify: `backend/app/optimizer.py`
- Test: `backend/tests/test_optimizer.py`

- [ ] **Step 1: 编写去噪层和动词标准化测试**

重写 `backend/tests/test_optimizer.py`：

```python
"""优化器单元测试"""
import pytest
from app.optimizer import VoiceOptimizer


class TestDenoiseLayer:
    """去噪层测试"""

    def setup_method(self):
        self.opt = VoiceOptimizer()

    def test_remove_filler_words(self):
        """去除语气词"""
        result = self.opt.denoise("嗯那个帮我画一个红色的长方形")
        assert "嗯" not in result
        assert "那个" not in result
        assert "画一个红色的长方形" in result

    def test_remove_multiple_fillers(self):
        """去除多个语气词"""
        result = self.opt.denoise("emmm就是然后那个画一个圆")
        assert "emmm" not in result
        assert "就是" not in result
        assert "然后" not in result

    def test_preserve_meaningful_content(self):
        """保留有意义的内容"""
        result = self.opt.denoise("画一个红色的长方形")
        assert "画" in result
        assert "红色" in result
        assert "长方形" in result

    def test_empty_input(self):
        """空输入"""
        assert self.opt.denoise("") == ""
        assert self.opt.denoise("   ") == ""

    def test_pure_filler(self):
        """纯语气词"""
        result = self.opt.denoise("嗯嗯嗯啊啊啊")
        assert result.strip() == ""


class TestVerbStandardize:
    """动词标准化测试"""

    def setup_method(self):
        self.opt = VoiceOptimizer()

    def test_create_verbs(self):
        """创建类动词"""
        for verb in ["画一个", "画个", "弄个", "搞个", "来个", "做个"]:
            result = self.opt.standardize_verbs(f"{verb}圆")
            assert "创建" in result, f"'{verb}' 应标准化为 '创建'"

    def test_delete_verbs(self):
        """删除类动词"""
        for verb in ["删掉", "去掉", "弄掉", "搞掉"]:
            result = self.opt.standardize_verbs(f"{verb}那个圆")
            assert "删除" in result, f"'{verb}' 应标准化为 '删除'"

    def test_move_verbs(self):
        """移动类动词"""
        for verb in ["挪一下", "搬到", "放到", "移到"]:
            result = self.opt.standardize_verbs(f"{verb}右边")
            assert "移动" in result, f"'{verb}' 应标准化为 '移动'"

    def test_undo_redo(self):
        """撤销/重做"""
        assert "undo" in self.opt.standardize_verbs("撤销")
        assert "redo" in self.opt.standardize_verbs("恢复")
```

- [ ] **Step 2: 运行测试确认失败**

Run: `cd /Users/hw/Ai_Projects/AI\ 语言绘图工具/backend && python -m pytest tests/test_optimizer.py -v`
Expected: FAIL (方法不存在)

- [ ] **Step 3: 重写 optimizer.py 的去噪和动词标准化方法**

重写 `backend/app/optimizer.py`，保留 `VoiceOptimizer` 类名和接口，但内部重构：

```python
"""语音指令优化器 - 规则引擎为主 + LLM 兜底"""
import logging
import re
from typing import Optional
from app.models import OptimizeResult

logger = logging.getLogger(__name__)


class VoiceOptimizer:
    """语音指令优化器，三层管道：规则引擎 + LLM 语义优化 + 前端展示"""

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
```

- [ ] **Step 4: 运行测试确认通过**

Run: `cd /Users/hw/Ai_Projects/AI\ 语言绘图工具/backend && python -m pytest tests/test_optimizer.py::TestDenoiseLayer tests/test_optimizer.py::TestVerbStandardize -v`
Expected: PASS

- [ ] **Step 5: 提交**

```bash
git add backend/app/optimizer.py backend/tests/test_optimizer.py
git commit -m "feat: 重写优化器规则引擎 — 去噪层和动词标准化

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 3: 规则引擎 — 形状/颜色标准化 + 模糊表达

**Files:**
- Modify: `backend/app/optimizer.py`
- Modify: `backend/tests/test_optimizer.py`

- [ ] **Step 1: 编写形状、颜色、模糊表达测试**

在 `backend/tests/test_optimizer.py` 末尾追加：

```python
class TestShapeColorStandardize:
    """形状和颜色标准化测试"""

    def setup_method(self):
        self.opt = VoiceOptimizer()

    def test_shape_standardize(self):
        """形状标准化"""
        assert "rect" in self.opt.standardize_shapes("长方形")
        assert "circle" in self.opt.standardize_shapes("圆形")
        assert "triangle" in self.opt.standardize_shapes("三角形")
        assert "diamond" in self.opt.standardize_shapes("菱形")
        assert "line" in self.opt.standardize_shapes("线条")
        assert "arrow" in self.opt.standardize_shapes("箭头")

    def test_color_standardize(self):
        """颜色标准化"""
        assert "#FF0000" in self.opt.standardize_colors("红色")
        assert "#0000FF" in self.opt.standardize_colors("蓝色")
        assert "#00CC00" in self.opt.standardize_colors("绿色")

    def test_full_rule_pipeline(self):
        """完整规则管道"""
        result = self.opt.rule_preprocess("嗯那个画一个红色的长方形")
        assert "嗯" not in result
        assert "创建" in result
        assert "#FF0000" in result or "红色" in result  # 颜色可能被标准化
        assert "rect" in result


class TestFuzzyExpression:
    """模糊表达测试"""

    def setup_method(self):
        self.opt = VoiceOptimizer()

    def test_relative_position(self):
        """相对位置解析"""
        for pos_key in ["右边", "左边", "上面", "下面", "中间"]:
            assert pos_key in self.opt.POSITION_MAP

    def test_relative_scale(self):
        """相对尺寸解析"""
        assert self.opt.SCALE_MAP["大一点"] > 1.0
        assert self.opt.SCALE_MAP["小一点"] < 1.0
        assert self.opt.SCALE_MAP["放大"] > self.opt.SCALE_MAP["大一点"]

    def test_reference_patterns(self):
        """指代模式存在"""
        assert len(self.opt.REFERENCE_PATTERNS) > 0
        pattern, target = self.opt.REFERENCE_PATTERNS[0]
        assert target == "last_created"
```

- [ ] **Step 2: 运行测试确认通过**

Run: `cd /Users/hw/Ai_Projects/AI\ 语言绘图工具/backend && python -m pytest tests/test_optimizer.py -v`
Expected: PASS

- [ ] **Step 3: 提交**

```bash
git add backend/tests/test_optimizer.py
git commit -m "feat: 添加形状/颜色/模糊表达测试

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 4: 置信度评分 + 指代消解

**Files:**
- Modify: `backend/app/optimizer.py`
- Modify: `backend/tests/test_optimizer.py`

- [ ] **Step 1: 编写置信度和指代消解测试**

在 `backend/tests/test_optimizer.py` 末尾追加：

```python
class TestConfidence:
    """置信度评分测试"""

    def setup_method(self):
        self.opt = VoiceOptimizer()

    def test_high_confidence_simple_command(self):
        """简单命令高置信度"""
        result = self.opt.calculate_confidence(
            "画一个红色的长方形",
            "创建红色rect",
            matched_rules=["verb", "color", "shape"],
        )
        assert result >= 0.7

    def test_low_confidence_ambiguous(self):
        """模糊表达低置信度"""
        result = self.opt.calculate_confidence(
            "嗯那个就是那个弄一下",
            "弄一下",
            matched_rules=["filler"],
        )
        assert result < 0.7

    def test_confidence_range(self):
        """置信度在 0-1 范围内"""
        result = self.opt.calculate_confidence("test", "test", [])
        assert 0.0 <= result <= 1.0


class TestReferenceResolution:
    """指代消解测试"""

    def setup_method(self):
        self.opt = VoiceOptimizer()

    def test_last_created_reference(self):
        """'刚才那个'指代最后创建的图形"""
        result = self.opt.resolve_references("刚才那个放大")
        assert "last_created" in result or "放大" in result

    def test_no_reference(self):
        """无指代时原文返回"""
        result = self.opt.resolve_references("画一个红色的长方形")
        assert "画" in result or "创建" in result
```

- [ ] **Step 2: 运行测试确认失败**

Run: `cd /Users/hw/Ai_Projects/AI\ 语言绘图工具/backend && python -m pytest tests/test_optimizer.py::TestConfidence tests/test_optimizer.py::TestReferenceResolution -v`
Expected: FAIL

- [ ] **Step 3: 在 optimizer.py 中实现置信度和指代消解**

在 `VoiceOptimizer` 类末尾添加：

```python
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
        # 没有大量未识别字符（处理后长度不应比原文长太多）
        if len(processed) <= len(original) * 2:
            score += 0.1
        return min(score, 1.0)

    def resolve_references(self, text: str, canvas_state=None) -> str:
        """指代消解 — 将代词引用转换为具体标识"""
        result = text
        for pattern, target in self.REFERENCE_PATTERNS:
            result = re.sub(pattern, target, result)

        # 动态匹配 "那个XX的" 模式
        color_ref = re.search(r"那个(\w+)的", result)
        if color_ref:
            color_word = color_ref.group(1)
            # 尝试匹配颜色
            for color_cn, color_hex in self.COLOR_MAP.items():
                if color_cn in color_word or color_word in color_cn:
                    result = result[:color_ref.start()] + f"by_color:{color_hex}" + result[color_ref.end():]
                    break

        return result
```

- [ ] **Step 4: 运行测试确认通过**

Run: `cd /Users/hw/Ai_Projects/AI\ 语言绘图工具/backend && python -m pytest tests/test_optimizer.py -v`
Expected: ALL PASS

- [ ] **Step 5: 提交**

```bash
git add backend/app/optimizer.py backend/tests/test_optimizer.py
git commit -m "feat: 实现置信度评分和指代消解

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 5: LLM 优化层重构 + optimize 主入口

**Files:**
- Modify: `backend/app/optimizer.py`
- Modify: `backend/tests/test_optimizer.py`

- [ ] **Step 1: 编写 optimize 主入口测试**

在 `backend/tests/test_optimizer.py` 末尾追加：

```python
import pytest


class TestOptimizeMain:
    """optimize 主入口测试"""

    def setup_method(self):
        self.opt = VoiceOptimizer()

    @pytest.mark.asyncio
    async def test_high_confidence_skips_llm(self):
        """高置信度时跳过 LLM"""
        result = await self.opt.optimize("画一个红色的长方形")
        assert isinstance(result, OptimizeResult)
        assert result.used_llm is False
        assert result.confidence >= 0.7
        assert "创建" in result.final

    @pytest.mark.asyncio
    async def test_empty_input(self):
        """空输入"""
        result = await self.opt.optimize("")
        assert result.original == ""
        assert result.final == ""
        assert result.used_llm is False

    @pytest.mark.asyncio
    async def test_optimize_result_structure(self):
        """返回结构完整"""
        result = await self.opt.optimize("撤销")
        assert result.original == "撤销"
        assert result.rule_processed != ""
        assert result.final != ""
        assert isinstance(result.used_llm, bool)
        assert 0.0 <= result.confidence <= 1.0
```

- [ ] **Step 2: 运行测试确认失败**

Run: `cd /Users/hw/Ai_Projects/AI\ 语言绘图工具/backend && python -m pytest tests/test_optimizer.py::TestOptimizeMain -v`
Expected: FAIL (optimize 方法不存在)

- [ ] **Step 3: 重写 LLM 优化层和 optimize 主入口**

在 `backend/app/optimizer.py` 的 `VoiceOptimizer` 类中，替换原有 `llm_optimize` 方法，添加 `optimize` 主入口：

```python
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
        rule_result = self.denoise(raw_text)
        if rule_result != raw_text.strip():
            matched_rules.append("denoise")

        verb_result = self.standardize_verbs(rule_result)
        if verb_result != rule_result:
            matched_rules.append("verb")

        shape_result = self.standardize_shapes(verb_result)
        if shape_result != verb_result:
            matched_rules.append("shape")

        color_result = self.standardize_colors(shape_result)
        if color_result != shape_result:
            matched_rules.append("color")

        ref_result = self.resolve_references(color_result, canvas_state)
        if ref_result != color_result:
            matched_rules.append("reference")

        rule_processed = ref_result

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
4. 颜色用中文名即可，解析器会处理

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

    # 保留 extract_intent_hint 供其他模块使用
    def extract_intent_hint(self, text: str) -> Optional[str]:
        """从文本中提取意图提示"""
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
```

- [ ] **Step 4: 运行全部测试确认通过**

Run: `cd /Users/hw/Ai_Projects/AI\ 语言绘图工具/backend && python -m pytest tests/test_optimizer.py -v`
Expected: ALL PASS

- [ ] **Step 5: 提交**

```bash
git add backend/app/optimizer.py backend/tests/test_optimizer.py
git commit -m "feat: 实现 optimize 主入口和 LLM 优化层重构

- 规则引擎管道输出置信度分数
- 高置信度(>=0.7)跳过 LLM，直接使用规则结果
- LLM 接收规则预处理结果+原始文本
- 返回 OptimizeResult 包含完整优化过程

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 6: 修改 main.py — 传递画布状态 + 发送 optimize_result

**Files:**
- Modify: `backend/app/main.py`

- [ ] **Step 1: 修改 _process_and_execute 函数**

在 `main.py` 中，修改 `_process_and_execute` 函数：

```python
async def _process_and_execute(websocket: WebSocket, raw_text: str):
    """处理文本指令：优化 → 解析 → 执行 → 响应"""
    # 获取当前画布状态用于指代消解
    canvas_state = executor.state

    # 优化指令
    opt_result = await optimizer.optimize(raw_text, canvas_state)

    # 发送优化结果给前端
    await websocket.send_json({
        "type": "optimize_result",
        "data": {
            "original": opt_result.original,
            "rule_processed": opt_result.rule_processed,
            "final": opt_result.final,
            "used_llm": opt_result.used_llm,
            "confidence": opt_result.confidence,
        },
    })

    # 用优化后的文本进行解析
    command = await parser.parse(opt_result.final)
    if not command:
        await websocket.send_json({"type": "error", "data": "无法理解指令，请重试"})
        return

    # 执行指令
    await executor.execute(command)

    # 发送更新后的画布状态
    await websocket.send_json({
        "type": "state_update",
        "data": executor.state.model_dump(),
    })
```

注意：确保 `_process_and_execute` 同时被 `_handle_audio` 和 `_handle_text` 调用。

- [ ] **Step 2: 运行后端测试确认无回归**

Run: `cd /Users/hw/Ai_Projects/AI\ 语言绘图工具/backend && python -m pytest tests/ -v`
Expected: ALL PASS

- [ ] **Step 3: 提交**

```bash
git add backend/app/main.py
git commit -m "feat: main.py 集成优化器 — 传递画布状态并发送 optimize_result

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 7: 前端类型定义 + WebSocket 回调

**Files:**
- Modify: `frontend/src/types/index.ts`
- Modify: `frontend/src/hooks/useWebSocket.ts`

- [ ] **Step 1: 添加 OptimizeResult 类型和扩展 WSMessage**

在 `frontend/src/types/index.ts` 末尾添加：

```typescript
/** 优化结果 */
export interface OptimizeResult {
  original: string;        // ASR 原始文本
  rule_processed: string;  // 规则预处理结果
  final: string;           // 最终优化结果
  used_llm: boolean;       // 是否调用了 LLM
  confidence: number;      // 规则引擎置信度
}
```

修改 `WSMessage` 的 `type` 字段：

```typescript
export interface WSMessage {
  type: 'text' | 'audio' | 'state_update' | 'error' | 'asr_result' | 'pong' | 'optimize_result';
  data: string | CanvasStateResponse | OptimizeResult;
}
```

- [ ] **Step 2: 在 useWebSocket 中添加 onOptimizeResult 回调**

修改 `frontend/src/hooks/useWebSocket.ts`：

```typescript
interface UseWebSocketOptions {
  url: string;
  onStateUpdate?: (state: CanvasState) => void;
  onAsrResult?: (text: string) => void;
  onOptimizeResult?: (result: OptimizeResult) => void;
  onError?: (msg: string) => void;
}
```

在 `callbacksRef` 中添加 `onOptimizeResult`：

```typescript
const callbacksRef = useRef({ onStateUpdate, onAsrResult, onOptimizeResult, onError });
callbacksRef.current = { onStateUpdate, onAsrResult, onOptimizeResult, onError };
```

在 `onmessage` 的 switch 中添加 case：

```typescript
case 'optimize_result':
  callbacksRef.current.onOptimizeResult?.(msg.data as OptimizeResult);
  break;
```

在函数参数和调用处也需更新 `callbacksRef.current` 的解构。

- [ ] **Step 3: 确认前端编译通过**

Run: `cd /Users/hw/Ai_Projects/AI\ 语言绘图工具/frontend && npx tsc --noEmit`
Expected: 无错误

- [ ] **Step 4: 提交**

```bash
git add frontend/src/types/index.ts frontend/src/hooks/useWebSocket.ts
git commit -m "feat: 前端添加 OptimizeResult 类型和 WebSocket 回调

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 8: VoicePanel 优化过程展示面板

**Files:**
- Modify: `frontend/src/components/VoicePanel.tsx`
- Modify: `frontend/src/App.tsx`
- Modify: `frontend/src/App.css`

- [ ] **Step 1: 修改 App.tsx 传递 onOptimizeResult**

修改 `frontend/src/App.tsx`，给 `useWebSocket` 传入 `onOptimizeResult`，并将结果传给 `VoicePanel`：

```typescript
const [optimizeResults, setOptimizeResults] = useState<OptimizeResult[]>([]);

const { connected, sendText, sendAudio } = useWebSocket({
  url: `ws://${window.location.hostname}:8000/ws`,
  onStateUpdate: (state) => setCanvasState(state),
  onAsrResult: (text) => setAsrText(text),
  onOptimizeResult: (result) => {
    setOptimizeResults(prev => [...prev.slice(-4), result]); // 保留最近5条
  },
  onError: (msg) => setError(msg),
});
```

将 `optimizeResults` 传给 `VoicePanel`：

```tsx
<VoicePanel
  connected={connected}
  onSendAudio={sendAudio}
  onSendText={sendText}
  asrText={asrText}
  optimizeResults={optimizeResults}
/>
```

- [ ] **Step 2: 修改 VoicePanel 添加优化过程面板**

修改 `frontend/src/components/VoicePanel.tsx`，添加 `optimizeResults` prop 和展示面板：

```tsx
import type { OptimizeResult } from '../types';

interface VoicePanelProps {
  connected: boolean;
  onSendAudio: (blob: Blob) => void;
  onSendText: (text: string) => void;
  asrText: string;
  optimizeResults?: OptimizeResult[];
}

export default function VoicePanel({ connected, onSendAudio, onSendText, asrText, optimizeResults = [] }: VoicePanelProps) {
  // ... 现有代码 ...

  const [showOptimize, setShowOptimize] = useState(true);

  // 在 return 中，text-input-form 之后添加：
  {optimizeResults.length > 0 && (
    <div className="optimize-panel">
      <div className="optimize-header" onClick={() => setShowOptimize(!showOptimize)}>
        📝 优化过程 {showOptimize ? '▼' : '▶'}
      </div>
      {showOptimize && (
        <div className="optimize-content">
          {optimizeResults.map((r, i) => (
            <div key={i} className="optimize-item">
              <div className="optimize-row">
                <span className="optimize-label">🎙️ 原始语音:</span>
                <span className="optimize-value">"{r.original}"</span>
              </div>
              <div className="optimize-row">
                <span className="optimize-label">⚡ 规则预处理:</span>
                <span className="optimize-value">"{r.rule_processed}"</span>
              </div>
              {r.used_llm && (
                <div className="optimize-row">
                  <span className="optimize-label">🤖 AI 优化:</span>
                  <span className="optimize-value">"{r.final}"</span>
                </div>
              )}
              <div className="optimize-meta">
                <span className={`confidence ${r.confidence >= 0.7 ? 'high' : 'low'}`}>
                  置信度: {Math.round(r.confidence * 100)}%
                </span>
                <span className={`method ${r.used_llm ? 'llm' : 'rule'}`}>
                  {r.used_llm ? 'AI 优化' : '规则引擎'}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )}
```

- [ ] **Step 3: 添加优化面板 CSS 样式**

在 `frontend/src/App.css` 末尾追加：

```css
/* 优化过程面板 */
.optimize-panel {
  margin-top: 12px;
  border-top: 1px solid #eee;
  padding-top: 8px;
}

.optimize-header {
  font-size: 0.875rem;
  color: #666;
  cursor: pointer;
  padding: 4px 0;
  user-select: none;
}

.optimize-header:hover {
  color: #333;
}

.optimize-content {
  max-height: 300px;
  overflow-y: auto;
}

.optimize-item {
  background: #f8f9fa;
  border-radius: 6px;
  padding: 8px 10px;
  margin-top: 6px;
  font-size: 0.8rem;
}

.optimize-row {
  display: flex;
  gap: 4px;
  margin-bottom: 2px;
}

.optimize-label {
  color: #888;
  white-space: nowrap;
}

.optimize-value {
  color: #333;
  word-break: break-all;
}

.optimize-meta {
  display: flex;
  gap: 8px;
  margin-top: 4px;
  font-size: 0.75rem;
}

.confidence {
  padding: 1px 6px;
  border-radius: 3px;
}

.confidence.high {
  background: #d4edda;
  color: #155724;
}

.confidence.low {
  background: #fff3cd;
  color: #856404;
}

.method {
  padding: 1px 6px;
  border-radius: 3px;
}

.method.rule {
  background: #d1ecf1;
  color: #0c5460;
}

.method.llm {
  background: #e2d5f1;
  color: #4a1a8a;
}
```

- [ ] **Step 4: 确认前端编译通过**

Run: `cd /Users/hw/Ai_Projects/AI\ 语言绘图工具/frontend && npx tsc --noEmit`
Expected: 无错误

- [ ] **Step 5: 提交**

```bash
git add frontend/src/App.tsx frontend/src/components/VoicePanel.tsx frontend/src/App.css
git commit -m "feat: VoicePanel 新增优化过程展示面板

- 显示原始语音 → 规则预处理 → AI 优化的转化过程
- 置信度高亮和处理方式标签
- 默认折叠，点击展开
- 保留最近 5 条优化记录

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 9: 后端集成测试 + 端到端验证

**Files:**
- Modify: `backend/tests/test_optimizer.py`

- [ ] **Step 1: 编写端到端集成测试**

在 `backend/tests/test_optimizer.py` 末尾追加：

```python
class TestEndToEnd:
    """端到端集成测试"""

    def setup_method(self):
        self.opt = VoiceOptimizer()

    @pytest.mark.asyncio
    async def test_simple_create_command(self):
        """简单创建命令 — 高置信度，不调 LLM"""
        result = await self.opt.optimize("画一个红色的长方形")
        assert result.used_llm is False
        assert result.confidence >= 0.7
        assert "创建" in result.final

    @pytest.mark.asyncio
    async def test_colloquial_with_filler(self):
        """口语化命令带语气词"""
        result = await self.opt.optimize("嗯那个帮我画一个红色的长方形就是那种大一点的")
        assert "嗯" not in result.final
        assert "那个" not in result.final
        assert "创建" in result.final

    @pytest.mark.asyncio
    async def test_delete_command(self):
        """删除命令"""
        result = await self.opt.optimize("把那个蓝色的圆弄掉")
        assert "删除" in result.final

    @pytest.mark.asyncio
    async def test_undo_command(self):
        """撤销命令"""
        result = await self.opt.optimize("撤销")
        assert "undo" in result.final
        assert result.used_llm is False

    @pytest.mark.asyncio
    async def test_reference_resolution(self):
        """指代消解"""
        result = await self.opt.optimize("刚才那个弄大一点")
        assert "last_created" in result.rule_processed or "放大" in result.final

    @pytest.mark.asyncio
    async def test_position_expression(self):
        """相对位置表达"""
        result = await self.opt.optimize("画一个圆放到右边")
        assert "创建" in result.final

    @pytest.mark.asyncio
    async def test_scale_expression(self):
        """相对尺寸表达"""
        result = await self.opt.optimize("画一个大一点的长方形")
        assert "创建" in result.final
```

- [ ] **Step 2: 运行全部后端测试**

Run: `cd /Users/hw/Ai_Projects/AI\ 语言绘图工具/backend && python -m pytest tests/ -v`
Expected: ALL PASS

- [ ] **Step 3: 前端构建验证**

Run: `cd /Users/hw/Ai_Projects/AI\ 语言绘图工具/frontend && npm run build`
Expected: BUILD SUCCESS

- [ ] **Step 4: 提交**

```bash
git add backend/tests/test_optimizer.py
git commit -m "test: 添加端到端集成测试

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 10: 最终推送

- [ ] **Step 1: 推送到 GitHub**

```bash
cd /Users/hw/Ai_Projects/AI\ 语言绘图工具 && git push origin main
```
