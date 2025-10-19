#!/bin/bash

# 🌐 启动 API 服务器
# Usage: ./scripts/start_api.sh

set -e

# 进入后端目录
cd "$(dirname "\$0")/../backend"

# 检查 .env 文件
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please copy .env.example to .env and configure it."
    exit 1
fi

# 加载环境变量
export $(cat .env | grep -v '^#' | xargs)

# 检查必要的环境变量
if [ -z "$LIVEKIT_URL" ] || [ -z "$LIVEKIT_API_KEY" ]; then
    echo "❌ Error: Missing required environment variables"
    echo "Please check LIVEKIT_URL and LIVEKIT_API_KEY in .env"
    exit 1
fi

echo "🌐 Starting API Server..."
echo "================================"
echo "URL: http://0.0.0.0:8000"
echo "Docs: http://0.0.0.0:8000/docs"
echo "================================"

# 启动 API 服务器
python -m api.server

# 或使用 uvicorn 指定更多参数
# uvicorn api.server:app \
#     --host 0.0.0.0 \
#     --port 8000 \
#     --reload \
#     --log-level info
