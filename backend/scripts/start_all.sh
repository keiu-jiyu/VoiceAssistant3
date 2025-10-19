#!/bin/bash
# backend/scripts/start_all.sh

echo "🚀 Starting Voice Assistant Backend..."

# 启动 API 服务
echo "📡 Starting API Server..."
python -m api.server &
API_PID=$!

# 等待 API 启动
sleep 2

# 启动 Agent
echo "🤖 Starting AI Agent..."
python -m agent.server &
AGENT_PID=$!

echo "✅ All services started!"
echo "API PID: $API_PID"
echo "Agent PID: $AGENT_PID"

# 捕获中断信号
trap "echo '⚠️ Stopping services...'; kill $API_PID $AGENT_PID; exit" INT TERM

wait
