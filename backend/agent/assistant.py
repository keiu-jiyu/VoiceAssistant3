# backend/agent/assistant.py
import asyncio
import aiohttp
import logging
from livekit import api, rtc
from livekit.agents.llm import ChatContext
from livekit.agents.stt import SpeechEventType

from core.config import settings
from core.exceptions import LiveKitConnectionError
from integrations.aliyun.stt import AliyunSTT
from integrations.aliyun.llm import create_llm
from integrations.aliyun.tts import create_tts

logger = logging.getLogger(__name__)


class AIAssistant:
    """AI 语音助手"""

    def __init__(self):
        self.room = None
        self.audio_source = None
        self.http_session = None
        self.stt = None
        self.llm = None
        self.tts = None

    async def initialize(self):
        """初始化组件"""
        logger.info("初始化 AI 组件...")

        self.http_session = aiohttp.ClientSession()

        self.stt = AliyunSTT(
            api_key=settings.DASHSCOPE_API_KEY,
            model='paraformer-realtime-v2',
            language='zh-CN'
        )

        self.llm = create_llm()
        self.tts = create_tts(self.http_session)

        logger.info("✅ AI 组件初始化完成")

    async def connect_to_room(self):
        """连接到 LiveKit 房间"""
        token = (
            api.AccessToken(settings.LIVEKIT_API_KEY, settings.LIVEKIT_API_SECRET)
            .with_identity(settings.AGENT_IDENTITY)
            .with_name("AI Assistant")
            .with_grants(api.VideoGrants(
                room_join=True,
                room=settings.ROOM_NAME,
                can_publish=True,
                can_publish_data=True,
                agent=True,
            ))
        ).to_jwt()

        self.room = rtc.Room()

        try:
            await self.room.connect(settings.LIVEKIT_URL, token)
            logger.info(f"✅ 已连接到房间: {settings.ROOM_NAME}")
        except Exception as e:
            raise LiveKitConnectionError(f"连接失败: {e}")

        # 创建音频轨道
        self.audio_source = rtc.AudioSource(
            self.tts.sample_rate,
            self.tts.num_channels
        )
        track = rtc.LocalAudioTrack.create_audio_track(
            "ai-voice",
            self.audio_source
        )
        await self.room.local_participant.publish_track(track)
        logger.info("🎤 AI 语音轨道已发布")

    async def process_participant_audio(self, participant: rtc.Participant):
        """处理参与者音频"""
        if participant.identity == settings.AGENT_IDENTITY:
            return

        # 查找麦克风轨道
        audio_stream = None
        for pub in participant.track_publications.values():
            if (pub.track and
                    pub.kind == rtc.TrackKind.KIND_AUDIO and
                    pub.source == rtc.TrackSource.SOURCE_MICROPHONE):
                audio_stream = rtc.AudioStream(pub.track)
                break

        if not audio_stream:
            logger.warning(f"未找到 {participant.identity} 的麦克风")
            return

        logger.info(f"🎧 开始处理: {participant.identity}")

        stt_stream = self.stt.stream()
        chat_context = ChatContext()

        async def feed_stt():
            """音频重采样并发送到 STT"""
            resampler = rtc.AudioResampler(
                input_rate=48000,
                output_rate=16000,
                num_channels=1,
                quality=rtc.AudioResamplerQuality.QUICK
            )

            async for frame_event in audio_stream:
                frame = frame_event.frame
                for resampled_frame in resampler.push(frame):
                    stt_stream.push_frame(resampled_frame)

            for resampled_frame in resampler.flush():
                stt_stream.push_frame(resampled_frame)

            await stt_stream.aclose()

        async def handle_stt():
            """处理 STT 结果"""
            async for event in stt_stream:
                if (event.type == SpeechEventType.FINAL_TRANSCRIPT and
                        event.alternatives):
                    user_text = event.alternatives[0].text.strip()
                    if not user_text:
                        continue

                    logger.info(f"💬 用户: {user_text}")
                    chat_context.add_message(role="user", content=user_text)

                    # 异步处理 LLM + TTS
                    asyncio.create_task(self.process_llm_response(chat_context))

        await asyncio.gather(
            feed_stt(),
            handle_stt(),
            return_exceptions=True
        )

    async def process_llm_response(self, chat_context: ChatContext):
        """处理 LLM 响应并播放"""
        tts_stream = self.tts.stream()
        full_response = ""

        try:
            llm_stream = self.llm.chat(chat_ctx=chat_context)
            async for chunk in llm_stream:
                if chunk.delta and chunk.delta.content:
                    content = chunk.delta.content
                    tts_stream.push_text(content)
                    full_response += content

            tts_stream.flush()
            chat_context.add_message(role="assistant", content=full_response)
            logger.info(f"🤖 AI: {full_response}")

            # 播放音频
            async for audio_chunk in tts_stream:
                if hasattr(audio_chunk, 'frame'):
                    await self.audio_source.capture_frame(audio_chunk.frame)
                else:
                    await self.audio_source.capture_frame(audio_chunk)

            await tts_stream.aclose()

        except Exception as e:
            logger.error(f"LLM/TTS 错误: {e}", exc_info=True)

    async def start(self):
        """启动助手"""
        try:
            await self.initialize()
            await self.connect_to_room()

            @self.room.on("track_subscribed")
            def on_track_subscribed(
                    track: rtc.Track,
                    publication: rtc.RemoteTrackPublication,
                    participant: rtc.RemoteParticipant
            ):
                if (publication.kind == rtc.TrackKind.KIND_AUDIO and
                        publication.source == rtc.TrackSource.SOURCE_MICROPHONE):
                    logger.info(f"🎤 检测到麦克风: {participant.identity}")
                    asyncio.create_task(self.process_participant_audio(participant))

            @self.room.on("participant_connected")
            def on_participant_connected(participant: rtc.RemoteParticipant):
                logger.info(f"👤 用户加入: {participant.identity}")

            logger.info("✨ AI Agent 就绪")
            await asyncio.Event().wait()

        except Exception as e:
            logger.error(f"错误: {e}", exc_info=True)
        finally:
            await self.cleanup()

    async def cleanup(self):
        """清理资源"""
        if self.http_session:
            await self.http_session.close()
        if self.room:
            await self.room.disconnect()
        logger.info("🚪 AI 助手已关闭")