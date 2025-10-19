# backend/api/routes.py

from fastapi import APIRouter, Query, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
import logging
import uuid
from livekit import api

from services.livekit_service import LiveKitService
from services.auth_service import auth_service
from core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()
livekit_service = LiveKitService()
security = HTTPBearer()


# ============ 数据模型 ============
class LoginRequest(BaseModel):
    """登录请求"""
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """登录响应"""
    access_token: str
    refresh_token: str
    user: dict


# ============ 认证依赖 ============
async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """验证用户身份"""
    token = credentials.credentials
    user = await auth_service.verify_token(token)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭证"
        )

    return user


# ============ 路由 ============
@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """用户登录"""
    try:
        result = await auth_service.login(request.email, request.password)

        if not result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="邮箱或密码错误"
            )

        logger.info(f"✅ 用户 {request.email} 登录成功")
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 登录失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="登录失败，请稍后重试"
        )


@router.get("/token")
async def get_token(current_user: dict = Depends(get_current_user)):
    """生成 LiveKit Token（需要认证）"""
    try:
        # 使用用户邮箱作为身份标识
        user_identity = current_user.get("email", "anonymous")

        token = api.AccessToken(
            api_key=settings.LIVEKIT_API_KEY,
            api_secret=settings.LIVEKIT_API_SECRET
        )

        token.with_identity(user_identity)
        token.with_name(user_identity)

        token.with_grants(api.VideoGrants(
            room_join=True,
            room=settings.ROOM_NAME,
            can_publish=True,
            can_subscribe=True,
            can_publish_data=True
        ))

        jwt_token = token.to_jwt()

        logger.info(f"✅ Token 生成成功: room={settings.ROOM_NAME}, user={user_identity}")

        return {
            "token": jwt_token,
            "url": settings.LIVEKIT_URL,
            "room": settings.ROOM_NAME
        }

    except Exception as e:
        logger.error(f"❌ Token 生成失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """获取当前用户信息"""
    return current_user