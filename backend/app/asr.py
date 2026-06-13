"""语音识别服务 - FunASR 本地模型"""
import asyncio
import io
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
        """初始化 FunASR 模型（异步，不阻塞事件循环）"""
        try:
            from funasr import AutoModel

            self.model = await asyncio.to_thread(
                AutoModel,
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
        """将音频转换为文字（支持 WebM/WAV/PCM 等格式）"""
        if not self.model:
            logger.warning("ASR 模型未初始化")
            return None

        try:
            # 解码音频为 PCM float32 数组
            audio_array = await asyncio.to_thread(
                self._decode_audio, audio_bytes
            )
            if audio_array is None:
                return None

            # 调用 FunASR 识别（阻塞操作放到线程池）
            result = await asyncio.to_thread(
                self.model.generate,
                input=audio_array,
                batch_size_s=300,
            )

            if result and len(result) > 0:
                text = result[0].get("text", "")
                logger.info(f"ASR 识别结果: {text}")
                return text

            return None

        except Exception as e:
            logger.error(f"ASR 识别失败: {e}")
            return None

    def _decode_audio(self, audio_bytes: bytes) -> Optional[np.ndarray]:
        """解码音频 bytes 为 float32 numpy 数组

        支持 WebM、WAV、MP3、OGG 等格式（通过 pydub/ffmpeg）。
        如果 pydub 不可用，回退为 raw PCM int16 解析。
        """
        try:
            from pydub import AudioSegment

            audio = AudioSegment.from_file(io.BytesIO(audio_bytes))
            audio = audio.set_frame_rate(self.sample_rate).set_channels(1).set_sample_width(2)
            return np.frombuffer(audio.raw_data, dtype=np.int16).astype(np.float32) / 32768.0
        except ImportError:
            logger.warning("pydub 未安装，尝试 raw PCM 解析（仅支持 16kHz 16-bit mono）")
            return np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
        except Exception as e:
            logger.error(f"音频解码失败: {e}")
            return None

    def is_ready(self) -> bool:
        """检查 ASR 是否就绪"""
        return self.model is not None


# 全局单例
asr_service = ASRService()
