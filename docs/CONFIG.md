# 配置说明

## 配置文件概览

项目包含两个主要配置文件：

1. `wxauto-restful-api/config.yaml` - API 服务配置
2. `wxauto-channel/config.yaml` - Channel 集成配置

## wxauto-restful-api 配置

### 完整配置示例

```yaml
server:
  host: 0.0.0.0        # 监听地址，0.0.0.0 表示所有网卡
  port: 8001           # 监听端口
  reload: false        # 热重载（开发模式）

security:
  token: token         # API 访问令牌

api:
  prefix: /v1          # API 路径前缀
  docs_url: /docs      # API 文档路径

logging:
  level: INFO          # 日志级别: DEBUG, INFO, WARNING, ERROR
  format: "%(asctime)s [%(name)s] [%(levelname)s] [%(filename)s:%(lineno)d]  %(message)s"
```

### 配置项说明

#### server 部分

- **host**: 服务监听地址
  - `0.0.0.0`: 允许所有网卡访问
  - `127.0.0.1`: 仅本机访问
  - 建议生产环境使用 `127.0.0.1`

- **port**: 服务端口
  - 默认: 8001
  - 确保端口未被占用

- **reload**: 热重载
  - `true`: 代码修改后自动重启（开发模式）
  - `false`: 不自动重启（生产模式）

#### security 部分

- **token**: API 访问令牌
  - 用于 HTTP 请求认证
  - 格式: `Authorization: Bearer <token>`
  - 建议使用强密码

#### logging 部分

- **level**: 日志级别
  - `DEBUG`: 详细调试信息
  - `INFO`: 一般信息（推荐）
  - `WARNING`: 警告信息
  - `ERROR`: 仅错误信息

## wxauto-channel 配置

### 完整配置示例

```yaml
# wxauto-restful-api 连接配置
wxapi:
  base_url: http://localhost:8001
  token: token

# OpenClaw Gateway 配置
openclaw:
  gateway_url: http://127.0.0.1:18789
  token: your_openclaw_token_here
  agent_id: main

# 微信昵称（用于过滤自己的消息）
my_nickname: ABLE - AI科研助手

# 临时文件目录
temp_dir: ./tmp

# 私聊配置
private_chats:
  - name: 张三
    enabled: true
  - name: 李四
    enabled: false

# 群聊配置
group_chats:
  - name: 工作群
    enabled: true
    reply_mode: at_me_only
    sender_whitelist: []
    sender_blacklist: []

  - name: 测试群
    enabled: true
    reply_mode: all
    sender_whitelist: [张三, 李四]
    sender_blacklist: [广告bot]
```

### 配置项说明

#### wxapi 部分

- **base_url**: wxauto-restful-api 地址
  - 默认: `http://localhost:8001`
  - 如果 API 在其他机器，修改为对应地址

- **token**: API 访问令牌
  - 必须与 wxauto-restful-api 的 token 一致

#### openclaw 部分

- **gateway_url**: OpenClaw Gateway 地址
  - 默认: `http://127.0.0.1:18789`
  - 如果 Gateway 在其他机器，修改为对应地址

- **token**: OpenClaw 访问令牌
  - 获取方式: `openclaw gateway token`

- **agent_id**: Agent 标识
  - 默认: `main`
  - 用于区分不同的对话上下文

#### my_nickname

- 你的微信昵称
- **必须与微信中显示的昵称完全一致**
- 用于过滤自己发送的消息，避免无限循环
- 示例: `ABLE - AI科研助手`

#### temp_dir

- 临时文件存储目录
- 用于存储下载的图片、文件等
- 默认: `./tmp`

#### private_chats

私聊监听配置列表。

**字段说明**:

- **name**: 好友备注名或微信昵称
  - 必须与微信中显示的名称完全一致
  - 区分大小写

- **enabled**: 是否启用
  - `true`: 启用监听和回复
  - `false`: 禁用（不监听）

**示例**:

```yaml
private_chats:
  - name: 张三
    enabled: true    # 会回复张三的所有消息

  - name: 李四
    enabled: false   # 不监听李四的消息
```

#### group_chats

群聊监听配置列表。

**字段说明**:

- **name**: 群聊名称
  - 必须与微信中显示的群名完全一致
  - 区分大小写

- **enabled**: 是否启用
  - `true`: 启用监听和回复
  - `false`: 禁用（不监听）

- **reply_mode**: 回复模式
  - `at_me_only`: 仅当消息 @我时才回复
  - `all`: 回复所有消息（自动过滤自己的消息）

- **sender_whitelist**: 发送者白名单
  - 数组格式: `[张三, 李四]`
  - 为空 `[]` 表示不限制
  - 非空时，仅回复白名单中的人

- **sender_blacklist**: 发送者黑名单
  - 数组格式: `[广告bot, 垃圾消息]`
  - 为空 `[]` 表示不限制
  - 非空时，不回复黑名单中的人

**示例**:

```yaml
group_chats:
  # 工作群：仅 @我时回复
  - name: 工作群
    enabled: true
    reply_mode: at_me_only
    sender_whitelist: []
    sender_blacklist: []

  # 测试群：回复所有消息，但仅限白名单
  - name: 测试群
    enabled: true
    reply_mode: all
    sender_whitelist: [张三, 李四]  # 仅回复这两人
    sender_blacklist: []

  # 闲聊群：回复所有消息，排除黑名单
  - name: 闲聊群
    enabled: true
    reply_mode: all
    sender_whitelist: []
    sender_blacklist: [广告bot, 垃圾消息]  # 不回复这些人

  # 禁用的群
  - name: 不活跃群
    enabled: false
    reply_mode: at_me_only
    sender_whitelist: []
    sender_blacklist: []
```

## 消息过滤规则

### 过滤优先级

1. **自消息过滤**（最高优先级）
   - 自动过滤 sender 为以下值的消息：
     - `self` (通过 API 发送)
     - `自己` (wxautox4 标识)
     - `SelfMsg`
     - 配置的 `my_nickname`

2. **enabled 检查**
   - 如果 `enabled: false`，不监听该对象

3. **reply_mode 检查**
   - `at_me_only`: 检查消息是否 @我
   - `all`: 继续下一步检查

4. **黑名单检查**
   - 如果 sender 在 `sender_blacklist` 中，不回复

5. **白名单检查**
   - 如果 `sender_whitelist` 非空且 sender 不在其中，不回复

### 过滤示例

**场景 1: 工作群，仅 @我时回复**

```yaml
- name: 工作群
  enabled: true
  reply_mode: at_me_only
  sender_whitelist: []
  sender_blacklist: []
```

- 张三: "大家好" → 不回复
- 张三: "@AI助手 你好" → 回复
- 自己: "测试" → 不回复（自消息过滤）

**场景 2: 测试群，回复所有消息，仅限白名单**

```yaml
- name: 测试群
  enabled: true
  reply_mode: all
  sender_whitelist: [张三, 李四]
  sender_blacklist: []
```

- 张三: "你好" → 回复
- 李四: "测试" → 回复
- 王五: "hello" → 不回复（不在白名单）
- 自己: "测试" → 不回复（自消息过滤）

**场景 3: 闲聊群，回复所有消息，排除黑名单**

```yaml
- name: 闲聊群
  enabled: true
  reply_mode: all
  sender_whitelist: []
  sender_blacklist: [广告bot]
```

- 张三: "你好" → 回复
- 广告bot: "推广信息" → 不回复（在黑名单）
- 自己: "测试" → 不回复（自消息过滤）

## 配置管理工具

使用 `config_manager.py` 快速管理配置：

```bash
cd wxauto-channel
python config_manager.py
```

或使用便捷脚本：

```bash
scripts\config.bat
```

### 功能菜单

```
=== wxauto-channel 配置管理 ===
1. 查看当前配置
2. 添加私聊监听
3. 添加群聊监听
4. 删除监听对象
5. 启用/禁用监听对象
0. 退出
```

### 使用示例

**添加私聊监听**:
1. 选择 `2`
2. 输入好友名称: `张三`
3. 自动添加并保存

**添加群聊监听**:
1. 选择 `3`
2. 输入群名: `工作群`
3. 选择回复模式: `1` (at_me_only) 或 `2` (all)
4. 自动添加并保存

**删除监听对象**:
1. 选择 `4`
2. 输入要删除的名称: `张三`
3. 确认删除

## 配置最佳实践

### 安全建议

1. **修改默认 token**
   ```yaml
   security:
     token: your_strong_password_here
   ```

2. **限制 API 访问**
   ```yaml
   server:
     host: 127.0.0.1  # 仅本机访问
   ```

3. **使用白名单**
   - 对于重要群聊，使用白名单限制回复对象

### 性能优化

1. **禁用不需要的监听**
   ```yaml
   - name: 不活跃群
     enabled: false
   ```

2. **使用 at_me_only 模式**
   - 减少不必要的 AI 调用
   ```yaml
   reply_mode: at_me_only
   ```

3. **合理使用黑名单**
   - 过滤广告、机器人等

### 调试技巧

1. **启用 DEBUG 日志**
   ```yaml
   logging:
     level: DEBUG
   ```

2. **使用监控脚本**
   ```bash
   cd wxauto-channel
   monitor.bat
   ```

3. **测试配置**
   - 先在测试群测试
   - 确认无误后再应用到正式群

## 配置模板

### 最小配置

```yaml
wxapi:
  base_url: http://localhost:8001
  token: token

openclaw:
  gateway_url: http://127.0.0.1:18789
  token: your_token
  agent_id: main

my_nickname: 你的昵称

private_chats: []
group_chats: []
```

### 生产环境配置

```yaml
wxapi:
  base_url: http://localhost:8001
  token: strong_password_here

openclaw:
  gateway_url: http://127.0.0.1:18789
  token: your_openclaw_token
  agent_id: main

my_nickname: AI助手

temp_dir: ./tmp

private_chats:
  - name: 老板
    enabled: true
  - name: 同事A
    enabled: true

group_chats:
  - name: 工作群
    enabled: true
    reply_mode: at_me_only
    sender_whitelist: []
    sender_blacklist: [广告bot]

  - name: 项目群
    enabled: true
    reply_mode: at_me_only
    sender_whitelist: []
    sender_blacklist: []
```

## 常见配置错误

### 错误 1: my_nickname 不匹配

**症状**: AI 回复自己的消息，导致无限循环

**原因**: `my_nickname` 与微信昵称不一致

**解决**: 确保 `my_nickname` 与微信中显示的昵称完全一致

### 错误 2: token 不一致

**症状**: Channel 无法连接 API，报 401 错误

**原因**: wxauto-channel 的 token 与 wxauto-restful-api 不一致

**解决**: 确保两个配置文件中的 token 完全相同

### 错误 3: 名称不匹配

**症状**: 配置了监听，但没有收到消息

**原因**: 配置的名称与微信中显示的不一致

**解决**:
- 检查大小写
- 检查空格
- 复制粘贴微信中的名称

### 错误 4: OpenClaw token 错误

**症状**: Channel 收到消息但无法回复

**原因**: OpenClaw token 不正确

**解决**:
```bash
openclaw gateway token
```
复制正确的 token 到配置文件

## 下一步

- [API 文档](API.md) - 了解 API 接口
- [故障排除](TROUBLESHOOTING.md) - 解决常见问题
