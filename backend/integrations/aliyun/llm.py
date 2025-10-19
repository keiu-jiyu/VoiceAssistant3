# backend/integrations/aliyun/llm.py
import logging
from livekit.plugins import aliyun
from core.config import settings

logger = logging.getLogger(__name__)


def create_llm() -> aliyun.LLM:
    """创建阿里云 LLM"""

    return aliyun.LLM(
        model="qwen-turbo",
        api_key=settings.DASHSCOPE_API_KEY
    )
