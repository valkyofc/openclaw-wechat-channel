"""
wxauto_channel.py — WeChat Channel for OpenClaw AI
通过 wxauto-restful-api 监听微信消息，转发给 OpenClaw AI，再将回复发回微信。
"""

import asyncio
import base64
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
import websockets
import yaml

# ─────────────────────────────────────────
# 日志配置
# ─────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("channel.log", encoding="utf-8")
    ],
)
logger = logging.getLogger("wxauto_channel")


# ─────────────────────────────────────────
# Config
# ─────────────────────────────────────────
class Config:
    def __init__(self, path: str = "config.yaml"):
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        wx = data.get("wxapi", {})
        self.wxapi_base_url: str = wx.get("base_url", "http://localhost:8001")
        self.wxapi_token: str = wx.get("token", "token")

        oc = data.get("openclaw", {})
        self.openclaw_gateway_url: str = oc.get("gateway_url", "http://127.0.0.1:18789")
        self.openclaw_token: str = oc.get("token", "")
        self.openclaw_agent_id: str = oc.get("agent_id", "main")

        self.my_nickname: str = data.get("my_nickname", "")
        self.temp_dir: str = data.get("temp_dir", "./tmp")
        os.makedirs(self.temp_dir, exist_ok=True)

        self.private_chats: List[Dict] = data.get("private_chats", [])
        self.group_chats: List[Dict] = data.get("group_chats", [])


# ─────────────────────────────────────────
# MessageFilter
# ─────────────────────────────────────────
class MessageFilter:
    def __init__(self, config: Config):
        self.config = config
        # 构建私聊 / 群聊快速查找字典
        self._private: Dict[str, Dict] = {
            c["name"]: c for c in config.private_chats if c.get("enabled", True)
        }
        self._groups: Dict[str, Dict] = {
            g["name"]: g for g in config.group_chats if g.get("enabled", True)
        }

    def should_reply_private(self, who: str, sender: str) -> bool:
        """私聊过滤：只回复对方（who）的消息，不回复自己的消息"""
        cfg = self._private.get(who)
        if cfg is None:
            return False
        # 私聊中，sender 应该是 who（对方）
        # 如果 sender 是对方，或者 whitelist 为空（兼容旧配置），都回复
        whitelist = cfg.get("whitelist", []) or []
        if whitelist:
            # 如果配置了 whitelist，只在 sender 在白名单中时回复
            return sender in whitelist
        # 默认：只回复对方（who）的消息
        return sender == who

    def should_reply_group(self, group_name: str, sender: str, content: str) -> bool:
        cfg = self._groups.get(group_name)
        if cfg is None:
            return False
        sender_blacklist = cfg.get("sender_blacklist", []) or []
        if sender in sender_blacklist:
            return False
        sender_whitelist = cfg.get("sender_whitelist", []) or []
        if sender_whitelist and sender not in sender_whitelist:
            return False
        reply_mode = cfg.get("reply_mode", "at_me_only")
        if reply_mode == "at_me_only":
            nickname = self.config.my_nickname
            if nickname and f"@{nickname}" not in content:
                return False
        return True

    def is_configured_private(self, who: str) -> bool:
        return who in self._private

    def is_configured_group(self, who: str) -> bool:
        return who in self._groups

    def all_targets(self) -> List[str]:
        return list(self._private.keys()) + list(self._groups.keys())


# ─────────────────────────────────────────
# MediaHandler
# ─────────────────────────────────────────
class MediaHandler:
    IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}

    def build_content(self, msg_type: str, text_prefix: str, file_path: Optional[str]) -> Any:
        """
        根据消息类型和本地文件路径，构建 OpenAI content 字段。
        - 图片：返回 [text, image_url] 列表
        - 其他文件：返回描述文字字符串
        - 无文件路径：返回描述文字字符串
        """
        if not file_path or not os.path.exists(file_path):
            return f"{text_prefix}（文件未找到: {file_path}）"

        ext = Path(file_path).suffix.lower()
        file_size = os.path.getsize(file_path)

        if msg_type == "image" and ext in self.IMAGE_EXTS:
            with open(file_path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            mime = "image/jpeg" if ext in (".jpg", ".jpeg") else f"image/{ext.lstrip('.')}"
            return [
                {"type": "text", "text": text_prefix},
                {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
            ]

        if msg_type in ("file", "voice", "video"):
            # 文本文件读取内容；其他只报文件名+大小
            if ext in (".txt", ".csv", ".md", ".json", ".xml", ".html", ".log"):
                try:
                    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                        file_content = f.read(4000)  # 最多 4000 字符
                    return f"{text_prefix}\n文件内容（前4000字符）:\n{file_content}"
                except Exception:
                    pass
            return f"{text_prefix} [{Path(file_path).name}, {file_size} bytes]"

        return text_prefix


# ─────────────────────────────────────────
# OpenClawClient
# ─────────────────────────────────────────
class OpenClawClient:
    def __init__(self, config: Config):
        self.base_url = config.openclaw_gateway_url.rstrip("/")
        self.token = config.openclaw_token
        self.agent_id = config.openclaw_agent_id
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    def chat(self, content: Any, user: str) -> str:
        """
        向 OpenClaw 发送聊天请求，返回 AI 回复文本。
        content 可以是字符串或 OpenAI content 数组。
        """
        payload = {
            "model": self.agent_id,
            "messages": [
                {"role": "user", "content": content}
            ],
            "user": user,
            "stream": False,
        }
        url = f"{self.base_url}/v1/chat/completions"
        try:
            resp = requests.post(url, headers=self.headers, json=payload, timeout=120)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]
        except requests.exceptions.HTTPError as e:
            logger.error(f"OpenClaw HTTP error: {e.response.status_code} {e.response.text[:200]}")
            raise
        except Exception as e:
            logger.error(f"OpenClaw request failed: {e}")
            raise


# ─────────────────────────────────────────
# WxClient
# ─────────────────────────────────────────
class WxClient:
    def __init__(self, config: Config):
        self.base_url = config.wxapi_base_url.rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {config.wxapi_token}",
            "Content-Type": "application/json",
        }

    def _post(self, path: str, payload: Dict) -> Dict:
        url = f"{self.base_url}{path}"
        resp = requests.post(url, headers=self.headers, json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def send_private(self, who: str, msg: str) -> None:
        self._post("/v1/wechat/send", {"who": who, "msg": msg})

    def send_quote(self, who: str, msg_id: str, content: str) -> None:
        self._post("/v1/chat/msg/quote", {"who": who, "msg_id": msg_id, "content": content})

    def start_listen(self, who: str) -> Dict:
        return self._post("/v1/listen/start", {"who": who})

    def health(self) -> bool:
        try:
            resp = requests.get(f"{self.base_url}/", timeout=5)
            return resp.status_code == 200
        except Exception:
            return False


# ─────────────────────────────────────────
# Channel（主循环）
# ─────────────────────────────────────────
class Channel:
    def __init__(self, config: Config):
        self.config = config
        self.filter = MessageFilter(config)
        self.media = MediaHandler()
        self.openclaw = OpenClawClient(config)
        self.wx = WxClient(config)

    # ── 消息处理 ──────────────────────────
    def _handle_message(self, msg_data: Dict) -> None:
        who: str = msg_data.get("who", "")
        sender: str = msg_data.get("sender", "")
        content: str = msg_data.get("content", "")
        msg_type: str = msg_data.get("type", "text")
        msg_id: str = msg_data.get("id", "")
        chat_type: str = msg_data.get("chat_type", "")
        file_path: Optional[str] = msg_data.get("file_path")

        # 调试日志：记录所有收到的消息
        logger.info(f"收到消息: who={who}, sender={sender}, type={msg_type}, content={content[:50] if content else ''}")

        is_group = self.filter.is_configured_group(who)
        is_private = self.filter.is_configured_private(who)

        # 过滤：只处理外部消息（sender 不是自己）
        if sender in ("自己", "SelfMsg", "self", self.config.my_nickname):
            logger.info(f"[过滤] 自己的消息: sender={sender}, who={who}")
            return

        # 判断是否应该回复
        if is_group:
            if not self.filter.should_reply_group(who, sender, content):
                return
        elif is_private:
            if not self.filter.should_reply_private(who, sender):
                return
        else:
            logger.debug(f"未配置的来源，忽略: who={who}")
            return

        # 构建 content 和 user 字段
        if is_group:
            user_id = f"wechat_{who}"
            text_prefix = f"[{sender} @ {who}]: {content}" if msg_type == "text" else f"[{sender} 发送了{msg_type}]:"
        else:
            user_id = f"wechat_{who}"
            text_prefix = f"[{sender}]: {content}" if msg_type == "text" else f"[{sender} 发送了{msg_type}]:"

        # 处理媒体
        if msg_type == "text":
            oc_content = text_prefix
        else:
            oc_content = self.media.build_content(msg_type, text_prefix, file_path)

        logger.info(f"调用 OpenClaw: user={user_id}, type={msg_type}, from={sender}@{who}")

        try:
            reply = self.openclaw.chat(oc_content, user_id)
        except Exception as e:
            logger.error(f"OpenClaw 调用失败: {e}")
            return

        if not reply:
            logger.warning("OpenClaw 返回空回复，跳过发送")
            return

        logger.info(f"回复 {who}: {reply[:80]}{'...' if len(reply) > 80 else ''}")

        try:
            # 暂时对所有消息使用普通发送，因为引用回复 API 有问题
            # TODO: 修复引用回复后恢复
            self.wx.send_private(who, reply)
        except Exception as e:
            logger.error(f"发送回复失败: {e}")

    # ── WebSocket 监听单个目标 ────────────
    async def _listen_one(self, who: str) -> None:
        ws_url = (
            f"{self.config.wxapi_base_url.replace('http', 'ws')}"
            f"/v1/listen/ws?who={who}&auto_start=true"
        )
        retry_delay = 2
        max_delay = 60

        while True:
            try:
                logger.info(f"WebSocket 连接: {who} → {ws_url}")
                async with websockets.connect(ws_url) as ws:
                    retry_delay = 2  # 重连成功，重置退避
                    async for raw in ws:
                        try:
                            envelope = json.loads(raw)
                        except json.JSONDecodeError:
                            continue

                        ev_type = envelope.get("type")
                        if ev_type == "message":
                            data = envelope.get("data", {})
                            # 在线程池中运行同步处理（requests 调用是阻塞的）
                            loop = asyncio.get_event_loop()
                            await loop.run_in_executor(None, self._handle_message, data)
                        elif ev_type in ("status", "warning"):
                            logger.info(f"[{who}] WS 状态: {envelope.get('data', {})}")
                        elif ev_type == "error":
                            logger.warning(f"[{who}] WS 错误: {envelope.get('data', {})}")

            except websockets.exceptions.ConnectionClosed as e:
                logger.warning(f"[{who}] WebSocket 断开: {e}，{retry_delay}s 后重连…")
            except OSError as e:
                logger.warning(f"[{who}] 连接失败: {e}，{retry_delay}s 后重试…")
            except Exception as e:
                logger.error(f"[{who}] 未知错误: {e}，{retry_delay}s 后重试…")

            await asyncio.sleep(retry_delay)
            retry_delay = min(retry_delay * 2, max_delay)

    # ── 主启动入口 ───────────────────────
    async def run(self) -> None:
        # 检查 wxauto-restful-api 可用性
        if not self.wx.health():
            logger.error(
                f"无法连接到 wxauto-restful-api ({self.config.wxapi_base_url})，请先启动服务。"
            )
            sys.exit(1)

        targets = self.filter.all_targets()
        if not targets:
            logger.error("config.yaml 中未配置任何私聊或群聊，退出。")
            sys.exit(1)

        logger.info(f"启动监听，目标: {targets}")

        # 不再通过 HTTP API 启动监听，完全依赖 WebSocket auto_start
        # 这样可以避免重复监听的问题
        logger.info("通过 WebSocket auto_start 启动监听...")

        # 并发监听所有目标的 WebSocket
        tasks = [asyncio.create_task(self._listen_one(t)) for t in targets]
        await asyncio.gather(*tasks)


# ─────────────────────────────────────────
# 入口
# ─────────────────────────────────────────
if __name__ == "__main__":
    config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
    if not os.path.exists(config_path):
        print(f"找不到配置文件: {config_path}")
        sys.exit(1)

    cfg = Config(config_path)
    channel = Channel(cfg)

    try:
        asyncio.run(channel.run())
    except KeyboardInterrupt:
        logger.info("用户中断，已退出。")
