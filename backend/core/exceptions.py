# backend/core/exceptions.py

class VoiceAssistantError(Exception):
    """基础异常"""
    pass


class LiveKitConnectionError(VoiceAssistantError):
    """LiveKit 连接错误"""
    pass


class STTError(VoiceAssistantError):
    """语音识别错误"""
    pass


class LLMError(VoiceAssistantError):
    """大模型错误"""
    pass


class TTSError(VoiceAssistantError):
    """语音合成错误"""
    pass


class ConfigurationError(VoiceAssistantError):
    """配置错误"""
    pass
