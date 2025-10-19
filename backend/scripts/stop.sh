#!/bin/bash

# 🛑 停止所有服务
# Usage: ./scripts/stop.sh

echo "🛑 Stopping all services..."

# 查找并终止 API 服务器
API_PID=$(ps aux | grep "api.server" | grep -v grep | awk '{print \$2}')
if [ -n "$API_PID" ]; then
    echo "Stopping API Server (PID: $API_PID)..."
    kill $API_PID
fi

# 查找并终止 Agent 服务
AGENT_PID=$(ps aux | grep "agent.server" | grep -v grep | awk '{print \$2}')
if [ -n "$AGENT_PID" ]; then
    echo "Stopping AI Agent (PID: $AGENT_PID)..."
    kill $AGENT_PID
fi

# 等待进程结束
sleep 2

# 强制终止
API_PID=$(ps aux | grep "api.server" | grep -v grep | awk '{print \$2}')
if [ -n "$API_PID" ]; then
    echo "Force stopping API..."
    kill -9 $API_PID
fi

AGENT_PID=$(ps aux | grep "agent.server" | grep -v grep | awk '{print \$2}')
if [ -n "$AGENT_PID" ]; then
    echo "Force stopping Agent..."
    kill -9 $AGENT_PID
fi

echo "✅ All services stopped!"
