# 贡献指南

感谢你对 openclaw-wechat-channel 项目的关注！我们欢迎各种形式的贡献。

## 如何贡献

### 报告 Bug

如果你发现了 Bug，请通过 GitHub Issues 报告，并包含以下信息：

- 问题描述
- 复现步骤
- 期望行为 vs 实际行为
- 环境信息（Windows 版本、Python 版本、微信版本）
- 相关日志片段

### 提交功能建议

有新功能想法？欢迎提交 Issue 讨论：

- 清晰描述功能
- 说明使用场景
- 如果可能，提供实现思路

### 提交代码

1. **Fork 仓库** 并克隆到本地

2. **创建分支**
   ```bash
   git checkout -b feature/your-feature-name
   # 或
   git checkout -b fix/bug-description
   ```

3. **编写代码**
   - 遵循 PEP 8 代码规范
   - 添加必要的注释
   - 保持代码简洁清晰

4. **测试**
   - 确保代码能正常运行
   - 测试各种边界情况

5. **提交更改**
   ```bash
   git add .
   git commit -m "feat: 添加新功能描述"
   ```

   Commit 信息规范：
   - `feat:` 新功能
   - `fix:` 修复 Bug
   - `docs:` 文档更新
   - `refactor:` 代码重构
   - `test:` 测试相关
   - `chore:` 构建/工具相关

6. **推送到你的 Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **创建 Pull Request**
   - 描述变更内容
   - 关联相关 Issue
   - 等待 Review

## 代码规范

### Python 代码风格

- 遵循 [PEP 8](https://pep8.org/)
- 使用 4 空格缩进
- 行长度不超过 100 字符
- 使用有意义的变量名

### 示例

```python
def handle_message(message_data: dict) -> str:
    """处理收到的消息。

    Args:
        message_data: 消息数据字典

    Returns:
        str: 处理结果
    """
    sender = message_data.get("sender", "")
    content = message_data.get("content", "")

    if not sender or not content:
        logger.warning("无效的消息数据")
        return ""

    # 处理逻辑...
    return result
```

## 开发环境设置

```bash
# 1. 克隆仓库
git clone https://github.com/yourusername/openclaw-wechat-channel.git
cd openclaw-wechat-channel

# 2. 创建虚拟环境
python -m venv venv
venv\Scripts\activate

# 3. 安装开发依赖
pip install -r requirements-dev.txt

# 4. 复制配置
cd wxauto-channel
copy config.yaml.template config.yaml
# 编辑 config.yaml 填入你的配置
```

## 注意事项

- 不要提交敏感信息（token、激活码等）
- 不要提交个人配置文件
- 确保代码兼容性（Python 3.11+）
- 更新相关文档

## 社区行为准则

- 友善交流，尊重他人
- 接受建设性批评
- 关注社区最佳利益

## 获取帮助

- GitHub Discussions: 一般性讨论
- GitHub Issues: Bug 报告、功能建议
- 微信群: 见 README 底部二维码

感谢你的贡献！
