from fastapi import APIRouter
from app.models.response import APIResponse
from app.utils.wx_package_manager import get_supported_features
from app.utils.config import settings

router = APIRouter()


@router.get(
    "/package",
    operation_id="[info]获取包信息",
    response_model=APIResponse,
    summary="获取当前使用的包信息"
)
async def get_package_info():
    """获取当前使用的包信息"""
    package_info = {
        "package": "wxautox4",
        "version": "Plus版",
        "description": "wxautox4 Plus版，功能丰富"
    }

    return APIResponse(
        success=True,
        message="获取包信息成功",
        data=package_info
    ) 