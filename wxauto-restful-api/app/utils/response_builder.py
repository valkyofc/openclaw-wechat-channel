"""
统一响应格式构建工具

提供标准化的响应构建函数，确保所有接口返回格式一致
"""

from typing import Any, Optional, List, Dict
from app.models.response import APIResponse


class ResponseBuilder:
    """响应构建器 - 统一处理各种响应格式"""

    @staticmethod
    def success(
        message: str = "操作成功",
        data: Any = None
    ) -> APIResponse:
        """
        构建成功响应

        Args:
            message: 成功消息
            data: 返回数据

        Returns:
            APIResponse
        """
        return APIResponse(success=True, message=message, data=data)

    @staticmethod
    def error(
        message: str = "操作失败",
        error_code: Optional[str] = None,
        solution: Optional[str] = None
    ) -> APIResponse:
        """
        构建失败响应

        Args:
            message: 错误消息
            error_code: 错误代码
            solution: 解决方案

        Returns:
            APIResponse
        """
        data = None
        if error_code or solution:
            data = {}
            if error_code:
                data["error_code"] = error_code
            if solution:
                data["solution"] = solution

        return APIResponse(success=False, message=message, data=data)

    @staticmethod
    def list_response(
        items: List[Any],
        total: Optional[int] = None,
        message: str = ""
    ) -> APIResponse:
        """
        构建列表数据响应（统一格式）

        Args:
            items: 列表数据
            total: 总数（如果为 None，则使用 len(items)）
            message: 提示消息

        Returns:
            APIResponse with data: {"total": int, "items": list}
        """
        if total is None:
            total = len(items)

        return APIResponse(
            success=True,
            message=message,
            data={
                "total": total,
                "items": items
            }
        )

    @staticmethod
    def single_object(
        obj: Any,
        message: str = ""
    ) -> APIResponse:
        """
        构建单个对象响应（统一格式）

        Args:
            obj: 对象数据
            message: 提示消息

        Returns:
            APIResponse with data: {"item": obj}
        """
        return APIResponse(
            success=True,
            message=message,
            data={
                "item": obj
            }
        )

    @staticmethod
    def operation_result(
        affected: int,
        message: str = "操作成功",
        extra_data: Optional[Dict] = None
    ) -> APIResponse:
        """
        构建操作结果响应（统一格式）

        Args:
            affected: 影响的行数/对象数
            message: 提示消息
            extra_data: 额外的结果信息

        Returns:
            APIResponse with data: {"affected": int, "result": dict}
        """
        data = {"affected": affected}
        if extra_data:
            data["result"] = extra_data

        return APIResponse(
            success=True,
            message=message,
            data=data
        )

    @staticmethod
    def message_data(
        messages: List[Any],
        chat_info: Dict,
        message: str = ""
    ) -> APIResponse:
        """
        构建消息数据响应（统一格式）

        Args:
            messages: 消息列表
            chat_info: 聊天信息
            message: 提示消息

        Returns:
            APIResponse with data: {"chat_info": dict, "messages": list}
        """
        return APIResponse(
            success=True,
            message=message,
            data={
                "chat_info": chat_info,
                "messages": messages
            }
        )

    @staticmethod
    def wechat_not_ready() -> APIResponse:
        """
        微信实例未就绪的标准错误响应

        Returns:
            APIResponse
        """
        return ResponseBuilder.error(
            message="wxautox4未激活，无法使用微信功能",
            error_code="NOT_ACTIVATED",
            solution="请先运行: wxautox4 -a your-activation-code"
        )

    @staticmethod
    def wechat_not_initialized() -> APIResponse:
        """
        微信实例未初始化的标准错误响应

        Returns:
            APIResponse
        """
        return ResponseBuilder.error(
            message="微信实例未就绪。请先调用 /api/v1/wechat/initialize 接口获取实例。",
            error_code="NOT_INITIALIZED",
            solution="确保微信已登录，如提示未激活请运行: wxautox4 -a your-activation-code"
        )


# 便捷函数别名
success = ResponseBuilder.success
error = ResponseBuilder.error
list_response = ResponseBuilder.list_response
single_object = ResponseBuilder.single_object
operation_result = ResponseBuilder.operation_result
message_data = ResponseBuilder.message_data
wechat_not_ready = ResponseBuilder.wechat_not_ready
wechat_not_initialized = ResponseBuilder.wechat_not_initialized
