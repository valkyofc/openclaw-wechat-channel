# 安装指南

## 系统要求

### 硬件要求
- CPU: 双核及以上
- 内存: 4GB 及以上
- 硬盘: 至少 2GB 可用空间

### 软件要求
- **操作系统**: Windows 10/11 (64位)
- **Python**: 3.11 或更高版本
- **微信**: 微信 PC 版（最新版本）
- **OpenClaw**: OpenClaw CLI 工具

## 详细安装步骤

### 1. 安装 Python

#### 下载 Python

访问 [Python 官网](https://www.python.org/downloads/) 下载 Python 3.11 或更高版本。

#### 安装注意事项

1. 勾选 "Add Python to PATH"
2. 选择 "Customize installation"
3. 确保勾选 "pip" 和 "py launcher"
4. 安装路径建议使用默认路径

#### 验证安装

打开命令提示符（cmd），输入：

```bash
python --version
```

应该显示类似 `Python 3.11.x` 的版本信息。

### 2. 安装 OpenClaw

```bash
pip install openclaw
```

验证安装：

```bash
openclaw --version
```

### 3. 配置 OpenClaw Gateway

#### 启动 Gateway

```bash
openclaw gateway start
```

#### 获取 Token

```bash
openclaw gateway token
```

记下这个 token，后面配置时需要用到。

#### 验证 Gateway

```bash
curl http://127.0.0.1:18789/health
```

应该返回 `{"ok":true,"status":"live"}`

### 4. 安装项目依赖

#### 安装 wxauto-restful-api 依赖

```bash
cd wxauto-openclaw-channel\wxauto-restful-api

# 方式一：使用 uv（推荐，速度更快）
pip install uv
uv sync

# 方式二：使用 pip
pip install fastapi uvicorn wxautox pyyaml python-multipart websockets
```

#### 安装 wxauto-channel 依赖

```bash
cd ..\wxauto-channel
pip install requests websockets pyyaml
```

### 5. 配置服务

#### 配置 wxauto-restful-api

编辑 `wxauto-restful-api\config.yaml`:

```yaml
server:
  host: 0.0.0.0
  port: 8001
  reload: false

security:
  token: token  # 可以修改为更安全的 token

logging:
  level: INFO
```

#### 配置 wxauto-channel

编辑 `wxauto-channel\config.yaml`:

```yaml
wxapi:
  base_url: http://localhost:8001
  token: token  # 必须与 API 的 token 一致

openclaw:
  gateway_url: http://127.0.0.1:18789
  token: your_openclaw_token_here  # 替换为步骤 3 获取的 token
  agent_id: main

my_nickname: 你的微信昵称  # 重要：必须与微信中显示的昵称完全一致

temp_dir: ./tmp

# 私聊配置示例
private_chats:
  - name: 张三
    enabled: true
  - name: 李四
    enabled: false

# 群聊配置示例
group_chats:
  - name: 测试群
    enabled: true
    reply_mode: at_me_only  # at_me_only 或 all
    sender_whitelist: []
    sender_blacklist: []
```

**重要配置说明**：

1. **my_nickname**: 必须与微信中显示的昵称完全一致，用于过滤自己的消息
2. **openclaw.token**: 使用步骤 3 获取的 token
3. **wxapi.token**: 必须与 wxauto-restful-api 的 token 一致

### 6. 首次启动

#### 启动微信

确保微信 PC 版已登录。

#### 启动 wxauto-restful-api

```bash
cd wxauto-restful-api
run.bat
```

等待看到类似以下输出：

```
======================================================================
wxautox4 RESTful API
======================================================================
[服务地址] http://0.0.0.0:8001
[API文档] http://127.0.0.1:8001/docs
======================================================================
```

浏览器会自动打开 API 文档页面。

#### 启动 wxauto-channel

打开新的命令提示符窗口：

```bash
cd wxauto-channel
start.bat
```

#### 验证运行

1. 访问 http://localhost:8001/docs 查看 API 文档
2. 运行监控脚本查看日志：
   ```bash
   cd wxauto-channel
   monitor.bat
   ```
3. 向配置的聊天对象发送测试消息

### 7. 使用配置管理工具

添加监听对象：

```bash
cd wxauto-channel
python config_manager.py
```

或双击运行 `scripts\config.bat`

## 快速启动脚本

安装完成后，可以使用便捷脚本：

```bash
# 启动所有服务
scripts\start-all.bat

# 停止所有服务
scripts\stop-all.bat

# 配置管理
scripts\config.bat
```

## 验证安装

### 检查清单

- [ ] Python 3.11+ 已安装
- [ ] OpenClaw Gateway 正常运行
- [ ] wxauto-restful-api 启动成功
- [ ] wxauto-channel 启动成功
- [ ] 微信已登录
- [ ] 配置文件已正确填写
- [ ] 测试消息能正常回复

### 测试步骤

1. **测试 API**
   ```bash
   curl -H "Authorization: Bearer token" http://localhost:8001/v1/listen/status
   ```
   应该返回监听状态信息。

2. **测试 OpenClaw**
   ```bash
   curl http://127.0.0.1:18789/health
   ```
   应该返回 `{"ok":true,"status":"live"}`

3. **测试消息回复**
   - 向配置的私聊对象发送消息
   - 或在配置的群聊中 @AI 助手
   - 观察是否收到回复

## 常见安装问题

### Python 版本过低

**错误**: `SyntaxError` 或 `requires-python >=3.11`

**解决**: 升级 Python 到 3.11 或更高版本

### pip 安装失败

**错误**: `pip is not recognized`

**解决**:
1. 重新安装 Python，勾选 "Add Python to PATH"
2. 或手动添加 Python 到系统环境变量

### wxautox 安装失败

**错误**: `error: Microsoft Visual C++ 14.0 or greater is required`

**解决**: 安装 [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)

### 端口被占用

**错误**: `Address already in use: 8001`

**解决**:
1. 修改 `wxauto-restful-api\config.yaml` 中的端口号
2. 或停止占用 8001 端口的程序

### OpenClaw Gateway 无法启动

**错误**: `Failed to start gateway`

**解决**:
1. 检查是否已安装 OpenClaw: `pip install openclaw`
2. 查看 OpenClaw 日志: `openclaw gateway logs`
3. 尝试重启: `openclaw gateway restart`

### 微信无法连接

**错误**: `无法找到微信窗口`

**解决**:
1. 确保微信 PC 版已登录
2. 不要最小化微信窗口
3. 重启 wxauto-restful-api

## 下一步

安装完成后，请阅读：
- [配置说明](CONFIG.md) - 详细的配置选项
- [API 文档](API.md) - API 接口说明
- [故障排除](TROUBLESHOOTING.md) - 常见问题解决

## 获取帮助

如果遇到问题：
1. 查看日志文件
2. 阅读故障排除文档
3. 提交 Issue 并附上详细的错误信息
