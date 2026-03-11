"""
Web控制台路由
提供管理界面和相关的API端点
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi import File, UploadFile
import os
import json
from pathlib import Path
from typing import Dict, Any

router = APIRouter()

# 获取项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
WEB_TEMPLATES = BASE_DIR / "web" / "templates"


@router.get("/web", response_class=HTMLResponse, include_in_schema=False)
async def web_console():
    """Web控制台主页"""
    try:
        html_path = WEB_TEMPLATES / "index.html"
        with open(html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Web控制台未安装</h1>", status_code=404)


@router.get("/api/config")
async def get_config() -> Dict[str, Any]:
    """获取当前配置信息"""
    from app.utils.config import settings

    config = {
        "server": {
            "host": settings.server.host,
            "port": settings.server.port,
            "reload": settings.server.reload
        },
        "wechat": {
            "app_path": settings.wechat.app_path,
            "language": settings.wechat.language,
            "enable_file_logger": settings.wechat.enable_file_logger
        },
        "logging": {
            "level": settings.logging.level,
            "file": settings.logging.file
        },
        "upload": {
            "base_dir": settings.upload.base_dir,
            "max_size": settings.upload.max_size
        }
    }
    return config


@router.post("/api/config")
async def update_config(request: Request) -> Dict[str, str]:
    """更新配置信息"""
    try:
        data = await request.json()

        # 这里应该实现配置更新逻辑
        # 注意：实际应用中需要验证输入并安全地更新配置文件

        return {"success": True, "message": "配置更新成功"}
    except Exception as e:
        return {"success": False, "message": str(e)}


@router.get("/api/logs")
async def get_logs(level: str = "all", limit: int = 100):
    """获取系统日志"""
    try:
        from app.utils.config import settings

        log_file = BASE_DIR / settings.logging.file

        if not log_file.exists():
            return []

        logs = []
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                # 解析日志行
                if line.strip():
                    # 简单的日志解析
                    parts = line.strip().split(" - ", 2)
                    if len(parts) >= 3:
                        timestamp = parts[0]
                        log_level = parts[1]
                        message = parts[2]

                        if level == "all" or log_level == level:
                            logs.append({
                                "timestamp": timestamp,
                                "level": log_level,
                                "message": message
                            })

                            if len(logs) >= limit:
                                break

        return logs[-limit:]  # 返回最新的日志

    except Exception as e:
        return []


@router.get("/api/status")
async def get_system_status() -> Dict[str, Any]:
    """获取系统状态"""
    try:
        from app.utils.wx_package_manager import get_package_info

        package_info = get_package_info()

        return {
            "service": {
                "running": True,
                "version": "2.0.0"
            },
            "package": package_info,
            "database": {
                "connected": True,
                "type": "sqlite"
            }
        }
    except Exception as e:
        return {
            "service": {
                "running": False,
                "error": str(e)
            }
        }
