# 故障排除指南

## 常见问题

### 1. 服务启动问题

#### 问题: wxauto-restful-api 启动失败

**症状**:
- 运行 `run.bat` 后立即退出
- 提示端口被占用
- 提示 Python 模块未找到

**解决方案**:

1. **检查 Python 版本**
   ```bash
   python --version
   ```
   确保版本 >= 3.11

2. **检查端口占用**
   ```bash
   netstat -ano | findstr :8001
   ```
   如果端口被占用，修改 `config.yaml` 中的端口号或停止占用进程

3. **重新安装依赖**
   ```bash
   cd wxauto-restful-api
   pip install uv
   uv sync
   ```

4. **查看详细错误**
   ```bash
   python run.py
   ```
   查看完整的错误信息

#### 问题: wxauto-channel 启动失败

**症状**:
- 提示无法连接 API
- 提示配置文件错误
- 提示 OpenClaw 连接失败

**解决方案**:

1. **检查 wxauto-restful-api 是否运行**
   ```bash
   curl -H "Authorization: Bearer token" http://localhost:8001/v1/listen/status
   ```

2. **检查配置文件**
   - 确认 `config.yaml` 存在
   - 确认 token 与 API 一致
   - 确认 OpenClaw token 正确

3. **检查 OpenClaw Gateway**
   ```bash
   openclaw gateway status
   curl http://127.0.0.1:18789/health
   ```

4. **查看日志**
   ```bash
   cd wxauto-channel
   type channel.log
   ```

### 2. 连接问题

#### 问题: 无法连接微信

**症状**:
- 提示"无法找到微信窗口"
- 提示"微信未登录"

**解决方案**:

1. **确保微信已登录**
   - 打开微信 PC 版
   - 确保已扫码登录
   - 不要最小化微信窗口

2. **重启 wxauto-restful-api**
   ```bash
   cd wxauto-restful-api
   stop.bat
   run.bat
   ```

3. **检查微信版本**
   - 建议使用最新版本微信
   - 某些旧版本可能不兼容

#### 问题: WebSocket 连接断开

**症状**:
- 日志显示 "WebSocket 断开"
- 消息无法接收

**解决方案**:

1. **检查网络连接**
   - 确保本地网络正常

2. **重启服务**
   ```bash
   scripts\stop-all.bat
   scripts\start-all.bat
   ```

3. **检查监听状态**
   ```bash
   curl -H "Authorization: Bearer token" http://localhost:8001/v1/listen/status
   ```

4. **查看 API 日志**
   ```bash
   cd wxauto-restful-api
   type wxauto_logs\app_YYYYMMDD.log
   ```

### 3. 消息处理问题

#### 问题: 收不到消息

**症状**:
- 发送消息后没有回复
- 日志中没有收到消息的记录

**解决方案**:

1. **检查配置**
   - 确认监听对象已启用 (`enabled: true`)
   - 确认名称与微信中完全一致（区分大小写）

2. **检查过滤规则**
   - 群聊: 检查 `reply_mode` 设置
   - 检查白名单/黑名单配置

3. **查看监听状态**
   ```bash
   curl -H "Authorization: Bearer token" http://localhost:8001/v1/listen/status
   ```

4. **查看日志**
   ```bash
   cd wxauto-channel
   monitor.bat
   ```

#### 问题: AI 回复自己的消息（无限循环）

**症状**:
- AI 不断回复自己发送的消息
- 日志中看到 sender=self 的消息被处理

**解决方案**:

1. **检查 my_nickname 配置**
   ```yaml
   my_nickname: 你的微信昵称  # 必须与微信中显示的完全一致
   ```

2. **检查代码版本**
   - 确保 `wxauto_channel.py` 包含 "self" 过滤
   - 查看第 258 行是否包含:
     ```python
     if sender in ("自己", "SelfMsg", "self", self.config.my_nickname):
     ```

3. **重启服务**
   ```bash
   cd wxauto-channel
   stop.bat
   start.bat
   ```

#### 问题: 重复回复消息

**症状**:
- 发送一条消息，收到多条相同回复

**解决方案**:

1. **检查是否有多个实例运行**
   ```bash
   wmic process where "name='python.exe' and CommandLine like '%wxauto_channel%'" get ProcessId,CommandLine
   ```

2. **停止所有实例**
   ```bash
   scripts\stop-all.bat
   ```

3. **重新启动**
   ```bash
   scripts\start-all.bat
   ```

4. **检查监听状态**
   ```bash
   curl -H "Authorization: Bearer token" http://localhost:8001/v1/listen/status
   ```
   确保每个对象只有 1 个连接

### 4. OpenClaw 问题

#### 问题: OpenClaw 无法回复

**症状**:
- 收到消息但没有回复
- 日志显示 "OpenClaw 调用失败"

**解决方案**:

1. **检查 Gateway 状态**
   ```bash
   openclaw gateway status
   curl http://127.0.0.1:18789/health
   ```

2. **检查 token**
   ```bash
   openclaw gateway token
   ```
   确保 token 与配置文件一致

3. **重启 Gateway**
   ```bash
   openclaw gateway restart
   ```

4. **查看 Gateway 日志**
   ```bash
   openclaw gateway logs
   ```

#### 问题: OpenClaw 响应慢

**症状**:
- 消息发送后很久才收到回复

**解决方案**:

1. **检查网络连接**
   - OpenClaw 需要访问 AI 模型 API

2. **检查 AI 模型配置**
   - 某些模型响应较慢
   - 考虑切换到更快的模型

3. **查看 Gateway 日志**
   ```bash
   openclaw gateway logs
   ```

### 5. 配置问题

#### 问题: 配置文件错误

**症状**:
- 提示 YAML 解析错误
- 提示配置项缺失

**解决方案**:

1. **检查 YAML 格式**
   - 确保缩进正确（使用空格，不要用 Tab）
   - 确保冒号后有空格
   - 确保列表项前有 `-`

2. **使用模板**
   ```bash
   copy config.yaml.template config.yaml
   ```

3. **在线验证**
   - 使用在线 YAML 验证工具检查格式

#### 问题: 名称不匹配

**症状**:
- 配置了监听但没有效果

**解决方案**:

1. **复制粘贴名称**
   - 从微信中复制名称
   - 粘贴到配置文件

2. **检查特殊字符**
   - 注意空格、标点符号
   - 注意全角/半角字符

3. **使用配置管理工具**
   ```bash
   cd wxauto-channel
   python config_manager.py
   ```

### 6. 性能问题

#### 问题: CPU 占用高

**症状**:
- Python 进程 CPU 占用持续很高

**解决方案**:

1. **检查日志级别**
   ```yaml
   logging:
     level: INFO  # 不要使用 DEBUG
   ```

2. **减少监听对象**
   - 禁用不需要的监听

3. **使用 at_me_only 模式**
   ```yaml
   reply_mode: at_me_only
   ```

#### 问题: 内存占用高

**症状**:
- Python 进程内存持续增长

**解决方案**:

1. **定期重启服务**
   - 每天重启一次

2. **清理临时文件**
   ```bash
   cd wxauto-channel
   rmdir /s /q tmp
   mkdir tmp
   ```

3. **检查日志文件大小**
   - 定期清理或归档日志

## 调试技巧

### 启用详细日志

**wxauto-restful-api**:
```yaml
# config.yaml
logging:
  level: DEBUG
```

**wxauto-channel**:
```python
# wxauto_channel.py 第 24 行
level=logging.DEBUG
```

### 实时监控日志

```bash
# wxauto-channel
cd wxauto-channel
monitor.bat

# wxauto-restful-api
cd wxauto-restful-api
powershell -Command "Get-Content wxauto_logs\app_*.log -Wait -Tail 20"
```

### 测试 API 连接

```bash
# 测试健康检查
curl http://localhost:8001/health

# 测试监听状态
curl -H "Authorization: Bearer token" http://localhost:8001/v1/listen/status

# 测试发送消息
curl -X POST http://localhost:8001/v1/wechat/send ^
  -H "Authorization: Bearer token" ^
  -H "Content-Type: application/json" ^
  -d "{\"who\":\"测试对象\",\"msg\":\"测试消息\"}"
```

### 测试 OpenClaw

```bash
# 测试健康检查
curl http://127.0.0.1:18789/health

# 测试对话
curl -X POST http://127.0.0.1:18789/v1/chat/completions ^
  -H "Authorization: Bearer your_token" ^
  -H "Content-Type: application/json" ^
  -d "{\"messages\":[{\"role\":\"user\",\"content\":\"你好\"}]}"
```

## 获取帮助

### 日志位置

- **wxauto-restful-api**: `wxauto-restful-api/wxauto_logs/app_YYYYMMDD.log`
- **wxauto-channel**: `wxauto-channel/channel.log`
- **OpenClaw Gateway**: 运行 `openclaw gateway logs`

### 提交 Issue

如果问题仍未解决，请提交 Issue 并附上：

1. **系统信息**
   - 操作系统版本
   - Python 版本
   - 微信版本

2. **错误信息**
   - 完整的错误堆栈
   - 相关日志片段

3. **配置信息**
   - 配置文件内容（隐藏敏感信息）

4. **复现步骤**
   - 详细的操作步骤
   - 预期结果和实际结果

## 常用命令速查

```bash
# 安装
scripts\install.bat

# 启动所有服务
scripts\start-all.bat

# 停止所有服务
scripts\stop-all.bat

# 配置管理
scripts\config.bat

# 监控日志
cd wxauto-channel
monitor.bat

# 检查服务状态
curl http://localhost:8001/health
curl http://127.0.0.1:18789/health
openclaw gateway status

# 查看监听状态
curl -H "Authorization: Bearer token" http://localhost:8001/v1/listen/status

# 重启 OpenClaw Gateway
openclaw gateway restart

# 查看 OpenClaw 日志
openclaw gateway logs
```
