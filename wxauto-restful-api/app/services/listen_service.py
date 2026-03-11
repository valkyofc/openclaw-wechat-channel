"""
微信消息监听服务
基于wxautox4的AddListenChat和on_message回调机制
"""
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Set, Any, Callable
from collections import defaultdict
from fastapi import WebSocket
from pydantic import BaseModel

from app.models.response import APIResponse
from app.services.wechat_service import get_wechat, check_wechat_alive
from app.services.init import WeChat
import os

# 配置日志
logger = logging.getLogger(__name__)

# 媒体文件下载目录
DOWNLOAD_DIR: str = "./downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# 安全白名单（已禁用，所有联系人都允许监听）
# 如需限制，请在 wxauto_channel 的 config.yaml 中配置
SAFE_CONTACTS: Set[str] = set()

# 沙箱模式：False = 允许监听任意联系人
SANDBOX_MODE: bool = False

# 主事件循环引用（由 FastAPI 启动时注入）
_main_loop: Optional[asyncio.AbstractEventLoop] = None

def set_main_loop(loop: asyncio.AbstractEventLoop):
    global _main_loop
    _main_loop = loop


class ListenMessage(BaseModel):
    """监听消息模型"""
    who: str  # 发送者
    content: str  # 消息内容
    msg_type: str  # 消息类型
    time: str  # 时间戳
    sender: str  # 发送者昵称
    chat_type: str  # 聊天类型

    class Config:
        json_schema_extra = {
            "example": {
                "who": "文件传输助手",
                "content": "测试消息",
                "msg_type": "text",
                "time": "2025-03-05 10:30:00",
                "sender": "自己",
                "chat_type": "friend"
            }
        }


class WebSocketConnectionManager:
    """WebSocket连接管理器"""

    def __init__(self):
        # 活跃的WebSocket连接: {client_id: WebSocket}
        self.active_connections: Dict[str, WebSocket] = {}
        # 监听映射: {who: set(client_ids)}
        self.listener_map: Dict[str, Set[str]] = defaultdict(set)
        # 客户端监听映射: {client_id: set(who)}
        self.self_client_listeners: Dict[str, Set[str]] = defaultdict(set)
        # 回调函数映射: {who: callback}
        self.callbacks: Dict[str, Callable] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        """连接WebSocket"""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"WebSocket客户端 {client_id} 已连接")

    def disconnect(self, client_id: str):
        """断开WebSocket连接"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            # 清理该客户端的监听
            if client_id in self.self_client_listeners:
                for who in self.self_client_listeners[client_id]:
                    if client_id in self.listener_map[who]:
                        self.listener_map[who].remove(client_id)
                    # 如果没有监听者了，清理回调
                    if not self.listener_map[who] and who in self.callbacks:
                        try:
                            wx = get_wechat('')
                            if check_wechat_alive(wx):
                                wx.RemoveListenChat(who)
                            del self.callbacks[who]
                        except Exception as e:
                            logger.error(f"清理监听回调时出错: {e}")
                del self.self_client_listeners[client_id]
            logger.info(f"WebSocket客户端 {client_id} 已断开")

    async def send_personal_message(self, message: dict, client_id: str):
        """发送消息给指定客户端"""
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_json(message)
            except Exception as e:
                logger.error(f"发送消息给客户端 {client_id} 失败: {e}")
                # 发送失败，移除连接
                self.disconnect(client_id)

    async def broadcast_to_listeners(self, who: str, message: dict):
        """向监听指定联系人的所有客户端广播消息"""
        if who in self.listener_map:
            for client_id in list(self.listener_map[who]):
                await self.send_personal_message(message, client_id)

    def add_listener(self, client_id: str, who: str):
        """添加监听"""
        self.listener_map[who].add(client_id)
        self.self_client_listeners[client_id].add(who)

    def remove_listener(self, client_id: str, who: str):
        """移除监听"""
        if who in self.listener_map and client_id in self.listener_map[who]:
            self.listener_map[who].remove(client_id)
        if client_id in self.self_client_listeners and who in self.self_client_listeners[client_id]:
            self.self_client_listeners[client_id].discard(who)

    def get_listeners(self, who: Optional[str] = None) -> Dict[str, Any]:
        """获取监听状态"""
        if who:
            return {
                "who": who,
                "is_listening": who in self.listener_map and len(self.listener_map[who]) > 0,
                "listener_count": len(self.listener_map.get(who, set()))
            }
        else:
            return {
                "active_listeners": {
                    who: len(clients) for who, clients in self.listener_map.items() if clients
                },
                "total_listeners": sum(len(clients) for clients in self.listener_map.values()),
                "active_connections": len(self.active_connections)
            }


# 全局WebSocket管理器
manager = WebSocketConnectionManager()


class ListenService:
    """消息监听服务"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ListenService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # 确保只初始化一次
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self.wx_listeners: Dict[str, Any] = {}  # wx实例映射

    def _create_message_callback(self, who: str) -> Callable:
        """创建消息回调函数"""

        def on_message(msg, chat):
            """处理接收到的消息"""
            try:
                msg_type = getattr(msg, 'type', 'unknown')
                msg_data = {
                    'type': msg_type,
                    'sender': getattr(msg, 'sender', ''),
                    'sender_remark': getattr(msg, 'sender_remark', ''),
                    'content': getattr(msg, 'content', ''),
                    'id': getattr(msg, 'id', ''),
                    'who': who,
                    'chat_type': getattr(chat, 'chat_type', '') if chat else '',
                    'file_path': None,
                }

                # 对媒体消息，下载到本地目录
                if msg_type in ('image', 'file', 'video', 'voice'):
                    try:
                        dl_path = msg.download(dir_path=DOWNLOAD_DIR)
                        msg_data['file_path'] = str(dl_path) if dl_path else None
                    except Exception as dl_err:
                        logger.warning(f"下载媒体文件失败: {dl_err}")
                message_data = {
                    "type": "message",
                    "data": msg_data
                }

                logger.info(f"收到来自 {who} 的消息: {msg_data['content']}")

                # 跨线程安全地将协程提交到主事件循环
                if _main_loop and _main_loop.is_running():
                    asyncio.run_coroutine_threadsafe(
                        manager.broadcast_to_listeners(who, message_data),
                        _main_loop
                    )
                else:
                    logger.warning("主事件循环不可用，消息推送失败")

            except Exception as e:
                logger.error(f"处理消息回调时出错: {e}")

        return on_message

    def is_safe_contact(self, who: str) -> bool:
        """检查联系人是否安全"""
        return who in SAFE_CONTACTS

    def start_listen(
        self,
        who: str,
        wxname: Optional[str] = None
    ) -> APIResponse:
        """启动监听

        Args:
            who: 监听的联系人名称
            wxname: 微信客户端名称

        Returns:
            APIResponse
        """
        try:
            # 安全检查
            if not self.is_safe_contact(who):
                if SANDBOX_MODE:
                    return APIResponse(
                        success=False,
                        message=f"安全限制: 联系人 '{who}' 不在安全白名单中。允许的联系人: {', '.join(SAFE_CONTACTS)}",
                        data={"safe_contacts": list(SAFE_CONTACTS)}
                    )
                else:
                    logger.warning(f"尝试监听非安全联系人: {who}")

            # 获取微信实例
            wx = get_wechat(wxname)

            if not check_wechat_alive(wx):
                return APIResponse(success=False, message="微信实例不可用")

            # 检查是否已经在监听
            if who in manager.callbacks:
                return APIResponse(success=False, message=f"已经在监听 {who}")

            # 先切换到对应聊天窗口
            wx.ChatWith(who)

            # 等待窗口加载完成（增加延迟，避免多窗口冲突）
            import time
            time.sleep(2)

            # 检查是否已有子窗口，如果没有则 AddListenChat 会自动创建
            # AddListenChat 会将聊天窗口独立出去形成 Chat 对象子窗口

            # 创建并注册回调
            callback = self._create_message_callback(who)

            try:
                result = wx.AddListenChat(who, callback)
                # AddListenChat 成功时返回 Chat 对象或字符串，不是字典
                # 只要没抛异常就认为成功
                logger.info(f"AddListenChat 返回: {result}")
            except Exception as e:
                logger.error(f"AddListenChat 失败: {e}")
                # 如果是窗口句柄错误，等待后重试一次
                if "1400" in str(e) or "窗口句柄" in str(e):
                    logger.info(f"窗口句柄错误，等待 3 秒后重试...")
                    time.sleep(3)
                    try:
                        result = wx.AddListenChat(who, callback)
                        logger.info(f"重试成功，返回: {result}")
                    except Exception as e2:
                        return APIResponse(
                            success=False,
                            message=f"启动监听失败（重试后仍失败）: {str(e2)}"
                        )
                else:
                    return APIResponse(
                        success=False,
                        message=f"启动监听失败: {str(e)}"
                    )

            manager.callbacks[who] = callback

            logger.info(f"已启动对 {who} 的监听")

            return APIResponse(
                success=True,
                message=f"已启动对 {who} 的监听",
                data={"who": who, "is_listening": True}
            )

        except Exception as e:
            logger.error(f"启动监听失败: {e}")
            return APIResponse(success=False, message=f"启动监听失败: {str(e)}")

    def stop_listen(
        self,
        who: str,
        wxname: Optional[str] = None
    ) -> APIResponse:
        """停止监听

        Args:
            who: 停止监听的联系人名称
            wxname: 微信客户端名称

        Returns:
            APIResponse
        """
        try:
            # 检查是否在监听
            if who not in manager.callbacks:
                return APIResponse(success=False, message=f"未在监听 {who}")

            # 获取微信实例
            wx = get_wechat(wxname)

            # 移除监听
            if check_wechat_alive(wx):
                try:
                    wx.RemoveListenChat(who)
                except Exception as e:
                    logger.warning(f"移除监听时出错（可能已自动清理）: {e}")

            # 清理回调
            del manager.callbacks[who]

            logger.info(f"已停止对 {who} 的监听")

            return APIResponse(
                success=True,
                message=f"已停止对 {who} 的监听",
                data={"who": who, "is_listening": False}
            )

        except Exception as e:
            logger.error(f"停止监听失败: {e}")
            return APIResponse(success=False, message=f"停止监听失败: {str(e)}")

    def get_listen_status(self, who: Optional[str] = None) -> APIResponse:
        """获取监听状态

        Args:
            who: 指定联系人名称，不指定则返回所有

        Returns:
            APIResponse
        """
        try:
            status_data = manager.get_listeners(who)
            return APIResponse(
                success=True,
                message="",
                data=status_data
            )
        except Exception as e:
            logger.error(f"获取监听状态失败: {e}")
            return APIResponse(success=False, message=f"获取监听状态失败: {str(e)}")

    def batch_start_listen(
        self,
        contacts: List[str],
        wxname: Optional[str] = None
    ) -> APIResponse:
        """批量启动监听

        Args:
            contacts: 联系人名称列表
            wxname: 微信客户端名称

        Returns:
            APIResponse
        """
        results = {
            "success": [],
            "failed": [],
            "skipped": []
        }

        for contact in contacts:
            # 安全检查
            if not self.is_safe_contact(contact):
                results["skipped"].append({
                    "who": contact,
                    "reason": "不在安全白名单中"
                })
                continue

            result = self.start_listen(contact, wxname)
            if result.success:
                results["success"].append(contact)
            else:
                results["failed"].append({
                    "who": contact,
                    "reason": result.message
                })

        return APIResponse(
            success=len(results["failed"]) == 0,
            message=f"批量启动完成: 成功 {len(results['success'])}, 失败 {len(results['failed'])}, 跳过 {len(results['skipped'])}",
            data=results
        )


# 导出管理器和服务实例
__all__ = ['ListenService', 'manager', 'SAFE_CONTACTS', 'SANDBOX_MODE']
