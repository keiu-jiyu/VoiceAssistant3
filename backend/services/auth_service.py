# backend/services/auth_service.py

import logging
from supabase import create_client, Client
from core.config import settings

logger = logging.getLogger(__name__)


class AuthService:
    """认证服务"""

    def __init__(self):
        """初始化 Supabase 客户端"""
        self.supabase: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY
        )
        logger.info("✅ Supabase 客户端已初始化")

    async def login(self, email: str, password: str) -> dict:
        """
        用户登录

        Args:
            email: 邮箱
            password: 密码

        Returns:
            包含 access_token 和 user 信息的字典
        """
        try:
            # Supabase 登录
            response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            if response.user:
                logger.info(f"✅ 用户登录成功: {email}")
                return {
                    "access_token": response.session.access_token,
                    "refresh_token": response.session.refresh_token,
                    "user": {
                        "id": response.user.id,
                        "email": response.user.email,
                    }
                }
            else:
                logger.warning(f"⚠️ 登录失败: {email}")
                return None

        except Exception as e:
            logger.error(f"❌ 登录异常: {e}", exc_info=True)
            raise

    async def verify_token(self, access_token: str) -> dict:
        """
        验证 Token

        Args:
            access_token: JWT Token

        Returns:
            用户信息
        """
        try:
            response = self.supabase.auth.get_user(access_token)
            if response.user:
                return {
                    "id": response.user.id,
                    "email": response.user.email,
                }
            return None
        except Exception as e:
            logger.error(f"❌ Token 验证失败: {e}")
            return None


# 全局实例
auth_service = AuthService()