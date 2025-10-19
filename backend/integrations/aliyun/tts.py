# backend/integrations/aliyun/tts.py
import logging
import aiohttp
from livekit.plugins import aliyun
from core.config import settings

logger = logging.getLogger(__name__)


def create_tts(http_session: aiohttp.ClientSession) -> aliyun.TTS:
    """创建阿里云 TTS"""

    return aliyun.TTS(
        model='cosyvoice-v1',
        voice='longxiaochun',
        http_session=http_session
    )
