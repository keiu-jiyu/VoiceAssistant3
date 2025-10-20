# backend/integrations/tools/manager.py

import json
import logging
from typing import Dict, Any, Callable
from .weather import weather_tool

logger = logging.getLogger(__name__)


class ToolManager:
    """工具调用管理器"""

    def __init__(self):
        # 注册所有可用工具
        self.tools = {
            "get_weather": {
                "function": weather_tool.get_weather,
                "description": "获取指定城市的实时天气信息",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "城市名称,例如:北京、上海、深圳"
                        }
                    },
                    "required": ["city"]
                }
            }
        }

    def get_tool_definitions(self) -> list:
        """
        获取工具定义(符合 OpenAI Function Calling 格式)
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": name,
                    "description": info["description"],
                    "parameters": info["parameters"]
                }
            }
            for name, info in self.tools.items()
        ]

    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """
        执行工具调用

        Args:
            tool_name: 工具名称
            arguments: 工具参数

        Returns:
            执行结果
        """
        if tool_name not in self.tools:
            return f"错误: 未知的工具 '{tool_name}'"

        try:
            logger.info(f"🔧 执行工具: {tool_name}, 参数: {arguments}")

            func = self.tools[tool_name]["function"]
            result = await func(**arguments)

            logger.info(f"✅ 工具执行成功: {tool_name}")
            return result

        except Exception as e:
            logger.error(f"❌ 工具执行失败: {e}", exc_info=True)
            return f"工具执行出错: {str(e)}"


# 全局实例
tool_manager = ToolManager()