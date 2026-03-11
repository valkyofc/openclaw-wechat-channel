"""
消息监听API路由
提供RESTful API和WebSocket端点用于微信消息监听
"""
import json
import uuid
from typing import Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from app.services.listen_service import ListenService, manager, SAFE_CONTACTS, SANDBOX_MODE
from app.models.request.listen import (
    StartListenRequest,
    StopListenRequest,
    GetListenStatusRequest,
    BatchStartListenRequest
)
from app.models.response import APIResponse

router = APIRouter()


@router.post(
    "/start",
    operation_id="[listen]启动监听",
    response_model=APIResponse,
    summary="启动指定联系人的消息监听"
)
async def start_listen(
    request: StartListenRequest,
    service: ListenService = Depends()
):
    """启动指定联系人的消息监听

    安全限制: 只能监听白名单中的联系人
    """
    return service.start_listen(who=request.who, wxname=request.wxname)


@router.post(
    "/stop",
    operation_id="[listen]停止监听",
    response_model=APIResponse,
    summary="停止指定联系人的消息监听"
)
async def stop_listen(
    request: StopListenRequest,
    service: ListenService = Depends()
):
    """停止指定联系人的消息监听"""
    return service.stop_listen(who=request.who, wxname=request.wxname)


@router.get(
    "/status",
    operation_id="[listen]获取监听状态",
    response_model=APIResponse,
    summary="获取当前监听状态"
)
async def get_listen_status(
    who: Optional[str] = Query(None, description="指定联系人名称，不指定则返回所有"),
    service: ListenService = Depends()
):
    """获取当前监听状态

    Args:
        who: 可选，指定联系人名称

    Returns:
        监听状态信息
    """
    return service.get_listen_status(who=who)


@router.post(
    "/batch/start",
    operation_id="[listen]批量启动监听",
    response_model=APIResponse,
    summary="批量启动多个联系人的消息监听"
)
async def batch_start_listen(
    request: BatchStartListenRequest,
    service: ListenService = Depends()
):
    """批量启动多个联系人的消息监听

    只监听白名单中的联系人，其他联系人将被跳过
    """
    return service.batch_start_listen(contacts=request.contacts, wxname=request.wxname)


@router.get(
    "/config",
    operation_id="[listen]获取配置",
    summary="获取监听服务配置信息"
)
async def get_config():
    """获取监听服务配置信息"""
    return APIResponse(
        success=True,
        message="",
        data={
            "safe_contacts": list(SAFE_CONTACTS),
            "sandbox_mode": SANDBOX_MODE,
            "description": "安全白名单用于防止误发消息给其他联系人，沙箱模式提供额外安全保护"
        }
    )


@router.websocket("/ws")
async def websocket_listen(
    websocket: WebSocket,
    who: str = Query(..., description="要监听的联系人名称"),
    auto_start: bool = Query(True, description="是否自动启动监听")
):
    """WebSocket监听端点

    连接后可以实时接收来自指定联系人的消息

    Args:
        websocket: WebSocket连接
        who: 要监听的联系人名称
        auto_start: 是否自动启动监听

    消息格式:
        {
            "type": "message" | "status" | "error",
            "data": {
                "who": "联系人名称",
                "content": "消息内容",
                "msg_type": "消息类型",
                "time": "时间戳",
                ...
            }
        }
    """
    # 生成客户端ID
    client_id = str(uuid.uuid4())
    service = ListenService()

    # 检查联系人是否安全
    is_safe = who in SAFE_CONTACTS

    try:
        # 接受连接
        await manager.connect(websocket, client_id)

        # 发送连接确认消息
        await websocket.send_json({
            "type": "status",
            "data": {
                "status": "connected",
                "client_id": client_id,
                "who": who,
                "is_safe": is_safe,
                "sandbox_mode": SANDBOX_MODE
            }
        })

        # 如果配置了安全白名单且不在其中，发送警告
        if SAFE_CONTACTS and not is_safe:
            await websocket.send_json({
                "type": "warning",
                "data": {
                    "message": f"警告: 联系人 '{who}' 不在安全白名单中",
                    "safe_contacts": list(SAFE_CONTACTS),
                    "sandbox_mode": SANDBOX_MODE
                }
            })

            # 如果是沙箱模式，拒绝连接
            if SANDBOX_MODE:
                await websocket.send_json({
                    "type": "error",
                    "data": {
                        "message": "沙箱模式: 拒绝监听非安全白名单中的联系人"
                    }
                })
                await websocket.close()
                return

        # 自动启动监听
        listen_started = False
        if auto_start:
            result = service.start_listen(who=who)
            listen_started = result.success
            manager.add_listener(client_id, who)

            await websocket.send_json({
                "type": "status",
                "data": {
                    "status": "listening" if listen_started else "listen_failed",
                    "who": who,
                    "message": result.message
                }
            })

        # 监听客户端消息
        while True:
            try:
                # 接收客户端消息（可用于控制命令）
                data = await websocket.receive_text()
                message = json.loads(data)

                # 处理控制命令
                if message.get("type") == "command":
                    command = message.get("command")

                    if command == "start_listen":
                        target_who = message.get("who", who)
                        result = service.start_listen(who=target_who)
                        manager.add_listener(client_id, target_who)
                        await websocket.send_json({
                            "type": "status",
                            "data": {
                                "status": "listening" if result.success else "failed",
                                "who": target_who,
                                "message": result.message
                            }
                        })

                    elif command == "stop_listen":
                        target_who = message.get("who", who)
                        result = service.stop_listen(who=target_who)
                        manager.remove_listener(client_id, target_who)
                        await websocket.send_json({
                            "type": "status",
                            "data": {
                                "status": "stopped",
                                "who": target_who,
                                "message": result.message
                            }
                        })

                    elif command == "get_status":
                        status = service.get_listen_status(who=message.get("who"))
                        await websocket.send_json({
                            "type": "status",
                            "data": status.data
                        })

                    elif command == "ping":
                        await websocket.send_json({
                            "type": "pong",
                            "data": {"timestamp": message.get("timestamp")}
                        })

            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "data": {"message": "无效的JSON格式"}
                })
            except Exception as e:
                await websocket.send_json({
                    "type": "error",
                    "data": {"message": f"处理消息时出错: {str(e)}"}
                })

    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "data": {"message": f"连接错误: {str(e)}"}
        })

    finally:
        # 清理连接
        manager.disconnect(client_id)
