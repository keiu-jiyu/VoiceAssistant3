import asyncio
import wave
import os
from livekit.plugins import aliyun
from livekit import rtc
import aiohttp
from dotenv import load_dotenv

load_dotenv()


async def test_with_real_audio():
    """使用真实音频文件测试"""

    audio_file = "test_chinese_1.wav"

    # 读取并转换音频到 16kHz
    print("🔄 转换音频到 16kHz...")

    try:
        import numpy as np
        from scipy import signal

        # 读取原始音频
        with wave.open(audio_file, 'rb') as wf:
            original_rate = wf.getframerate()
            channels = wf.getnchannels()
            sample_width = wf.getsampwidth()
            frames = wf.readframes(wf.getnframes())

            print(f"📊 原始音频: {original_rate} Hz")

        # 转换为 numpy 数组
        audio_data = np.frombuffer(frames, dtype=np.int16)

        # 重采样到 16kHz
        target_rate = 16000
        num_samples = int(len(audio_data) * target_rate / original_rate)
        resampled = signal.resample(audio_data, num_samples)
        resampled = resampled.astype(np.int16)

        # 保存转换后的音频
        converted_file = "com_16k.wav"
        with wave.open(converted_file, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(16000)
            wf.writeframes(resampled.tobytes())

        print(f"✅ 已转换为 16kHz: {converted_file}")
        audio_file = converted_file
        sample_rate = 16000

    except ImportError:
        print("⚠️ 需要安装: pip install numpy scipy")
        return

    # 创建 session
    session = aiohttp.ClientSession()

    try:
        # 创建 STT
        stt = aliyun.STT(
            language='zh-CN',
            model='paraformer-realtime-v2',
            max_sentence_silence=800,
            api_key=os.getenv('DASHSCOPE_API_KEY'),
            http_session=session
        )

        print("✅ STT 实例创建成功")

        # 创建音频流
        stream = stt.stream()
        print("✅ Stream 创建成功")

        # 等待初始化
        await asyncio.sleep(1)

        # 监听识别结果
        async def listen_results():
            print("🎯 开始监听 STT 结果...")
            try:
                async for event in stream:
                    print(f"🔔 收到事件: type={event.type}")
                    if event.alternatives:
                        text = event.alternatives[0].text
                        is_final = event.is_final
                        print(f"{'🟢 最终' if is_final else '🟡 中间'} 识别: '{text}'")
            except Exception as e:
                print(f"❌ 监听出错: {e}")

        # 启动监听
        listen_task = asyncio.create_task(listen_results())

        # 推送音频
        print("📡 开始推送音频...")
        with wave.open(audio_file, 'rb') as wf:
            chunk_size = int(16000 * 0.1)  # 100ms
            frame_count = 0

            while True:
                data = wf.readframes(chunk_size)
                if not data:
                    break

                audio_frame = rtc.AudioFrame(
                    data=data,
                    sample_rate=16000,
                    num_channels=1,
                    samples_per_channel=len(data) // 2
                )

                stream.push_frame(audio_frame)
                frame_count += 1

                if frame_count % 10 == 0:
                    print(f"   已推送 {frame_count} 帧...")

                await asyncio.sleep(0.1)

        print(f"✅ 音频推送完成，共 {frame_count} 帧")

        # 等待识别
        print("⏳ 等待识别完成...")
        await asyncio.sleep(5)

        # 关闭
        await stream.aclose()

        try:
            await asyncio.wait_for(listen_task, timeout=2)
        except asyncio.TimeoutError:
            listen_task.cancel()

        print("🏁 测试完成")

    finally:
        await session.close()


asyncio.run(test_with_real_audio())