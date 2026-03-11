"""错误处理装饰器和服务"""
import functools
import traceback
import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Callable, Any, Optional
from app.models.response import APIResponse
from app.utils.config import settings


class ErrorTracker:
    """错误追踪器，专门记录详细的错误信息"""

    def __init__(self):
        self.error_log_dir = Path("logs/errors")
        self.error_log_dir.mkdir(parents=True, exist_ok=True)

        # 创建专门的错误日志记录器
        self.logger = logging.getLogger("error_tracker")
        self.logger.setLevel(logging.ERROR)

        # 文件处理器 - 记录详细错误到文件
        error_file_handler = logging.FileHandler(
            self.error_log_dir / f"errors_{datetime.now().strftime('%Y%m%d')}.log",
            encoding='utf-8'
        )
        error_file_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s\n%(message)s\n')
        )
        self.logger.addHandler(error_file_handler)

        # 控制台处理器 - 开发时查看
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s\n%(message)s\n')
        )
        self.logger.addHandler(console_handler)

    def format_error(self, func_name: str, error: Exception, extra_info: dict = None) -> str:
        """格式化错误信息为漂亮的格式"""
        separator = "=" * 80

        error_info = {
            "时间": datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
            "方法": func_name,
            "错误类型": type(error).__name__,
            "错误信息": str(error),
            "额外信息": extra_info or {}
        }

        formatted = f"""
{separator}
🔴 错误详情
{separator}
{'📅 时间:':<12} {error_info['时间']}
{'🔧 方法:':<12} {error_info['方法']}
{'❌ 错误类型:':<12} {error_info['错误类型']}
{'💬 错误信息:':<12} {error_info['错误信息']}
"""

        if extra_info:
            formatted += f"{'📋 额外信息:':<12} {json.dumps(extra_info, ensure_ascii=False, indent=2)}\n"

        formatted += f"""
{separator}
📚 完整堆栈追踪:
{separator}
{traceback.format_exc()}
{separator}
"""
        return formatted

    def track_error(self, func_name: str, error: Exception, extra_info: dict = None):
        """记录错误到日志文件"""
        formatted_error = self.format_error(func_name, error, extra_info)
        self.logger.error(formatted_error)

        # 同时保存为独立的 JSON 文件，方便程序化分析
        self._save_error_json(func_name, error, extra_info)

    def _save_error_json(self, func_name: str, error: Exception, extra_info: dict = None):
        """保存错误信息为 JSON 格式"""
        error_data = {
            "timestamp": datetime.now().isoformat(),
            "function": func_name,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc(),
            "extra_info": extra_info or {}
        }

        # 按日期和错误类型保存
        timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        filename = f"{type(error).__name__}_{timestamp_str}.json"
        json_path = self.error_log_dir / filename

        try:
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(error_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"保存错误 JSON 文件失败: {e}")


# 全局错误追踪器实例
error_tracker = ErrorTracker()


def handle_service_error(
    return_error_message: bool = True,
    include_error_type: bool = False,
    custom_message: str = None
):
    """服务层错误处理装饰器

    Args:
        return_error_message: 是否在返回中包含错误信息
        include_error_type: 是否包含错误类型名称
        custom_message: 自定义的错误消息前缀

    Returns:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                # 检查是否是预期的业务异常（不需要记录为错误）
                from app.services.wechat_service import WeChatNotInitializedError

                if isinstance(e, WeChatNotInitializedError):
                    # 这是一个预期的异常，不记录为错误，直接返回友好的错误信息
                    return APIResponse(
                        success=False,
                        message=str(e),
                        data={"error": "NOT_ACTIVATED", "solution": "请先激活 wxautox4"}
                    )

                # 记录详细的错误信息
                extra_info = {
                    "args": str(args)[:200],  # 限制参数长度
                    "kwargs": str(kwargs)[:200],
                    "function_module": func.__module__,
                    "function_name": func.__name__
                }
                error_tracker.track_error(func.__name__, e, extra_info)

                # 返回用户友好的错误信息
                if return_error_message:
                    error_msg = str(e)
                    if include_error_type:
                        error_msg = f"[{type(e).__name__}] {error_msg}"
                    if custom_message:
                        error_msg = f"{custom_message}: {error_msg}"

                    return APIResponse(success=False, message=error_msg)
                else:
                    return APIResponse(success=False, message="操作失败，请稍后重试")

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # 检查是否是预期的业务异常（不需要记录为错误）
                from app.services.wechat_service import WeChatNotInitializedError

                if isinstance(e, WeChatNotInitializedError):
                    # 这是一个预期的异常，不记录为错误，直接返回友好的错误信息
                    return APIResponse(
                        success=False,
                        message=str(e),
                        data={"error": "NOT_ACTIVATED", "solution": "请先激活 wxautox4"}
                    )

                # 记录详细的错误信息
                extra_info = {
                    "args": str(args)[:200],
                    "kwargs": str(kwargs)[:200],
                    "function_module": func.__module__,
                    "function_name": func.__name__
                }
                error_tracker.track_error(func.__name__, e, extra_info)

                # 返回用户友好的错误信息
                if return_error_message:
                    error_msg = str(e)
                    if include_error_type:
                        error_msg = f"[{type(e).__name__}] {error_msg}"
                    if custom_message:
                        error_msg = f"{custom_message}: {error_msg}"

                    return APIResponse(success=False, message=error_msg)
                else:
                    return APIResponse(success=False, message="操作失败，请稍后重试")

        # 根据函数类型返回对应的包装器
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


# 导入 asyncio 以支持异步检测
import asyncio


def track_manual_error(func_name: str, error: Exception, extra_info: dict = None):
    """手动追踪错误的便捷函数

    Args:
        func_name: 发生错误的函数名
        error: 异常对象
        extra_info: 额外信息
    """
    error_tracker.track_error(func_name, error, extra_info)


def get_recent_errors(limit: int = 10) -> list:
    """获取最近的错误列表

    Args:
        limit: 返回的错误数量

    Returns:
        错误文件列表
    """
    error_files = sorted(
        error_tracker.error_log_dir.glob("*.json"),
        key=lambda x: x.stat().st_mtime,
        reverse=True
    )
    return error_files[:limit]
