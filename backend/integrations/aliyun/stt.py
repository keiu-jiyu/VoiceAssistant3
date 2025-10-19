# backend/integrations/aliyun/stt.py
import os
import json
import asyncio
import aiohttp
from typing import Optional
from livekit.agents import stt, utils, APIConnectOptions, DEFAULT_API_CONNECT_OPTIONS


class AliyunSTT(stt.STT):
    """阿里云实时语音识别"""

    def __init__(
            self,
            *,
            api_key: str,
            model: str = "paraformer-realtime-v2",
            language: str = "zh-CN",
    ):
        super().__init__(
            capabilities=stt.STTCapabilities(
                streaming=True,
                interim_results=True
            )
        )
        self._api_key = api_key
        self._model = model
        self._language = language
        self._session: Optional[aiohttp.ClientSession] = None

    def _ensure_session(self) -> aiohttp.ClientSession:
        if self._session is None:
            self._session = aiohttp.ClientSession()
        return self._session

    async def _recognize_impl(
            self,
            buffer: utils.AudioBuffer,
            *,
            language: str | None = None,
    ) -> stt.SpeechEvent:
        raise NotImplementedError("请使用 stream() 方法")

    def stream(
            self,
            *,
            language: str | None = None,
            conn_options: APIConnectOptions = DEFAULT_API_CONNECT_OPTIONS,
    ) -> "AliyunSTTStream":
        return AliyunSTTStream(
            stt=self,
            conn_options=conn_options,
            api_key=self._api_key,
            model=self._model,
            language=language or self._language,
        )

    async def aclose(self) -> None:
        if self._session:
            await self._session.close()


class AliyunSTTStream(stt.SpeechStream):
    """阿里云 STT 流"""

    def __init__(
            self,
            *,
            stt: AliyunSTT,
            conn_options: APIConnectOptions,
            api_key: str,
            model: str,
            language: str,
    ):
        super().__init__(stt=stt, conn_options=conn_options)
        self._api_key = api_key
        self._model = model
        self._language = language
        self._ws: Optional[aiohttp.ClientWebSocketResponse] = None
        self._session = stt._ensure_session()
        self._task_started_event = asyncio.Event()
        self._closed = False
        self._running = False
        self._main_task = asyncio.create_task(self._run())

    async def _run(self) -> None:
        if self._running:
            return

        self._running = True

        url = "wss://dashscope.aliyuncs.com/api-ws/v1/inference"
        import urllib.parse
        params = {
            "model": self._model,
            "api_key": self._api_key,
        }
        full_url = f"{url}?{urllib.parse.urlencode(params)}"

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json"
        }

        try:
            self._ws = await self._session.ws_connect(full_url, headers=headers)

            await asyncio.gather(
                self._send_audio_task(),
                self._receive_task(),
                return_exceptions=True
            )
        except Exception as e:
            print(f"❌ STT 错误: {e}")
        finally:
            self._running = False
            if self._ws and not self._ws.closed:
                await self._ws.close()

    async def _send_audio_task(self) -> None:
        import uuid
        task_id = str(uuid.uuid4())

        run_task_msg = {
            "header": {
                "action": "run-task",
                "task_id": task_id,
                "streaming": "duplex"
            },
            "payload": {
                "task_group": "audio",
                "task": "asr",
                "function": "recognition",
                "model": self._model,
                "parameters": {
                    "format": "pcm",
                    "sample_rate": 16000,
                    "language_hints": ["zh"],
                    "max_sentence_silence": 800,
                },
                "input": {}
            }
        }

        await self._ws.send_str(json.dumps(run_task_msg))

        try:
            await asyncio.wait_for(self._task_started_event.wait(), timeout=10.0)
        except asyncio.TimeoutError:
            return

        async for frame in self._input_ch:
            if self._closed or frame is None:
                break

            if not self._ws.closed:
                audio_bytes = frame.data.tobytes()
                await self._ws.send_bytes(audio_bytes)

        if not self._ws.closed:
            finish_msg = {
                "header": {
                    "action": "finish-task",
                    "task_id": task_id,
                    "streaming": "duplex"
                },
                "payload": {"input": {}}
            }
            await self._ws.send_str(json.dumps(finish_msg))

    async def _receive_task(self) -> None:
        async for msg in self._ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                data = json.loads(msg.data)
                header = data.get("header", {})
                event = header.get("event")

                if event == "task-started":
                    self._task_started_event.set()

                elif event == "result-generated":
                    payload = data.get("payload", {})
                    output = payload.get("output", {})

                    if "sentence" in output:
                        sentence = output["sentence"]
                        text = sentence.get("text", "").strip()
                        sentence_end = sentence.get("sentence_end", False)

                        if text and not sentence.get("heartbeat", False):
                            speech_event = stt.SpeechEvent(
                                type=stt.SpeechEventType.FINAL_TRANSCRIPT if sentence_end else stt.SpeechEventType.INTERIM_TRANSCRIPT,
                                alternatives=[
                                    stt.SpeechData(
                                        language=self._language,
                                        text=text,
                                        confidence=0.9,
                                    )
                                ],
                            )
                            self._event_ch.send_nowait(speech_event)

                elif event in ["task-finished", "task-failed"]:
                    break

    async def aclose(self) -> None:
        self._closed = True

        try:
            await self._input_ch.send(None)
        except:
            pass

        if self._main_task and not self._main_task.done():
            self._main_task.cancel()
            try:
                await self._main_task
            except asyncio.CancelledError:
                pass

        if self._ws and not self._ws.closed:
            await self._ws.close()

        self._event_ch.close()
