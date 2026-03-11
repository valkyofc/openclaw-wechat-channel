from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, Form, Depends
from app.models.response import APIResponse
from app.models.file import FileInfo, FileUploadResponse
from app.services.file_service import FileService
from app.utils.auth import get_current_token
from app.utils.response_builder import success, error, list_response, single_object, operation_result
from app.models.base import QueryParams

router = APIRouter()
file_service = FileService()

@router.post(
    "/upload",
    response_model=APIResponse,
    summary="上传文件"
)
async def upload_file(
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
    uploader: Optional[str] = Form(None),
    token: str = Depends(get_current_token)
) -> APIResponse:
    """上传文件

    Args:
        file: 上传的文件
        description: 文件描述
        uploader: 上传者
        token: 认证令牌

    Returns:
        APIResponse: 包含文件上传结果
    """
    result = await file_service.upload_file(file, description, uploader)

    # 转换为标准格式
    file_data = {
        "file_id": result.file_id,
        "filename": result.filename,
        "file_type": result.file_type,
        "file_size": result.file_size,
        "file_hash": result.file_hash,
        "file_path": result.file_path,
        "upload_time": result.upload_time.isoformat(),
        "is_new": result.is_new
    }

    return single_object(
        obj=file_data,
        message="文件上传成功" if result.is_new else "文件已存在"
    )

@router.get(
    "/{file_id}",
    response_model=APIResponse,
    summary="获取文件信息"
)
async def get_file(
    file_id: str,
    token: str = Depends(get_current_token)
) -> APIResponse:
    """获取文件信息

    Args:
        file_id: 文件ID
        token: 认证令牌

    Returns:
        APIResponse: 包含文件信息
    """
    file_info = file_service.get_file(file_id)
    if not file_info:
        return error(message="文件不存在", error_code="FILE_NOT_FOUND")

    return single_object(
        obj=file_info.dict(),
        message=""
    )

@router.delete(
    "/{file_id}",
    response_model=APIResponse,
    summary="删除文件"
)
async def delete_file(
    file_id: str,
    token: str = Depends(get_current_token)
) -> APIResponse:
    """删除文件

    Args:
        file_id: 文件ID
        token: 认证令牌

    Returns:
        APIResponse: 删除结果
    """
    if file_service.delete_file(file_id):
        return operation_result(
            affected=1,
            message="文件删除成功"
        )

    return error(message="文件不存在", error_code="FILE_NOT_FOUND")

@router.get(
    "/",
    response_model=APIResponse,
    summary="获取文件列表"
)
async def list_files(
    skip: int = 0,
    limit: int = 100,
    token: str = Depends(get_current_token)
) -> APIResponse:
    """列出文件

    Args:
        skip: 跳过数量
        limit: 限制数量
        token: 认证令牌

    Returns:
        APIResponse: 包含文件列表和总数
    """
    total, files = file_service.list_files(skip, limit)

    # 转换为字典列表
    items = [file.dict() for file in files]

    return list_response(
        items=items,
        total=total,
        message=""
    ) 