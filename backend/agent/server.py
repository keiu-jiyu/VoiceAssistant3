# backend/agent/server.py
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.logger import setup_logger
from agent.assistant import AIAssistant

logger = setup_logger("agent_server")


async def main():
    logger.info("🚀 启动 AI Agent...")
    assistant = AIAssistant()
    await assistant.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Agent 已停止")