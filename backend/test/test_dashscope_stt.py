import os
import asyncio
import aiohttp
from dotenv import load_dotenv

load_dotenv()


async def test_dashscope_stt():
    api_key = os.getenv('DASHSCOPE_API_KEY')

    url = "wss://dashscope.aliyuncs.com/api-ws/v1/inference"
    headers = {
        "Authorization": f"bearer {api_key}",
        "X-DashScope-DataInspection": "enable",
    }

    print(f"🔗 连接 URL: {url}")
    print(f"🔑 API Key: {api_key[:15]}...")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(url, headers=headers) as ws:
                print("✅ WebSocket 连接成功！")

                # 发送识别任务
                params = {
                    "header": {
                        "action": "run-task",
                        "task_id": "test-123",
                        "streaming": "duplex",
                    },
                    "payload": {
                        "task_group": "audio",
                        "task": "asr",
                        "function": "recognition",
                        "model": "paraformer-realtime-v2",
                        "parameters": {
                            "format": "wav",
                            "sample_rate": 16000,
                            "language_hints": ["zh-CN"],
                        },
                        "input": {},
                    },
                }

                await ws.send_json(params)
                print("📤 已发送识别请求")

                # 接收响应
                msg = await asyncio.wait_for(ws.receive(), timeout=5)
                print(f"📥 收到响应: {msg.data}")

    except aiohttp.ClientConnectorError as e:
        print(f"❌ 连接失败: {e}")
    except asyncio.TimeoutError:
        print("⏱️ 超时：5秒内未收到响应")
    except Exception as e:
        print(f"❌ 错误: {type(e).__name__}: {e}")


asyncio.run(test_dashscope_stt())