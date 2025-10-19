# backend/core/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, List
from pathlib import Path


class Settings(BaseSettings):
    """应用配置"""

    # ============ API 服务配置 ============
    DEBUG: bool = False
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    LOG_LEVEL: str = "INFO"
    LOG_DIR: str = "logs"

    # ============ LiveKit 配置 ============
    LIVEKIT_URL: str = "wss://keiu-zw85ymix.livekit.cloud"
    LIVEKIT_API_KEY: str
    LIVEKIT_API_SECRET: str
    ROOM_NAME: str = "voice-room"

    # ============ AI Agent 配置 ============
    AGENT_IDENTITY: str = "voice-assistant-ai"

    # ============ 阿里云通义千问配置 ============
    DASHSCOPE_API_KEY: str  # 通义千问 API Key
    QWEN_MODEL: str = "qwen-turbo"  # 可选: qwen-turbo, qwen-plus, qwen-max

    # ============ 阿里云语音识别配置 ============
    ALIYUN_APP_KEY: str
    ALIYUN_NLS_TOKEN: Optional[str] = None  # 直接使用 Token（24小时有效）
    ALIYUN_ACCESS_KEY_ID: Optional[str] = None
    ALIYUN_ACCESS_KEY_SECRET: Optional[str] = None

    # ============ Supabase 配置 ============
    SUPABASE_URL: str
    SUPABASE_KEY: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow"
    )

    def validate_nls_credentials(self) -> dict:
        """验证阿里云 NLS 凭证（支持两种方式）"""
        if self.ALIYUN_NLS_TOKEN:
            # 方式1: 直接使用 Token
            return {
                "appkey": self.ALIYUN_APP_KEY,
                "token": self.ALIYUN_NLS_TOKEN
            }
        elif all([self.ALIYUN_APP_KEY, self.ALIYUN_ACCESS_KEY_ID, self.ALIYUN_ACCESS_KEY_SECRET]):
            # 方式2: 使用 AccessKey（需自动获取 Token）
            return {
                "appkey": self.ALIYUN_APP_KEY,
                "akid": self.ALIYUN_ACCESS_KEY_ID,
                "aksecret": self.ALIYUN_ACCESS_KEY_SECRET
            }
        else:
            raise ValueError(
                "阿里云 NLS 配置不完整，请提供以下之一：\n"
                "1. ALIYUN_APP_KEY + ALIYUN_NLS_TOKEN\n"
                "2. ALIYUN_APP_KEY + ALIYUN_ACCESS_KEY_ID + ALIYUN_ACCESS_KEY_SECRET"
            )


# 全局配置实例
settings = Settings()

# ============ 配置验证（开发时使用）============
if __name__ == "__main__":
    print("=" * 50)
    print("📋 应用配置")
    print("=" * 50)

    print(f"\n🌐 API 服务:")
    print(f"  Host: {settings.API_HOST}")
    print(f"  Port: {settings.API_PORT}")
    print(f"  Debug: {settings.DEBUG}")
    print(f"  Log Dir: {settings.LOG_DIR}")

    print(f"\n🎬 LiveKit:")
    print(f"  URL: {settings.LIVEKIT_URL}")
    print(f"  API Key: {settings.LIVEKIT_API_KEY[:20]}...")
    print(f"  Room: {settings.ROOM_NAME}")

    print(f"\n🤖 AI Agent (阿里云通义千问):")
    print(f"  Identity: {settings.AGENT_IDENTITY}")
    print(f"  Model: {settings.QWEN_MODEL}")
    print(f"  API Key: {settings.DASHSCOPE_API_KEY[:20]}...")

    try:
        nls_creds = settings.validate_nls_credentials()
        print(f"\n🎤 阿里云 NLS:")
        print(f"  AppKey: {nls_creds.get('appkey', 'N/A')}")
        print(f"  认证方式: {'Token' if 'token' in nls_creds else 'AccessKey'}")
    except ValueError as e:
        print(f"\n⚠️ NLS 配置错误: {e}")

    print("=" * 50)
