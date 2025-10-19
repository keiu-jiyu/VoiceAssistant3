#!/bin/bash

# 🔧 开发模式 - 使用热重载
# Usage: ./scripts/dev.sh [api|agent|all]

set -e

SERVICE=${1:-all}
cd "$(dirname "\$0")/../backend"

# 检查 .env
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    exit 1
fi

export $(cat .env | grep -v '^#' | xargs)

start_api() {
    echo "🌐 Starting API (Dev Mode)..."
    uvicorn api.server:app \
        --host 0.0.0.0 \
        --port 8000 \
        --reload \
        --reload-dir api \
        --reload-dir common \
        --log-level debug
}

start_agent() {
    echo "🤖 Starting Agent (Dev Mode)..."
    # Agent 通常不需要热重载,但可以使用 watchdog
    python -m agent.server
}

case $SERVICE in
    api)
        start_api
        ;;
    agent)
        start_agent
        ;;
    all)
        echo "🚀 Starting all services in dev mode..."
        start_api &
        API_PID=$!
        sleep 2
        start_agent &
        AGENT_PID=$!
        
        trap "echo '⚠️ Stopping...'; kill $API_PID $AGENT_PID; exit" INT TERM
        wait
        ;;
    *)
        echo "Usage: \$0 [api|agent|all]"
        exit 1
        ;;
esac