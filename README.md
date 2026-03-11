# OpenClaw WeChat Channel

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-blue.svg" alt="Python 3.11+">
  <img src="https://img.shields.io/badge/Platform-Windows-green.svg" alt="Windows">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="MIT License">
  <img src="https://img.shields.io/badge/WeChat-Automation-orange.svg" alt="WeChat Automation">
</p>

<p align="center">
  <b>将你的 OpenClaw AI 助手接入微信</b><br>
  完整的微信自动化 AI 助手解决方案，支持私聊、群聊、图片、文件等多种消息类型
</p>

---

## 📋 目录

- [✨ 功能特性](#-功能特性)
- [🚀 快速开始（小白教程）](#-快速开始小白教程)
- [📁 项目结构](#-项目结构)
- [📖 使用指南](#-使用指南)
- [🏗️ 项目架构](#️-项目架构)
- [📋 故障排除](#-故障排除)
- [⚠️ 免责声明](#️-免责声明)
- [👥 加入社区](#-加入社区)

---

## ✨ 功能特性

### 💬 消息支持

| 功能 | 私聊 | 群聊 | 说明 |
|------|------|------|------|
| **文本消息** | ✅ | ✅ | 支持纯文本、表情、链接 |
| **@提及回复** | - | ✅ | 可配置仅在@我时回复 |
| **图片识别** | ✅ | ✅ | AI 可分析图片内容 |
| **文件处理** | ✅ | ✅ | 支持 txt/csv/md/json 等文本文件 |
| **语音消息** | ✅ | ✅ | 语音转文字后处理 |
| **引用回复** | ✅ | ✅ | 可引用原消息回复 |

### 🎯 智能功能

| 功能 | 说明 |
|------|------|
| **自消息过滤** | 自动过滤自己发送的消息，避免无限循环 |
| **黑白名单** | 群聊支持发送者白名单/黑名单过滤 |
| **回复模式** | `at_me_only` 仅@回复 / `all` 回复所有 |
| **多账号隔离** | 不同聊天对象使用独立会话上下文 |
| **多媒体理解** | AI 可理解图片内容并回复 |
| **文件阅读** | AI 可阅读文本文件内容并总结 |

### 🔧 系统功能

| 功能 | 说明 |
|------|------|
| **RESTful API** | 完整的 HTTP API，支持发送/接收消息 |
| **WebSocket 实时推送** | 低延迟消息推送 |
| **配置管理工具** | 可视化交互式配置 |
| **日志监控** | 实时查看运行日志 |
| **自动重连** | WebSocket 断线自动重连 |
| **健康检查** | 服务状态监控接口 |

---

## 🚀 快速开始（小白教程）

> **预计耗时**: 10-15 分钟
> **难度**: ⭐⭐☆☆☆（零基础友好）

### 第一步：环境准备（3分钟）

#### 1.1 检查系统要求

确保你的电脑满足以下条件：

- [x] **Windows 10/11** 操作系统
- [x] **微信 PC 版** 已安装并登录（必须保持登录状态）
- [x] **Python 3.11+** （下面教你安装）

#### 1.2 安装 Python

如果你还没有 Python，按以下步骤安装：

1. 访问 [Python 官网下载页](https://www.python.org/downloads/)
2. 点击 **"Download Python 3.11.x"** 按钮
3. 运行下载的安装程序，**重要**：勾选 **"Add Python to PATH"**
4. 点击 "Install Now" 完成安装

**验证安装**：打开命令提示符（CMD），输入：

```bash
python --version
```

看到 `Python 3.11.x` 即表示安装成功。

---

### 第二步：下载项目（2分钟）

#### 2.1 下载项目代码

**方式一：使用 Git（推荐，方便后续更新）**

```bash
# 打开 CMD，执行以下命令
git clone https://github.com/SEUWanglibo/openclaw-wechat-channel.git
cd openclaw-wechat-channel
```

**方式二：直接下载 ZIP**

1. 访问项目主页：https://github.com/SEUWanglibo/openclaw-wechat-channel
2. 点击绿色 **"<> Code"** 按钮
3. 选择 **"Download ZIP"**
4. 解压到任意文件夹，记住路径

---

### 第三步：安装依赖（3分钟）

#### 3.1 一键安装（推荐）

```bash
# 在项目文件夹内，双击运行
scripts\install.bat
```

或者 CMD 中执行：

```bash
cd scripts
install.bat
```

#### 3.2 手动安装（如果一键安装失败）

```bash
# 1. 安装 wxauto-restful-api 依赖
cd wxauto-restful-api
pip install -r requirements.txt

# 2. 安装 wxauto-channel 依赖
cd ../wxauto-channel
pip install requests websockets pyyaml
```

---

### 第四步：配置服务（5分钟）

#### 4.1 配置 Channel

```bash
# 进入 wxauto-channel 目录
cd wxauto-channel

# 复制配置模板（Windows CMD）
copy config.yaml.template config.yaml

# 用记事本打开配置文件
notepad config.yaml
```

#### 4.2 修改关键配置

你需要修改以下几个地方：

**① 配置 OpenClaw Token**

```yaml
openclaw:
  gateway_url: http://127.0.0.1:18789
  token: 你的_openclaw_token_here  # ← 改成你的 Token
  agent_id: main
```

> 💡 **如何获取 OpenClaw Token？**
> 运行 `openclaw gateway token` 命令即可显示

**② 设置你的微信昵称**

```yaml
my_nickname: 你的微信昵称  # ← 改成你微信中显示的昵称（重要！）
```

> ⚠️ **注意**：这里的昵称必须与微信中显示的完全一致，否则会导致 AI 回复自己的消息！

**③ 配置监听对象**

**私聊配置**（你想让 AI 回复哪些好友）：

```yaml
private_chats:
  - name: 张三          # 好友的备注名或微信昵称
    enabled: true       # true=启用, false=禁用

  - name: 李四
    enabled: true
```

**群聊配置**（你想让 AI 回复哪些群）：

```yaml
group_chats:
  - name: 测试群                    # 群聊名称
    enabled: true                   # 启用
    reply_mode: at_me_only          # at_me_only=仅@时回复, all=回复所有消息
    sender_whitelist: []            # 白名单（可选）
    sender_blacklist: []            # 黑名单（可选）

  - name: 工作群
    enabled: true
    reply_mode: all                 # 回复群内所有消息
    sender_whitelist: [老板, 经理]   # 只回复这些人的消息
```

#### 4.3 配置 wxauto-restful-api（可选）

默认配置通常无需修改，如需修改：

```bash
cd wxauto-restful-api
notepad config.yaml
```

---

### 第五步：启动服务（2分钟）

#### 5.1 一键启动（推荐）

```bash
# 在项目根目录，双击运行
scripts\start-all.bat
```

看到以下提示表示启动成功：

```
========================================
  所有服务已启动！
========================================

服务状态:
- wxauto-restful-api: http://localhost:8001/docs
- OpenClaw Gateway: http://127.0.0.1:18789/health
- wxauto-channel: 运行中
```

#### 5.2 手动启动（如果一键启动失败）

需要打开 **两个 CMD 窗口**：

**窗口 1 - 启动 API 服务**：

```bash
cd wxauto-restful-api
python run.py
```

等待看到 `Uvicorn running on http://0.0.0.0:8001` 表示成功。

**窗口 2 - 启动 Channel**：

```bash
cd wxauto-channel
python wxauto_channel.py
```

等待看到 `启动监听，目标: [xxx]` 表示成功。

---

### 第六步：测试验证

#### 6.1 检查服务状态

打开浏览器，访问：http://localhost:8001/docs

能看到 API 文档页面表示 API 服务正常。

#### 6.2 发送测试消息

1. 向配置的好友发送一条消息
2. 或在配置的群中 @你的 AI 助手
3. 观察 AI 是否回复

#### 6.3 查看日志

如果出现异常，查看日志排查：

```bash
cd wxauto-channel
monitor.bat
```

---

## 📁 项目结构

```
openclaw-wechat-channel/
│
├── README.md                    # 项目说明文档（本文件）
├── LICENSE                      # MIT 许可证
├── DISCLAIMER.md                # 免责声明
├── CONTRIBUTING.md              # 贡献指南
│
├── wxauto-restful-api/          # 微信自动化 API 服务
│   ├── app/                     # API 核心代码
│   │   ├── api/                 # API 路由
│   │   ├── services/            # 业务逻辑
│   │   ├── utils/               # 工具函数
│   │   └── main.py              # FastAPI 应用入口
│   ├── run.py                   # 启动脚本
│   ├── run.bat                  # Windows 启动脚本
│   ├── stop.bat                 # 停止脚本
│   ├── config.yaml.template     # 配置文件模板
│   ├── pyproject.toml           # Python 项目配置
│   └── requirements.txt         # Python 依赖列表
│
├── wxauto-channel/              # OpenClaw Channel 集成
│   ├── wxauto_channel.py        # Channel 主程序
│   ├── config_manager.py        # 配置管理工具
│   ├── config.yaml.template     # 配置文件模板
│   ├── requirements.txt         # Python 依赖列表
│   ├── start.bat                # 启动脚本
│   ├── stop.bat                 # 停止脚本
│   └── monitor.bat              # 日志监控脚本
│
├── scripts/                     # 便捷脚本
│   ├── install.bat              # 一键安装脚本
│   ├── start-all.bat            # 启动所有服务
│   ├── stop-all.bat             # 停止所有服务
│   └── config.bat               # 配置管理快捷方式
│
├── docs/                        # 详细文档
│   ├── INSTALL.md               # 详细安装指南
│   ├── CONFIG.md                # 配置说明文档
│   └── TROUBLESHOOTING.md       # 故障排除指南
│
└── .github/                     # GitHub 配置
    └── ISSUE_TEMPLATE/          # Issue 模板
```

---

## 📖 使用指南

### 配置管理工具

使用交互式配置工具快速管理监听对象：

```bash
scripts\config.bat
```

**功能菜单**：

```
==================================================
  OpenClaw WeChat Channel - 配置管理
==================================================

1. 查看当前配置
2. 添加私聊监听
3. 添加群聊监听
4. 删除监听对象
5. 启用/禁用监听对象
6. 编辑配置文件
0. 退出
```

### 群聊回复模式详解

| 模式 | 适用场景 | 说明 |
|------|----------|------|
| `at_me_only` | 大群、公开群 | 只有消息中 @你的昵称时，AI 才会回复 |
| `all` | 小群、工作群 | AI 会回复群内所有消息（自动过滤自己） |

### 黑白名单配置

```yaml
group_chats:
  - name: 工作群
    enabled: true
    reply_mode: all
    sender_whitelist: [张三, 李四]  # 只回复白名单中的成员
    sender_blacklist: []            # 黑名单为空表示不限制

  - name: 技术群
    enabled: true
    reply_mode: all
    sender_whitelist: []            # 白名单为空表示不限制
    sender_blacklist: [广告bot]     # 不回复黑名单中的成员
```

**注意**：白名单和黑名单同时存在时，白名单优先级更高。

### 支持的消息类型

| 消息类型 | AI 处理方式 |
|----------|-------------|
| 文本 | 直接处理 |
| 图片 | AI 可识别图片内容 |
| 文件 | 文本文件会被读取内容，其他文件显示文件名 |
| 语音 | 语音消息标识 |
| 视频 | 视频消息标识 |

---

## 🏗️ 项目架构

### 数据流

```
┌─────────────┐    ┌──────────────┐    ┌─────────────────┐
│  微信 PC 端  │───▶│  wxautox4    │───▶│ wxauto-restful  │
│             │    │  (第三方依赖) │    │    -api         │
└─────────────┘    └──────────────┘    └────────┬────────┘
                                                 │
                                                 │ WebSocket
                                                 ▼
┌─────────────┐    ┌──────────────┐    ┌─────────────────┐
│  微信 PC 端  │◀───│  wxautox4    │◀───│  wxauto-channel │
│             │    │  (第三方依赖) │    │   (本项目)      │
└─────────────┘    └──────────────┘    └────────┬────────┘
                                                 │
                                                 │ HTTP
                                                 ▼
                                        ┌─────────────────┐
                                        │ OpenClaw Gateway│
                                        │   (第三方依赖)   │
                                        └────────┬────────┘
                                                 │
                                                 ▼
                                        ┌─────────────────┐
                                        │    AI 模型      │
                                        │  (Claude/GPT等) │
                                        └─────────────────┘
```

### 组件说明

| 组件 | 类型 | 说明 |
|------|------|------|
| **wxauto-restful-api** | 本项目 | FastAPI 实现的微信自动化 RESTful API |
| **wxauto-channel** | 本项目 | OpenClaw Channel 实现，处理消息流转 |
| **wxautox4** | 第三方依赖 | 微信自动化核心库（需单独获取） |
| **OpenClaw Gateway** | 第三方依赖 | AI 模型统一网关（开源） |

---

## 📋 故障排除

### 常见问题速查

| 问题 | 可能原因 | 解决方案 |
|------|----------|----------|
| API 启动失败 | 端口 8001 被占用 | 关闭占用程序或修改 `config.yaml` 中的端口 |
| Channel 无法连接 API | API 未启动或 token 不匹配 | 确认 API 已启动，检查两个 config.yaml 中的 token 是否一致 |
| AI 不回复消息 | OpenClaw Gateway 未启动 | 运行 `openclaw gateway start` |
| AI 回复自己的消息 | `my_nickname` 配置错误 | 确保与微信昵称完全一致 |
| 重复回复 | 多个 Channel 实例运行 | 运行 `scripts\stop-all.bat` 后重新启动 |
| 微信频繁掉线 | 操作太频繁 | 减少监听群数量，增加回复间隔 |

### 查看日志

```bash
# Channel 日志
cd wxauto-channel
type channel.log

# 实时监控日志
monitor.bat

# API 日志
cd wxauto-restful-api
type wxauto_api.log
```

### 完全重启

如果出现问题，尝试完全重启：

```bash
# 1. 停止所有服务
scripts\stop-all.bat

# 2. 等待 5 秒

# 3. 重新启动
scripts\start-all.bat
```

更多问题请参考 [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

---

## ⚠️ 免责声明

**重要提示**: 使用本项目前请仔细阅读 [DISCLAIMER.md](DISCLAIMER.md)

- 微信官方禁止使用第三方自动化工具，使用可能导致账号被封
- 本项目仅供学习研究使用，请遵守当地法律法规
- 因使用本项目导致的任何损失，项目作者不承担责任
- **本项目代码禁止用于商业用途**（第三方依赖的使用遵循其 respective 协议）

---

## 👥 加入社区

<p align="center">
  <b>扫码加入微信交流群，获取技术支持</b>
</p>

<p align="center">
  <img src="docs/images/wechat-group-qr.png" alt="微信群二维码" width="300">
</p>

<p align="center">
  <i>如果二维码过期，请在 GitHub Issues 留言获取新二维码</i>
</p>

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

详细指南请参考 [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 📄 许可证

本项目基于 [MIT License](LICENSE) 开源。

---

## 🙏 致谢

- [wxautox4](https://docs.wxauto.org/) - 微信自动化库
- [OpenClaw](https://github.com/openclaw) - AI 模型网关
- [FastAPI](https://fastapi.tiangolo.com/) - 现代 Web 框架

---

<p align="center">
  <b>如果本项目对你有帮助，请给个 ⭐ Star 支持一下！</b>
</p>
