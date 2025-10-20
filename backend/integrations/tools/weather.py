# backend/integrations/tools/weather.py

import aiohttp
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class WeatherTool:
    """天气查询工具"""

    def __init__(self):
        # 使用免费的天气 API (无需 Key)
        self.base_url = "https://wttr.in"

    async def get_weather(self, city: str = "北京") -> str:
        """
        获取指定城市的天气信息

        Args:
            city: 城市名称（中文/拼音/英文）

        Returns:
            天气描述文本
        """
        try:
            url = f"{self.base_url}/{city}?format=j1&lang=zh"

            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        return f"抱歉,无法获取{city}的天气信息"

                    data = await response.json()

                    # 解析天气数据
                    current = data['current_condition'][0]
                    temp = current['temp_C']
                    feels_like = current['FeelsLikeC']
                    weather_desc = current['lang_zh'][0]['value']
                    humidity = current['humidity']
                    wind_speed = current['windspeedKmph']

                    result = (
                        f"{city}的天气情况:\n"
                        f"天气: {weather_desc}\n"
                        f"温度: {temp}°C (体感温度 {feels_like}°C)\n"
                        f"湿度: {humidity}%\n"
                        f"风速: {wind_speed} 公里/小时"
                    )

                    logger.info(f"✅ 获取天气成功: {city}")
                    return result

        except Exception as e:
            logger.error(f"❌ 获取天气失败: {e}")
            return f"抱歉,查询天气时出现错误: {str(e)}"


# 全局实例
weather_tool = WeatherTool()