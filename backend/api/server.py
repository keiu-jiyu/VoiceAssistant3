# backend/api/server.py

import sys
from pathlib import Path

# 添加项目根目录到路径
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from core.logger import logger
from api.routes import router

# 创建 FastAPI 应用
app = FastAPI(
    title="Voice Assistant API",
    version="1.0.0",
    debug=settings.DEBUG
)

# ✅ 直接在这里解析 CORS
cors_origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",")]

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,  # ✅ 使用解析后的列表
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(router, prefix="/api")


@app.get("/")
async def root():
    return {
        "service": "Voice Assistant API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    logger.info(f"🚀 Starting API server on {settings.API_HOST}:{settings.API_PORT}")
    logger.info(f"📝 CORS Origins: {cors_origins}")

    uvicorn.run(
        "server:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        workers=settings.API_WORKERS if not settings.DEBUG else 1
    )
