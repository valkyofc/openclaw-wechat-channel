"""
标准数据结构定义

定义 API 返回值中 data 字段的标准结构
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ListItem(BaseModel):
    """列表项的标准结构"""
    id: str = Field(..., description="唯一标识")
    name: str = Field(..., description="名称")
    type: Optional[str] = Field(None, description="类型")
    data: Optional[Dict[str, Any]] = Field(None, description="额外数据")


class ListData(BaseModel):
    """列表数据的标准结构"""
    total: int = Field(..., description="总数")
    items: List[Dict[str, Any]] = Field(..., description="数据列表")


class SingleObjectData(BaseModel):
    """单个对象的标准结构"""
    item: Dict[str, Any] = Field(..., description="对象数据")


class MessageData(BaseModel):
    """消息数据的标准结构"""
    chat_info: Dict[str, Any] = Field(..., description="聊天信息")
    messages: List[Dict[str, Any]] = Field(..., description="消息列表")


class OperationResultData(BaseModel):
    """操作结果的标准结构"""
    affected: int = Field(..., description="影响的数量")
    result: Optional[Dict[str, Any]] = Field(None, description="额外结果信息")


class SubWindowItem(BaseModel):
    """子窗口项的标准结构"""
    name: str = Field(..., alias="who", description="联系人名称")
    type: str = Field(..., alias="chat_type", description="聊天类型")


class SessionItem(BaseModel):
    """会话项的标准结构"""
    who: str = Field(..., description="联系人名称")
    msg_count: int = Field(0, description="消息数量")
    last_message: Optional[str] = Field(None, description="最后一条消息")
    data: Optional[Dict[str, Any]] = Field(None, description="额外数据")


class ContactItem(BaseModel):
    """联系人项的标准结构"""
    name: str = Field(..., description="名称")
    nickname: Optional[str] = Field(None, description="昵称")
    remark: Optional[str] = Field(None, description="备注")
    type: str = Field(..., description="类型：friend/group")
    data: Optional[Dict[str, Any]] = Field(None, description="额外数据")


class OnlineStatusData(BaseModel):
    """在线状态的标准结构"""
    status: str = Field(..., description="online/offline")
    online: bool = Field(..., description="是否在线")
