import asyncio
import aiohttp


async def download():
    # 阿里云官方测试音频（16kHz 中文）
    urls = [
        "https://isv-data.oss-cn-hangzhou.aliyuncs.com/ics/MaaS/ASR/test_audio/asr_example_zh.wav",
        "https://gw.alipayobjects.com/os/bmw-prod/0574ee2e-f494-45a5-820f-63aee583045a.wav"
    ]

    async with aiohttp.ClientSession() as session:
        for i, url in enumerate(urls):
            try:
                print(f"📥 下载测试音频 {i + 1}...")
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                    if resp.status == 200:
                        content = await resp.read()
                        with open(f"test_chinese_{i + 1}.wav", "wb") as f:
                            f.write(content)
                        print(f"✅ 已保存：test_chinese_{i + 1}.wav ({len(content)} 字节)")
            except Exception as e:
                print(f"❌ 下载失败：{e}")


asyncio.run(download())