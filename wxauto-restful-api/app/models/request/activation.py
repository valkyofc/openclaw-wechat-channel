from pydantic import BaseModel

# 激活许可证请求
class ActivateLicenseRequest(BaseModel):
    """激活wxautox4许可证请求"""
    license_key: str

# 检查激活状态请求
class CheckActivationRequest(BaseModel):
    """检查激活状态请求"""
    pass
