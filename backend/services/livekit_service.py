# backend/services/livekit_service.py

import logging
from datetime import timedelta
from livekit import api

from core.config import settings

logger = logging.getLogger(__name__)


class LiveKitService:
    """LiveKit 服务封装"""

    def __init__(self):
        """初始化 LiveKit 服务"""
        self.api_key = settings.LIVEKIT_API_KEY
        self.api_secret = settings.LIVEKIT_API_SECRET
        self.url = settings.LIVEKIT_URL

        if not self.api_key or not self.api_secret:
            raise ValueError(
                "LiveKit credentials not configured. Please set:\n"
                "- LIVEKIT_API_KEY\n"
                "- LIVEKIT_API_SECRET"
            )

        logger.info(f"✅ LiveKit service initialized (URL: {self.url})")

    async def create_token(
            self,
            identity: str,
            room_name: str = "",
            ttl_seconds: int = 3600,
            **kwargs
    ) -> str:
        """
        创建 LiveKit 访问令牌

        Args:
            identity: 用户唯一标识
            room_name: 房间名（可选）
            ttl_seconds: Token 有效期（秒）
            **kwargs: 其他权限参数

        Returns:
            JWT Token 字符串
        """
        try:
            # 创建 Token（使用 timedelta）
            token = api.AccessToken(
                api_key=self.api_key,
                api_secret=self.api_secret
            )

            # 设置基本信息
            token.identity = identity
            token.name = kwargs.get("name", identity)

            # ✅ 修复：使用 timedelta 而不是整数
            token.ttl = timedelta(seconds=ttl_seconds)

            # 设置房间权限
            if room_name:
                video_grants = api.VideoGrants(
                    room_join=True,
                    room=room_name,
                    can_publish=kwargs.get("can_publish", True),
                    can_subscribe=kwargs.get("can_subscribe", True),
                    can_publish_data=kwargs.get("can_publish_data", True)
                )
                token.video_grants = video_grants

            # 生成 JWT
            jwt_token = token.to_jwt()

            logger.info(
                f"✅ Token created: identity={identity}, "
                f"room={room_name or 'any'}, ttl={ttl_seconds}s"
            )

            return jwt_token

        except Exception as e:
            logger.error(f"❌ Failed to create token: {e}", exc_info=True)
            raise

    def get_connection_info(self) -> dict:
        """获取连接信息"""
        return {
            "url": self.url,
            "api_key": self.api_key[:8] + "..." if self.api_key else None
        }
