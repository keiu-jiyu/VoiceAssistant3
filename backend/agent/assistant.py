# backend/agent/assistant.py
import asyncio
import json
import aiohttp
import logging
from livekit import api, rtc
from livekit.agents import llm
from livekit.agents.llm import ChatContext, FunctionCall, FunctionCallOutput
from livekit.agents.stt import SpeechEventType

from core.config import settings
from core.exceptions import LiveKitConnectionError
from integrations.aliyun.stt import AliyunSTT
from integrations.aliyun.llm import create_llm
from integrations.aliyun.tts import create_tts
from integrations.tools.manager import tool_manager

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
        self.tool_manager = tool_manager

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

    async def _execute_tool(self, function_name: str, arguments: dict) -> str:
        """执行工具调用"""
        try:
            logger.info(f"🔧 执行工具: {function_name}({arguments})")
            result = await self.tool_manager.execute_tool(function_name, arguments)
            logger.info(f"✅ 工具结果: {result}")
            return result
        except Exception as e:
            error_msg = f"工具执行失败: {str(e)}"
            logger.error(f"❌ {error_msg}", exc_info=True)
            return error_msg

    def _create_tool_functions(self):
        """创建工具函数列表"""
        from livekit.agents.llm import function_tool

        tools = []
        for tool_name, tool_config in self.tool_manager.tools.items():
            # 提取工具描述和参数
            description = tool_config.get('description', f'工具: {tool_name}')
            parameters = tool_config.get('parameters', {})

            # ✅ 使用闭包捕获正确的变量
            def make_tool_func(name: str):
                async def tool_func(**kwargs):
                    return await self._execute_tool(name, kwargs)

                tool_func.__name__ = name
                tool_func.__doc__ = description

                # 添加参数类型注解
                annotations = {}
                props = parameters.get('properties', {})
                for param_name, param_info in props.items():
                    param_type = param_info.get('type', 'string')
                    type_map = {
                        'string': str,
                        'number': float,
                        'integer': int,
                        'boolean': bool
                    }
                    annotations[param_name] = type_map.get(param_type, str)

                if annotations:
                    tool_func.__annotations__ = annotations

                return tool_func

            tool_func = make_tool_func(tool_name)
            tools.append(function_tool(tool_func))
            logger.info(f"📌 注册工具: {tool_name} - {description}")

        return tools

    async def process_llm_response(self, chat_context: ChatContext):
        """处理 LLM 响应并播放 (支持工具调用)"""
        tts_stream = self.tts.stream()
        full_response = ""

        try:
            # 添加系统提示 (只添加一次)
            messages = [item for item in chat_context.items if hasattr(item, 'role')]
            has_system_message = any(msg.role == "system" for msg in messages)

            if not has_system_message:
                chat_context.add_message(
                    role="system",
                    content=(
                        "你是一个智能语音助手。"
                        "当用户询问天气时，使用 get_weather 工具获取实时信息。"
                        "用简洁友好的语气回答，直接说出温度和天气状况，不要说'根据查询结果'之类的话。"
                    )
                )

            # 创建工具上下文
            from livekit.agents.llm import ToolContext
            tools = self._create_tool_functions()
            tool_ctx = ToolContext(tools) if tools else None

            # ✅ 调用 LLM (兼容阿里云插件)
            try:
                # 方式 1: 使用 tool_ctx (标准方式)
                llm_stream = self.llm.chat(
                    chat_ctx=chat_context,
                    tool_ctx=tool_ctx
                )
                logger.debug("✅ 使用 tool_ctx 模式")

            except TypeError as e:
                # 方式 2: 不使用工具 (降级)
                logger.warning(f"⚠️ LLM 不支持 tool_ctx，降级到普通模式: {e}")
                llm_stream = self.llm.chat(chat_ctx=chat_context)

            # 处理流式响应
            pending_tool_calls = []

            async for chunk in llm_stream:
                # ✅ 检查 LiveKit 原生的工具调用格式
                if isinstance(chunk, FunctionCall):
                    logger.info(f"🔧 检测到工具调用: {chunk.name}")
                    pending_tool_calls.append(chunk)
                    continue

                # ✅ 检查 OpenAI 风格的工具调用
                if hasattr(chunk, 'choices') and chunk.choices:
                    choice = chunk.choices[0]

                    # 工具调用请求
                    if hasattr(choice, 'message') and hasattr(choice.message,
                                                              'tool_calls') and choice.message.tool_calls:
                        for tool_call in choice.message.tool_calls:
                            pending_tool_calls.append(tool_call)
                        continue

                    # 文本内容
                    if hasattr(choice, 'delta') and choice.delta and choice.delta.content:
                        content = choice.delta.content
                        tts_stream.push_text(content)
                        full_response += content

                # ✅ 直接的 delta 格式
                elif hasattr(chunk, 'delta') and chunk.delta and hasattr(chunk.delta,
                                                                         'content') and chunk.delta.content:
                    content = chunk.delta.content
                    tts_stream.push_text(content)
                    full_response += content

                # ✅ 简单的 content 格式
                elif hasattr(chunk, 'content') and chunk.content:
                    content = chunk.content
                    tts_stream.push_text(content)
                    full_response += content

            # ✅ 执行待处理的工具调用
            if pending_tool_calls:
                logger.info(f"📋 处理 {len(pending_tool_calls)} 个工具调用")

                for tool_call in pending_tool_calls:
                    # 兼容多种格式
                    if isinstance(tool_call, FunctionCall):
                        # LiveKit 原生格式
                        function_name = tool_call.name
                        arguments = json.loads(tool_call.arguments) if isinstance(tool_call.arguments,
                                                                                  str) else tool_call.arguments
                        call_id = tool_call.call_id
                    else:
                        # OpenAI 格式
                        function_name = tool_call.function.name
                        arguments = json.loads(tool_call.function.arguments)
                        call_id = tool_call.id

                    logger.info(f"🔧 执行: {function_name}({arguments})")

                    # 添加函数调用到上下文
                    func_call = FunctionCall(
                        call_id=call_id,
                        name=function_name,
                        arguments=json.dumps(arguments, ensure_ascii=False)
                    )
                    chat_context.items.append(func_call)

                    # 执行工具
                    tool_result = await self._execute_tool(function_name, arguments)

                    # 添加函数输出到上下文
                    func_output = FunctionCallOutput(
                        call_id=call_id,
                        name=function_name,
                        output=tool_result,
                        is_error=False
                    )
                    chat_context.items.append(func_output)

                # ✅ 递归调用，让 AI 根据工具结果生成自然语言回答
                logger.info("🔄 根据工具结果生成回答...")
                await self.process_llm_response(chat_context)
                return

            # 保存并播放助手回复
            if full_response:
                tts_stream.flush()
                chat_context.add_message(
                    role="assistant",
                    content=full_response
                )
                logger.info(f"🤖 AI: {full_response}")

                # 播放音频
                async for audio_chunk in tts_stream:
                    if hasattr(audio_chunk, 'frame'):
                        await self.audio_source.capture_frame(audio_chunk.frame)
                    else:
                        await self.audio_source.capture_frame(audio_chunk)

            await tts_stream.aclose()

        except Exception as e:
            logger.error(f"❌ LLM/TTS 错误: {e}", exc_info=True)
            # 发送错误提示
            try:
                error_text = "抱歉，我遇到了一些问题，请稍后再试。"
                tts_stream.push_text(error_text)
                tts_stream.flush()
                async for audio_chunk in tts_stream:
                    if hasattr(audio_chunk, 'frame'):
                        await self.audio_source.capture_frame(audio_chunk.frame)
                    else:
                        await self.audio_source.capture_frame(audio_chunk)
                await tts_stream.aclose()
            except:
                pass

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
                    chat_context.add_message(
                        role="user",
                        content=user_text
                    )

                    # 异步处理 LLM + TTS
                    asyncio.create_task(self.process_llm_response(chat_context))

        await asyncio.gather(
            feed_stt(),
            handle_stt(),
            return_exceptions=True
        )

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