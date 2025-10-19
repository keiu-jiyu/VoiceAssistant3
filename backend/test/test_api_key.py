import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('DASHSCOPE_API_KEY')

print(f"🔑 API Key 长度: {len(api_key) if api_key else 0}")
print(f"🔑 API Key 前缀: {api_key[:10] if api_key else 'None'}...")
print(f"🔑 API Key 后缀: ...{api_key[-5:] if api_key else 'None'}")

# 简单验证格式
if api_key and api_key.startswith('sk-'):
    print("✅ API Key 格式正确")
else:
    print("❌ API Key 格式错误或为空")

# 测试简单的 HTTP 请求
import aiohttp
import asyncio


async def test_key():
    url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "qwen-turbo",
        "input": {"prompt": "测试"},
        "parameters": {"max_tokens": 10}
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, headers=headers, json=data) as resp:
                print(f"📡 HTTP 状态码: {resp.status}")
                if resp.status == 200:
                    print("✅ API Key 验证成功！")
                else:
                    text = await resp.text()
                    print(f"❌ 验证失败: {text}")
        except Exception as e:
            print(f"❌ 请求失败: {e}")


asyncio.run(test_key())