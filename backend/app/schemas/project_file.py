# backend/app/schemas/project_file.py
"""
项目文件数据格式定义
定义文件上传、下载的API数据格式
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.project_file import FileType


class ProjectFileBase(BaseModel):
    """文件基础信息"""
    file_type: FileType = Field(..., description="文件类型")
    description: Optional[str] = Field(None, description="文件描述")


class ProjectFileUpload(ProjectFileBase):
    """文件上传数据格式"""
    pass


class ProjectFileResponse(BaseModel):
    """文件信息响应格式"""
    id: int
    project_id: int
    file_name: str
    file_type: FileType
    file_size: int
    file_extension: str
    mime_type: Optional[str]
    description: Optional[str]
    uploaded_by: str
    upload_time: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


class ProjectFileListResponse(BaseModel):
    """文件列表响应格式"""
    items: List[ProjectFileResponse]
    total: int
    
    class Config:
        from_attributes = True


class FileUploadResult(BaseModel):
    """文件上传结果"""
    success: bool
    message: str
    file_id: Optional[int] = None
    file_info: Optional[ProjectFileResponse] = None


# 文件类型配置
FILE_TYPE_CONFIG = {
    FileType.AWARD_NOTICE: {
        "name": "中标通知书",
        "icon": "📋",
        "color": "blue",
        "max_count": 1,  # 最多只能有1个
        "description": "项目中标通知书文件"
    },
    FileType.CONTRACT: {
        "name": "合同文件", 
        "icon": "📄",
        "color": "green",
        "max_count": 10,  # 最多10个合同文件
        "description": "项目合同相关文件"
    },
    FileType.ATTACHMENT: {
        "name": "附件",
        "icon": "📎", 
        "color": "orange",
        "max_count": 20,  # 最多20个附件
        "description": "项目相关附件"
    },
    FileType.OTHER: {
        "name": "其他文件",
        "icon": "📁",
        "color": "gray", 
        "max_count": 50,  # 最多50个其他文件
        "description": "其他项目相关文件"
    }
}

# 支持的文件格式
ALLOWED_FILE_EXTENSIONS = {
    # 文档格式
    '.pdf': 'application/pdf',
    '.doc': 'application/msword', 
    '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    '.xls': 'application/vnd.ms-excel',
    '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    '.ppt': 'application/vnd.ms-powerpoint',
    '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    
    # 图片格式
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg', 
    '.png': 'image/png',
    '.gif': 'image/gif',
    '.bmp': 'image/bmp',
    
    # 文本格式
    '.txt': 'text/plain',
    '.rtf': 'application/rtf',
    
    # 压缩格式
    '.zip': 'application/zip',
    '.rar': 'application/x-rar-compressed',
    '.7z': 'application/x-7z-compressed'
}

# 文件大小限制 (字节)
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB