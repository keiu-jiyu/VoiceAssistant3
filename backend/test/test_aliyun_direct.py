import asyncio
import websockets
import json
import os
import wave
from dotenv import load_dotenv

load_dotenv()


async def test_aliyun_stt():
    """直接测试阿里云实时语音识别 API"""

    api_key = os.getenv('DASHSCOPE_API_KEY')

    # 阿里云实时语音识别 WebSocket URL
    url = "wss://nls-gateway-cn-shanghai.aliyuncs.com/ws/v1"

    # 构建认证参数
    params = {
        "appkey": api_key.replace("sk-", ""),  # 去掉 sk- 前缀
        "token": api_key,
        "format": "pcm",
        "sample_rate": 16000,
        "enable_intermediate_result": True,
        "enable_punctuation_prediction": True,
        "enable_inverse_text_normalization": True
    }

    print(f"🔗 连接 URL: {url}")
    print(f"🔑 使用 API Key: {api_key[:10]}...{api_key[-5:]}")

    try:
        # 读取音频文件
        audio_file = "com_16k.wav"
        with wave.open(audio_file, 'rb') as wf:
            print(f"\n📊 音频信息:")
            print(f"   采样率: {wf.getframerate()} Hz")
            print(f"   声道数: {wf.getnchannels()}")
            print(f"   位深: {wf.getsampwidth() * 8} bit")
            print(f"   总帧数: {wf.getnframes()}")

            audio_data = wf.readframes(wf.getnframes())

        # 连接 WebSocket
        async with websockets.connect(url) as ws:
            print("\n✅ WebSocket 连接成功")

            # 发送开始命令
            start_msg = {
                "header": {
                    "message_id": "test-001",
                    "task_id": "test-task",
                    "namespace": "SpeechTranscriber",
                    "name": "StartTranscription",
                    "appkey": params["appkey"]
                },
                "payload": {
                    "format": "pcm",
                    "sample_rate": 16000,
                    "enable_intermediate_result": True
                }
            }

            await ws.send(json.dumps(start_msg))
            print("📤 已发送开始命令")

            # 接收响应
            response = await ws.recv()
            print(f"📥 收到响应: {response}")

            # 分块发送音频
            chunk_size = 3200  # 每次发送 0.1 秒的音频
            for i in range(0, len(audio_data), chunk_size):
                chunk = audio_data[i:i + chunk_size]
                await ws.send(chunk)
                await asyncio.sleep(0.01)

            print(f"✅ 已发送全部音频数据")

            # 发送结束命令
            stop_msg = {
                "header": {
                    "message_id": "test-002",
                    "task_id": "test-task",
                    "namespace": "SpeechTranscriber",
                    "name": "StopTranscription",
                    "appkey": params["appkey"]
                }
            }

            await ws.send(json.dumps(stop_msg))
            print("📤 已发送结束命令")

            # 接收所有结果
            print("\n📝 识别结果:")
            async for message in ws:
                result = json.loads(message)
                print(json.dumps(result, indent=2, ensure_ascii=False))

    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()


asyncio.run(test_aliyun_stt())