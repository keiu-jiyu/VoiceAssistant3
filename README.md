```markdown
# 🎤 Voice Assistant - AI 语音助手
---

## 📖 项目简介

Voice Assistant 是一个现代化的实时语音对话系统，结合了 WebRTC 技术和 AI 语音处理能力。通过 LiveKit 实现低延迟的音频传输，使用 Supabase 进行用户认证管理，提供流畅的语音交互体验。

### 🎯 核心技术栈

**后端：**
- **FastAPI** - 高性能异步 Web 框架
- **LiveKit** - 实时音视频通信
- **Supabase** - 用户认证和数据库
- **Pydantic** - 数据验证
- **Python-Jose** - JWT 令牌处理

**前端：**
- **React 18** - 用户界面框架
- **Vite** - 现代化构建工具
- **LiveKit React Components** - 实时音频组件
- **Axios** - HTTP 客户端

---

## ✨ 功能特性

### 🔐 用户认证
- ✅ 基于 Supabase 的安全认证
- ✅ JWT Token 管理
- ✅ 会话持久化
- ✅ 自动登录状态检测

### 🎙️ 实时语音
- ✅ 低延迟音频传输（< 100ms）
- ✅ 自动回声消除
- ✅ 噪音抑制
- ✅ 自动增益控制

### 📊 状态监控
- ✅ 实时连接状态显示
- ✅ 音频轨道可视化
- ✅ 参与者列表
- ✅ 网络质量指示

### 🎨 用户界面
- ✅ 响应式设计
- ✅ 深色模式
- ✅ 现代化 UI 组件
- ✅ 流畅的动画效果

---

## 🏗️ 项目架构

voice-assistant/
├── backend/                    # 后端服务
│   ├── api/                   # API 层
│   │   ├── server.py          # FastAPI 应用入口
│   │   ├── routes.py          # API 路由定义
│   │   └── services/          # 业务逻辑层
│   │       └── auth_service.py    # 认证服务
│   ├── core/                  # 核心模块
│   │   ├── config.py          # 配置管理
│   │   └── logger.py          # 日志系统
│   ├── .env.example           # 环境变量模板
│   └── requirements.txt       # Python 依赖
│
├── frontend/                   # 前端应用
│   ├── src/
│   │   ├── App.jsx            # 主应用组件
│   │   ├── main.jsx           # 应用入口
│   │   └── index.css          # 全局样式
│   ├── public/                # 静态资源
│   ├── .env.example           # 前端环境变量模板
│   ├── package.json           # Node 依赖
│   ├── vite.config.js         # Vite 配置
│   └── index.html             # HTML 模板
│
├── .gitignore
├── README.md
└── LICENSE

---

## 🚀 快速开始

### 📋 前置要求

确保你的开发环境已安装以下工具：

- **Python** 3.9 或更高版本
- **Node.js** 18 或更高版本
- **npm** 或 **yarn**
- **Git**

### 🔑 准备工作

#### 1. 创建 LiveKit 账号

1. 访问 [LiveKit Cloud](https://cloud.livekit.io/)
2. 注册并创建新项目
3. 获取以下凭据：
   - `LIVEKIT_URL` (WebSocket URL)
   - `LIVEKIT_API_KEY`
   - `LIVEKIT_API_SECRET`

#### 2. 创建 Supabase 项目

1. 访问 [Supabase](https://supabase.com/)
2. 创建新项目
3. 在 Authentication 中启用 Email 认证
4. 创建测试用户（推荐使用 SQL）：

```sql
-- 在 Supabase SQL Editor 中执行
INSERT INTO auth.users (
  instance_id,
  id,
  aud,
  role,
  email,
  encrypted_password,
  email_confirmed_at,
  created_at,
  updated_at,
  confirmation_token,
  email_change,
  email_change_token_new,
  recovery_token
) VALUES (
  '00000000-0000-0000-0000-000000000000',
  gen_random_uuid(),
  'authenticated',
  'authenticated',
  'test@example.com',
  crypt('password123', gen_salt('bf')),
  NOW(),
  NOW(),
  NOW(),
  '',
  '',
  '',
  ''
);
```

5. 获取以下凭据：
   - `SUPABASE_URL`
   - `SUPABASE_KEY` (anon/public key)
   - `SUPABASE_JWT_SECRET` (在 Settings > API > JWT Secret)

---

### 📥 安装步骤

#### 1. 克隆仓库

```bash
git clone https://github.com/your-username/voice-assistant.git
cd voice-assistant
```

#### 2. 后端设置

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的配置
```

**`.env` 配置示例：**

```env
# LiveKit 配置
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret

# Supabase 配置
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_key
SUPABASE_JWT_SECRET=your_jwt_secret

# API 配置
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true

# CORS 配置
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

#### 3. 前端设置

```bash
# 打开新终端，进入前端目录
cd frontend

# 安装依赖
npm install
# 或使用 yarn
yarn install

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件
```

**前端 `.env` 配置：**

```env
VITE_API_URL=http://localhost:8000
```

---

### ▶️ 运行项目

#### 启动后端

```bash
cd backend
python api/server.py
```

后端将运行在 `http://localhost:8000`

访问 API 文档：`http://localhost:8000/docs`

#### 启动前端

```bash
cd frontend
npm run dev
# 或
yarn dev
```

前端将运行在 `http://localhost:5173`

---

## 🎮 使用指南

### 登录

1. 打开浏览器访问 `http://localhost:5173`
2. 使用测试账号登录：
   - **邮箱**: `test@example.com`
   - **密码**: `password123`

### 开始对话

1. 登录成功后，点击"连接房间"按钮
2. 允许浏览器访问麦克风权限
3. 等待连接建立（状态显示"已连接"）
4. 开始语音对话

### 功能操作

- **静音/取消静音**: 点击麦克风按钮
- **断开连接**: 点击"断开连接"按钮
- **登出**: 点击"登出"按钮

---

## 📡 API 文档

### 认证相关

#### POST `/api/login`

用户登录

**请求体：**
```json
{
  "email": "test@example.com",
  "password": "password123"
}
```

**响应：**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "test@example.com"
  }
}
```

#### GET `/api/me`

获取当前用户信息

**请求头：**
```
Authorization: Bearer <access_token>
```

**响应：**
```json
{
  "id": "uuid",
  "email": "test@example.com",
  "aud": "authenticated",
  "role": "authenticated"
}
```

### LiveKit 相关

#### GET `/api/token`

获取 LiveKit 房间令牌

**请求头：**
```
Authorization: Bearer <access_token>
```

**查询参数：**
- `room_name` (可选): 房间名称，默认为 "default-room"
- `participant_name` (可选): 参与者名称，默认为用户邮箱

**响应：**
```json
{
  "token": "eyJ...",
  "url": "wss://your-project.livekit.cloud",
  "room_name": "default-room",
  "participant_name": "test@example.com"
}
```

---

## 🔧 配置说明

### 后端配置 (`backend/core/config.py`)

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `LIVEKIT_URL` | LiveKit 服务器地址 | - |
| `LIVEKIT_API_KEY` | LiveKit API 密钥 | - |
| `LIVEKIT_API_SECRET` | LiveKit API 密钥 | - |
| `SUPABASE_URL` | Supabase 项目 URL | - |
| `SUPABASE_KEY` | Supabase 公钥 | - |
| `SUPABASE_JWT_SECRET` | JWT 签名密钥 | - |
| `API_HOST` | API 服务器地址 | `0.0.0.0` |
| `API_PORT` | API 服务器端口 | `8000` |
| `DEBUG` | 调试模式 | `false` |
| `CORS_ORIGINS` | 允许的跨域源 | `*` |

### 前端配置

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `VITE_API_URL` | 后端 API 地址 | `http://localhost:8000` |

---

## 🐛 常见问题

### 1. 连接失败

**问题**: 无法连接到 LiveKit 房间

**解决方案**:
- 检查 LiveKit 凭据是否正确
- 确认防火墙未阻止 WebSocket 连接
- 验证 CORS 配置

### 2. 认证错误

**问题**: 登录失败或 401 错误

**解决方案**:
- 确认 Supabase 凭据正确
- 检查用户是否已创建
- 验证 JWT Secret 配置

### 3. 麦克风权限

**问题**: 无法访问麦克风

**解决方案**:
- 浏览器设置中允许麦克风权限
- 使用 HTTPS（生产环境必需）
- 检查浏览器兼容性

### 4. 跨域问题

**问题**: CORS 错误

**解决方案**:
```python
# backend/.env
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

---

## 🚀 部署指南

### Docker 部署

创建 `Dockerfile`:

```dockerfile
# Backend Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

EXPOSE 8000

CMD ["python", "api/server.py"]
```

创建 `docker-compose.yml`:

```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - backend/.env
    restart: unless-stopped

  frontend:
    image: node:18-alpine
    working_dir: /app
    volumes:
      - ./frontend:/app
    ports:
      - "5173:5173"
    command: sh -c "npm install && npm run dev -- --host"
    restart: unless-stopped
```

运行：
```bash
docker-compose up -d
```

### 生产环境部署

#### 后端（使用 Gunicorn）

```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker api.server:app --bind 0.0.0.0:8000
```

#### 前端（构建静态文件）

```bash
cd frontend
npm run build
# 将 dist/ 目录部署到静态文件服务器
```

---

## 📊 性能优化

### 后端优化

- 使用连接池管理数据库连接
- 启用 HTTP/2
- 配置适当的 Worker 数量
- 使用 Redis 缓存认证 Token

### 前端优化

- 启用代码分割
- 压缩静态资源
- 使用 CDN 加速
- 实现懒加载

---

## 🔒 安全建议

### 生产环境必须：

1. **使用 HTTPS**
   ```nginx
   server {
       listen 443 ssl;
       ssl_certificate /path/to/cert.pem;
       ssl_certificate_key /path/to/key.pem;
   }
   ```

2. **限制 CORS**
   ```python
   CORS_ORIGINS=https://yourdomain.com
   ```

3. **Token 过期时间**
   ```python
   # 设置合理的 Token 过期时间
   ACCESS_TOKEN_EXPIRE_MINUTES = 30
   ```

4. **环境变量保护**
   - 永远不要将 `.env` 文件提交到 Git
   - 使用密钥管理服务（如 AWS Secrets Manager）

5. **速率限制**
   ```python
   from slowapi import Limiter
   limiter = Limiter(key_func=get_remote_address)
   ```

---

## 🤝 贡献指南

我们欢迎所有形式的贡献！

### 如何贡献

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 开发规范

- 遵循 PEP 8 (Python) 和 ESLint (JavaScript)
- 编写清晰的提交信息
- 添加必要的测试
- 更新相关文档

---

## 📝 更新日志

### v1.0.0 (2024-01-XX)

- ✨ 初始版本发布
- 🔐 Supabase 用户认证
- 🎙️ LiveKit 实时语音
- 📊 状态监控面板
- 🎨 现代化 UI 界面

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 👨‍💻 作者

**Your Name**

- GitHub: https://github.com/keiu-jiyu
- Email: jiyuzhao521@outlook.com

---

## 🙏 致谢

- [LiveKit](https://livekit.io/) - 实时音视频通信
- [Supabase](https://supabase.com/) - 后端服务
- [FastAPI](https://fastapi.tiangolo.com/) - Web 框架
- [React](https://reactjs.org/) - 前端框架

---

## 📮 联系我们

有问题或建议？欢迎：

- 提交 [Issue](https://github.com/your-username/voice-assistant/issues)
- 发送邮件到 jiyuzhao521@outlook.com
- 加入我们的 [Discord 社区](#)

---
<div align="center">

**⭐ 如果这个项目对你有帮助，请给它一个星标！**

✅ **精美的格式和徽章**

需要我调整任何部分吗？ 🚀
