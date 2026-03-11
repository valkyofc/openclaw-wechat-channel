from pydantic import BaseModel, Field
from typing import Optional, List, Union

# 基础请求
class BaseRequest(BaseModel):
    wxname: Union[None, str] = ''

# 启动监听请求
class StartListenRequest(BaseRequest):
    """启动监听请求"""
    who: str = Field(..., description="监听的联系人名称", examples=["文件传输助手"])

    # 安全白名单
    SAFE_CONTACTS: List[str] = ["文件传输助手"]

    def is_safe_contact(self) -> bool:
        """检查联系人是否在安全白名单中"""
        return self.who in self.SAFE_CONTACTS

# 停止监听请求
class StopListenRequest(BaseRequest):
    """停止监听请求"""
    who: str = Field(..., description="停止监听的联系人名称", examples=["文件传输助手"])

# 获取监听状态请求
class GetListenStatusRequest(BaseRequest):
    """获取监听状态请求"""
    who: Optional[str] = Field(None, description="指定联系人名称，不指定则返回所有")

# 批量启动监听请求
class BatchStartListenRequest(BaseRequest):
    """批量启动监听请求"""
    contacts: List[str] = Field(..., description="监听的联系人名称列表")

    # 安全白名单
    SAFE_CONTACTS: List[str] = ["文件传输助手"]

    def get_safe_contacts(self) -> List[str]:
        """获取在安全白名单中的联系人"""
        return [c for c in self.contacts if c in self.SAFE_CONTACTS]

    def get_unsafe_contacts(self) -> List[str]:
        """获取不在安全白名单中的联系人"""
        return [c for c in self.contacts if c not in self.SAFE_CONTACTS]
