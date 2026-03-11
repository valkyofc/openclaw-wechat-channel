# 发布前检查清单

## ✅ 隐私检查

- [x] **config.yaml 已删除** - 包含真实 OpenClaw token
- [x] **config.yaml 在 .gitignore 中** - 确保不会被提交
- [x] **中文文件已重命名**:
  - [x] `启动面板.bat` → `launch-panel.bat`
- [x] **已删除的冗余/过时文档**:
  - [x] `QUICKSTART.md` - 与 README 重复
  - [x] `使用说明.md` - 与 README 和 docs/INSTALL.md 重复
  - [x] `项目交付说明.md` - 内部交付文档，不适合开源
  - [x] `FILELIST.md` - 内容已合并到 README
  - [x] `wxauto-restful-api/README.md` - 包含过时信息，已删除
- [x] **检查代码中没有真实 API key** - 只有模板值如 `token`, `your_openclaw_token_here`

## GitHub 仓库设置

- [ ] 创建 GitHub 账号（如果没有）
- [ ] 创建新仓库：`openclaw-wechat-channel`
- [ ] 设置仓库为 Public
- [ ] 添加仓库描述："OpenClaw 微信 Channel - 将 AI 助手接入微信的开源解决方案"
- [ ] 添加 Topics: `openclaw`, `wechat`, `automation`, `ai`, `channel`

## 文件准备

- [x] README.md - 项目说明（已更新，小白友好）
- [x] LICENSE - MIT 许可证
- [x] DISCLAIMER.md - 免责声明（已更新，区分代码与第三方）
- [x] CONTRIBUTING.md - 贡献指南
- [x] .gitignore - 忽略文件（包含 config.yaml）
- [x] config.yaml.template - 配置模板
- [x] RELEASE_NOTES.md - Release 内容
- [x] PROMOTION.md - 推广文案

## 代码整理

- [x] 检查代码中是否包含敏感信息
  - [x] API Token - 确认只有模板值
  - [x] 激活码 - 无
  - [x] 个人微信信息 - 已删除 config.yaml
- [x] 确保 config.yaml 被正确忽略
- [x] 检查代码注释完整
- [x] 确保所有脚本文件编码正确（UTF-8）

## 文档准备

- [x] docs/ 目录下的文档完整
  - [x] INSTALL.md
  - [x] CONFIG.md
  - [x] TROUBLESHOOTING.md
- [x] 微信群二维码图片已添加到 docs/images/
  - [x] 路径: `docs/images/wechat-group-qr.png`

## 首次提交

```bash
# 0. 确保 config.yaml 不被 git 追踪（如果之前曾 git add 过）
cd /Users/wlb/Claude_code/wxauto-openclaw-channel
git rm --cached wxauto-restful-api/config.yaml 2>/dev/null || true
git rm --cached wxauto-channel/config.yaml 2>/dev/null || true

# 1. 初始化本地仓库
cd /Users/wlb/Claude_code/wxauto-openclaw-channel
git init

# 2. 添加远程仓库
git remote add origin https://github.com/SEUWanglibo/openclaw-wechat-channel.git

# 3. 添加文件（注意：config.yaml 会被 .gitignore 自动忽略）
git add .

# 4. 检查是否有敏感文件被添加
# 如果看到 config.yaml，说明 gitignore 有问题，立即停止！
git status

# 5. 提交
git commit -m "Initial commit: OpenClaw WeChat Channel v1.0.0"

# 6. 推送
git branch -M main
git push -u origin main

# 7. 创建标签（用于 Release）
git tag -a v1.0.0 -m "Initial release v1.0.0"
git push origin v1.0.0
```

## GitHub Release 创建

推送后访问：`https://github.com/SEUWanglibo/openclaw-wechat-channel/releases`

1. 点击 **"Draft a new release"**
2. 选择标签：**v1.0.0**
3. 标题：`OpenClaw WeChat Channel v1.0.0 - 将 AI 助手接入微信`
4. 内容复制 [RELEASE_NOTES.md](RELEASE_NOTES.md) 的内容
5. 点击 **"Publish release"**

## GitHub 功能配置

- [ ] 启用 Issues
- [ ] 启用 Discussions（可选）
- [ ] Issue 模板已配置
  - [x] Bug 报告模板
  - [x] 功能建议模板
  - [x] 问题咨询模板

## 推广准备

- [x] 推广文案已准备（见 [PROMOTION.md](PROMOTION.md)）
- [x] 准备发布的平台清单：
  - [ ] V2EX
  - [ ] 知乎
  - [ ] 掘金
  - [ ] 技术微信群

## 发布后

- [ ] 在微信群通知
- [ ] 发布到相关技术社区
  - [ ] V2EX
  - [ ] 知乎
  - [ ] 掘金
- [ ] 收集反馈，快速修复问题

## 版本更新

版本号格式：MAJOR.MINOR.PATCH

- MAJOR: 不兼容的 API 变更
- MINOR: 向后兼容的功能添加
- PATCH: 向后兼容的问题修复

## 联系方式确认

- [x] 微信群二维码路径: `docs/images/wechat-group-qr.png`
- [x] GitHub 用户名: `SEUWanglibo`
- [x] 相关链接已更新

## 二维码过期提醒

⚠️ **重要**：微信群二维码 7 天后会过期（3月18日前）

过期后更新步骤：
```bash
# 1. 替换二维码图片
# 2. 提交更新
git add docs/images/wechat-group-qr.png
git commit -m "docs: update WeChat group QR code"
git push
```

---

**完成以上检查后，就可以正式发布到 GitHub 了！** 🚀
