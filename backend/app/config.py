"""应用配置"""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    APP_NAME: str = "AI Voice Draw"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # LLM 配置
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "https://api.example.com/v1")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "mimo-v2.5-pro")

    # FunASR 配置
    ASR_MODEL: str = os.getenv("ASR_MODEL", "paraformer-zh")
    ASR_VAD_MODEL: str = os.getenv("ASR_VAD_MODEL", "fsmn-vad")
    ASR_PUNC_MODEL: str = os.getenv("ASR_PUNC_MODEL", "ct-punc")

    # 服务端口
    PORT: int = int(os.getenv("PORT", "8000"))


settings = Settings()
