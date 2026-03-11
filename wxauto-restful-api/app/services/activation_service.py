"""Activation Service for wxautox4 License Management"""
from app.models.response import APIResponse
from app.utils.error_handler import handle_service_error


class ActivationService:
    """wxautox4激活服务类"""

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ActivationService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """初始化激活服务"""
        if not self._initialized:
            self._initialized = True
            print("[ActivationService] 激活服务已初始化", flush=True)

    @handle_service_error(custom_message="激活许可证失败")
    def activate_license(
            self,
            license_key: str
    ) -> APIResponse:
        """激活wxautox4许可证

        Args:
            license_key: 许可证密钥

        Returns:
            APIResponse: 激活结果
        """
        from wxautox4.utils.useful import authenticate
        result = authenticate(license_key)
        if result:
            return APIResponse(
                success=True,
                message='激活成功!',
                data={
                    'activated': True,
                    'license_key': license_key
                }
            )
        else:
            return APIResponse(
                success=False,
                message='激活失败，请检查许可证密钥是否正确',
                data={
                    'activated': False,
                    'license_key': license_key
                }
            )

    @handle_service_error(custom_message="检查激活状态失败")
    def check_activation(self) -> APIResponse:
        """检查wxautox4激活状态

        Returns:
            APIResponse: 激活状态
        """
        from wxautox4.utils.useful import check_license
        is_activated = check_license()
        if is_activated:
            return APIResponse(
                success=True,
                message='已激活',
                data={
                    'activated': True,
                    'status': 'activated'
                }
            )
        else:
            return APIResponse(
                success=True,
                message='未激活',
                data={
                    'activated': False,
                    'status': 'not_activated',
                    'solution': '请使用激活接口激活许可证'
                }
            )
