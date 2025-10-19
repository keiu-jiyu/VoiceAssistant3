# backend/integrations/livekit_client.py
import logging
from livekit import api
from core.config import settings

logger = logging.getLogger(__name__)


class LiveKitClient:
    """LiveKit 客户端"""

    def __init__(self):
        self.api_key = settings.LIVEKIT_API_KEY
        self.api_secret = settings.LIVEKIT_API_SECRET
        self.url = settings.LIVEKIT_URL

    def create_token(
            self,
            identity: str,
            room_name: str = None,
            **kwargs
    ) -> str:
        """创建访问令牌"""
        room = room_name or settings.ROOM_NAME

        token = api.AccessToken(self.api_key, self.api_secret)
        token.with_identity(identity)
        token.with_name(identity)
        token.with_grants(api.VideoGrants(
            room_join=True,
            room=room,
            can_publish=True,
            can_subscribe=True,
            **kwargs
        ))

        return token.to_jwt()


livekit_client = LiveKitClient()