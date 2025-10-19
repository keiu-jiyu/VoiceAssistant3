#!/bin/bash

# 🤖 启动 AI Agent 服务
# Usage: ./scripts/start_agent.sh

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
REQUIRED_VARS=(
    "LIVEKIT_URL"
    "LIVEKIT_API_KEY"
    "LIVEKIT_API_SECRET"
    "DASHSCOPE_API_KEY"
    "ALIYUN_APP_KEY"
)

for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Error: Missing required environment variable: $var"
        exit 1
    fi
done

echo "🤖 Starting AI Agent..."
echo "================================"
echo "LiveKit URL: $LIVEKIT_URL"
echo "Agent will connect to rooms automatically"
echo "================================"

# 启动 Agent 服务
python -m agent.server
