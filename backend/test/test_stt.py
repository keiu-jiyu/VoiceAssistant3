import asyncio
import os
import aiohttp
from dotenv import load_dotenv
from livekit.plugins import aliyun
import logging

logging.basicConfig(level=logging.INFO)
load_dotenv()


async def test_stt():
    print("🧪 测试阿里云 STT...")

    # 创建 HTTP Session
    async with aiohttp.ClientSession() as session:
        # 创建 STT 实例（传入 session）
        stt = aliyun.STT(
            model="paraformer-realtime-v2",
            language="zh-CN",
            http_session=session,  # ← 关键！
        )

        print(f"✅ STT 实例创建成功")
        print(f"   Model: {stt._opts.model}")
        print(f"   Language: {stt._opts.language}")

        # 测试连接
        try:
            stream = stt.stream()
            print("✅ STT Stream 创建成功")

            # 监听事件
            async def listen_events():
                async for event in stream:
                    print(f"📝 收到事件: {event.type}")
                    if event.alternatives:
                        print(f"   文本: {event.alternatives[0].text}")

            # 启动监听（超时 5 秒）
            try:
                await asyncio.wait_for(listen_events(), timeout=5.0)
            except asyncio.TimeoutError:
                print("⏱️ 5 秒超时（正常，因为没有音频输入）")

            await stream.aclose()
            print("✅ 测试完成")
        except Exception as e:
            print(f"❌ 错误: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_stt())