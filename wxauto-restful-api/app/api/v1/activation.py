from fastapi import APIRouter, Depends
from app.services.activation_service import ActivationService
from app.models.request.activation import ActivateLicenseRequest
from app.models.response import APIResponse

router = APIRouter()

@router.post(
    "/activate",
    operation_id="[activation]激活许可证",
    response_model=APIResponse,
    summary='✨激活wxautox4许可证'
)
async def activate_license(
    request: ActivateLicenseRequest,
    service: ActivationService = Depends()
):
    """激活wxautox4许可证

    使用许可证密钥激活wxautox4，激活后才能使用微信自动化功能。

    - **license_key**: 许可证密钥

    无需认证即可调用此接口。
    """
    return service.activate_license(license_key=request.license_key)

@router.get(
    "/check",
    operation_id="[activation]检查激活状态",
    response_model=APIResponse,
    summary='✨检查wxautox4激活状态'
)
async def check_activation(
    service: ActivationService = Depends()
):
    """检查wxautox4激活状态

    返回当前wxautox4的激活状态。

    无需认证即可调用此接口。
    """
    return service.check_activation()
