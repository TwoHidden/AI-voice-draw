"""语音识别服务 - FunASR 本地模型"""
import logging
from typing import Optional
import numpy as np

logger = logging.getLogger(__name__)


class ASRService:
    """FunASR 语音识别服务"""

    def __init__(self):
        self.model = None
        self.sample_rate = 16000

    async def initialize(self):
        """初始化 FunASR 模型"""
        try:
            from funasr import AutoModel

            self.model = AutoModel(
                model="paraformer-zh",
                vad_model="fsmn-vad",
                punc_model="ct-punc",
            )
            logger.info("FunASR 模型加载成功")
        except ImportError:
            logger.warning("FunASR 未安装，语音识别不可用")
        except Exception as e:
            logger.error(f"FunASR 模型加载失败: {e}")

    async def transcribe(self, audio_bytes: bytes) -> Optional[str]:
        """将音频转换为文字"""
        if not self.model:
            logger.warning("ASR 模型未初始化")
            return None

        try:
            # 将 bytes 转换为 numpy 数组
            audio_array = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0

            # 调用 FunASR 识别
            result = self.model.generate(input=audio_array, batch_size_s=300)

            if result and len(result) > 0:
                text = result[0].get("text", "")
                logger.info(f"ASR 识别结果: {text}")
                return text

            return None

        except Exception as e:
            logger.error(f"ASR 识别失败: {e}")
            return None

    def is_ready(self) -> bool:
        """检查 ASR 是否就绪"""
        return self.model is not None


# 全局单例
asr_service = ASRService()
