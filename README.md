# 📝 更新后的 GitHub README.md

```markdown
# 🎙️ AI 语音助手

基于 LiveKit + 阿里云 NLS + 通义千问的实时语音对话系统

## ✨ 功能特性

- 🎤 **实时语音识别**：使用阿里云语音识别服务（NLS）
- 🤖 **智能对话**：接入阿里云通义千问大模型
- 🔊 **语音合成**：阿里云语音合成（TTS）
- 📡 **实时通信**：基于 LiveKit 的低延迟音视频传输
- 🌐 **Web 界面**：React 前端，简洁易用
- 🛠️ **工具调用**：支持天气查询等外部工具集成

---

## 🏗️ 技术栈

### 后端
- **Python 3.10+**
- **FastAPI** - 高性能 Web 框架
- **LiveKit SDK** - 实时音视频
- **阿里云 SDK** - NLS 语音服务
- **Dashscope** - 通义千问 API

### 前端
- **React 18**
- **LiveKit Components** - 音视频组件
- **Create React App** - 项目脚手架

---

## 📦 项目结构

voice-assistant/
├── backend/                    # 后端服务
│   ├── api/                   # API 服务器
│   │   ├── server.py          # FastAPI 主程序
│   │   └── endpoints/         # API 路由
│   │       └── token.py       # Token 生成
│   ├── agent/                 # AI Agent
│   │   ├── server.py          # Agent 主程序
│   │   ├── assistant.py       # 核心助手逻辑
│   │   └── worker.py          # 语音处理工作流
│   ├── core/                  # 核心配置
│   │   └── config.py          # 环境配置
│   ├── integrations/          # 第三方集成
│   │   ├── aliyun/           # 阿里云服务
│   │   │   ├── stt.py        # 语音识别
│   │   │   ├── tts.py        # 语音合成
│   │   │   └── llm.py        # 通义千问
│   │   └── tools/            # 工具管理
│   │       ├── manager.py    # 工具调用管理器
│   │       └── weather.py    # 天气查询工具
│   ├── requirements.txt       # Python 依赖
│   └── .env                  # 环境变量（需创建）
│
└── frontend/                  # 前端应用
    ├── public/
    ├── src/
    │   ├── App.jsx            # 主组件
    │   ├── index.js           # 入口文件
    │   └── index.css          # 样式
    ├── .env                  # 环境变量（需创建）
    └── package.json           # 依赖配置

---

## 🚀 快速开始

### 1️⃣ 克隆项目

```bash
git clone https://github.com/your-username/voice-assistant.git
cd voice-assistant
```

### 2️⃣ 配置后端

#### 安装依赖

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

#### 配置环境变量

创建 `backend/.env` 文件：

```env
# ============ API 服务配置 ============
DEBUG=false
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=1

# ============ LiveKit Cloud 配置 ============
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=APIxxxxxxxxxxxxx
LIVEKIT_API_SECRET=xxxxxxxxxxxxxxxxx
LIVEKIT_ROOM_NAME=voice-room

# ============ 阿里云通义千问配置 ============
DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxxxx
QWEN_MODEL=qwen-turbo

# ============ 阿里云语音服务 NLS 配置 ============
# 方式1: 直接使用 Token（测试用，24小时有效）
# ALIYUN_NLS_TOKEN=your_nls_token

# 方式2: 使用 AccessKey（生产推荐，自动刷新）
ALIYUN_ACCESS_KEY_ID=LTAI5xxxxxxxxxx
ALIYUN_ACCESS_KEY_SECRET=xxxxxxxxxxxxxxxxx
ALIYUN_APP_KEY=your_app_key

# ============ 日志配置 ============
LOG_LEVEL=INFO
LOG_DIR=logs
```

#### 启动服务

```bash
# 终端 1：启动 API 服务器
python api/server.py api

# 终端 2：启动 AI Agent
python agent/server.py agent
```

---

### 3️⃣ 配置前端

#### 安装依赖

```bash
cd frontend
npm install
```

#### 配置环境变量

创建 `frontend/.env` 文件：

```env
REACT_APP_API_URL=http://localhost:8000
```

#### 启动应用

```bash
npm start
```

浏览器自动打开 `http://localhost:3000`

---

## 🔑 获取必需的 API Keys

### 1. LiveKit Cloud（免费额度）

1. 访问 https://cloud.livekit.io/
2. 注册/登录账号
3. 创建项目
4. 获取：
   - `LIVEKIT_URL`（WebSocket URL）
   - `LIVEKIT_API_KEY`
   - `LIVEKIT_API_SECRET`

### 2. 阿里云通义千问

1. 访问 https://dashscope.aliyun.com/
2. 开通服务（有免费额度）
3. 获取 `DASHSCOPE_API_KEY`

### 3. 阿里云语音服务（NLS）

1. 访问 https://nls-portal.console.aliyun.com/
2. 开通服务
3. 创建项目，获取 `ALIYUN_APP_KEY`
4. 创建 AccessKey（推荐）或使用 24 小时 Token

---

## 📖 使用说明

### 基础对话

1. **启动服务**：确保后端两个服务都已启动
2. **打开网页**：访问 `http://localhost:3000`
3. **授权麦克风**：浏览器会请求麦克风权限
4. **开始对话**：
   - 点击"连接"按钮
   - 等待连接成功（状态变为"已连接"）
   - 直接说话即可，AI 会实时回复

### 工具调用示例

AI 助手现在支持调用外部工具！试试这些命令：

- 🌤️ "今天北京天气怎么样？"
- 🌧️ "查一下上海的天气"
- ☀️ "深圳现在天气如何？"

**工作原理**：
1. AI 识别用户需要查询天气
2. 自动调用天气查询工具
3. 获取实时天气数据
4. 用自然语言播报结果

---

## 🛠️ 工具调用系统

### 架构说明

本项目实现了**降级模式的工具调用**，通过 Prompt 工程让 LLM 返回结构化的工具调用指令。

#### 为什么使用降级模式？

当前 LiveKit 的阿里云插件（`livekit-plugins-aliyun`）**不支持原生 `tool_ctx` 参数**，原因可能是：
- 插件版本较旧
- 阿里云 Qwen API 不支持 OpenAI 式的 Function Calling
- LiveKit 插件未实现完整的工具调用接口

#### 实现方式

```python
# 1. 通过 System Prompt 引导 LLM
system_prompt = """
当需要查询实时信息时，请按以下格式返回：
<tool_call>
{"name": "get_weather", "arguments": {"city": "北京"}}
</tool_call>
"""

# 2. 正则解析 LLM 响应
tool_call_pattern = r'<tool_call>\s*(\{.*?\})\s*</tool_call>'

# 3. 执行工具并返回结果
result = await tool_manager.execute_tool(tool_name, arguments)

# 4. 将结果重新发送给 LLM 生成最终回复
```

### 添加新工具

#### 步骤 1：定义工具

创建 `backend/integrations/tools/your_tool.py`：

```python
import logging

logger = logging.getLogger(__name__)

async def your_tool_function(param1: str, param2: int) -> dict:
    """
    你的工具描述
    
    Args:
        param1: 参数1说明
        param2: 参数2说明
    
    Returns:
        dict: 返回结果
    """
    try:
        # 实现你的工具逻辑
        result = {"status": "success", "data": "..."}
        return result
    except Exception as e:
        logger.error(f"工具执行失败: {e}")
        return {"error": str(e)}

# 导出工具配置
your_tool = {
    "name": "your_tool_name",
    "description": "工具功能描述（告诉 AI 何时使用）",
    "parameters": {
        "type": "object",
        "properties": {
            "param1": {
                "type": "string",
                "description": "参数1的作用"
            },
            "param2": {
                "type": "integer",
                "description": "参数2的作用"
            }
        },
        "required": ["param1"]
    },
    "function": your_tool_function
}
```

#### 步骤 2：注册工具

在 `backend/integrations/tools/manager.py` 中注册：

```python
from .your_tool import your_tool

class ToolManager:
    def __init__(self):
        self.tools = {
            "get_weather": weather_tool,
            "your_tool_name": your_tool,  # 添加新工具
        }
```

#### 步骤 3：测试

启动服务后，尝试触发工具：

```
用户: "请帮我执行XXX操作"
AI: (自动识别并调用 your_tool_name)
```

---

## 🐛 常见问题

### 1. WebSocket 401 错误

**原因**：LiveKit API Key/Secret 不正确

**解决**：
- 检查 `.env` 中的 `LIVEKIT_API_KEY` 和 `LIVEKIT_API_SECRET`
- 确保没有多余空格
- 重新从 LiveKit Cloud 复制

### 2. 麦克风无法连接

**原因**：浏览器权限或 HTTPS 问题

**解决**：
- 确保允许麦克风权限
- 使用 `localhost` 或 HTTPS 访问
- 检查浏览器控制台错误

### 3. AI 无响应

**原因**：通义千问 API 配置错误

**解决**：
- 检查 `DASHSCOPE_API_KEY` 是否正确
- 确认账户有可用额度
- 查看后端日志排查错误

### 4. 语音识别失败

**原因**：阿里云 NLS 配置问题

**解决**：
- 检查 `ALIYUN_ACCESS_KEY_ID`、`ALIYUN_ACCESS_KEY_SECRET`
- 确认 `ALIYUN_APP_KEY` 正确
- 确保服务已开通并有额度

### 5. 工具调用不生效

**原因**：LLM 未正确识别工具调用需求

**解决**：
- 检查 System Prompt 是否正确加载
- 查看后端日志，确认是否解析到 `<tool_call>` 标签
- 尝试更明确的命令，如"查询北京天气"而非"北京天气如何"
- 考虑切换到支持原生 Function Calling 的 LLM（如 OpenAI GPT-4）

### 6. 工具返回结果但 AI 未播报

**原因**：工具结果未正确返回给 LLM

**解决**：
- 检查日志中的 `✅ 工具结果:` 输出
- 确认 `chat_context.messages` 包含工具结果
- 验证 `process_llm_response` 的递归调用逻辑

---

## 📊 系统架构

```
┌─────────────┐      WebSocket       ┌──────────────┐
│   浏览器    │ ←─────────────────→ │  LiveKit     │
│  (React)    │      音视频流        │   Cloud      │
└─────────────┘                      └──────────────┘
       │                                     ↑
       │ HTTP/REST                           │
       ↓                                     │
┌─────────────┐                             │
│  API Server │                             │
│  (FastAPI)  │                             │
└─────────────┘                             │
                                            │
                                            │
┌───────────────────────────────────────────┘
│
│  ┌─────────────────────────────────────┐
│  │         AI Agent Worker              │
│  │  ┌────────────────────────────────┐ │
│  │  │  1. 语音识别 (阿里云 STT)     │ │
│  │  │  2. LLM 对话 (通义千问)       │ │
│  │  │  3. 工具调用 (降级模式)       │ │
│  │  │  4. 语音合成 (阿里云 TTS)     │ │
│  │  └────────────────────────────────┘ │
│  └─────────────────────────────────────┘
└─────────────────────────────────────────┘
```

### 工具调用流程

```
用户语音输入
    ↓
语音识别 (STT)
    ↓
LLM 处理 → 识别需要调用工具
    ↓
解析 <tool_call> 标签
    ↓
执行工具函数 (如查询天气 API)
    ↓
将结果追加到对话历史
    ↓
LLM 根据结果生成回复
    ↓
语音合成 (TTS)
    ↓
播放给用户
```

---

## 🔮 未来计划

- [ ] 支持更多工具（搜索、计算器、日历等）
- [ ] 迁移到原生 Function Calling（OpenAI/Claude）
- [ ] 添加多轮工具调用支持
- [ ] 实现工具调用的可视化调试界面
- [ ] 支持自定义 System Prompt

---

## 🛠️ 开发

### 添加新功能

1. **后端**：在 `backend/agent/assistant.py` 修改对话流程
2. **工具**：在 `backend/integrations/tools/` 添加新工具
3. **前端**：在 `frontend/src/App.jsx` 添加 UI 组件
4. **配置**：在 `.env` 和 `config.py` 添加新配置项

### 调试

```bash
# 后端日志
tail -f backend/logs/app.log

# 前端控制台
# 打开浏览器开发者工具 (F12)
```

### 查看工具调用日志

```bash
# 过滤工具相关日志
grep "工具" backend/logs/app.log
grep "tool_call" backend/logs/app.log
```

---

## 📄 许可证

MIT License

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

如果你添加了新工具或改进了工具调用逻辑，请务必分享 🎉

---

## 📧 联系方式

- GitHub: zhao.jiyu
- Email: jiyuzhao521@outlook.com

---

## 🙏 致谢

- [LiveKit](https://livekit.io/) - 实时通信基础设施
- [阿里云](https://www.aliyun.com/) - 语音服务和 AI 能力
- [FastAPI](https://fastapi.tiangolo.com/) - 现代 Python Web 框架

---

⭐ 如果这个项目对你有帮助，请给个 Star！
```

---

## 🆕 新增的关键更新

### 1. **项目结构** - 添加了工具相关目录
├── integrations/
│   └── tools/
│       ├── manager.py    # 工具管理器
│       └── weather.py    # 天气工具示例

### 2. **使用说明** - 添加了工具调用示例
明确说明如何触发工具调用功能

### 3. **工具调用系统** - 新增完整章节
- 解释为什么使用降级模式
- 详细说明实现方式
- 提供添加新工具的完整教程

### 4. **常见问题** - 添加工具相关问题
- 工具调用不生效
- 工具结果未播报

### 5. **系统架构** - 更新流程图
包含工具调用的完整数据流

### 6. **未来计划** - 添加改进方向
说明项目的演进路线

---

现在你可以直接把这个 README.md 上传到 GitHub 了！🚀
