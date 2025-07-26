# backend/app/models/project_file.py
"""
项目文件数据模型
管理项目相关的文档文件
"""

from sqlalchemy import Column, Integer, String, DateTime, BigInteger, ForeignKey, Enum, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class FileType(str, enum.Enum):
    """文件类型枚举"""
    AWARD_NOTICE = "award_notice"     # 中标通知书
    CONTRACT = "contract"             # 合同文件
    ATTACHMENT = "attachment"         # 附件
    OTHER = "other"                   # 其他


class ProjectFile(Base):
    """
    项目文件表模型
    存储项目相关的所有文档文件信息
    """
    __tablename__ = "project_files"
    
    # 主键ID
    id = Column(Integer, primary_key=True, index=True, comment="文件ID")
    
    # 关联项目
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, comment="关联项目ID")
    
    # 文件基本信息
    file_name = Column(String(255), nullable=False, comment="原始文件名")
    file_type = Column(Enum(FileType), nullable=False, comment="文件类型")
    file_size = Column(BigInteger, nullable=False, comment="文件大小(字节)")
    file_extension = Column(String(10), nullable=False, comment="文件扩展名")
    mime_type = Column(String(100), comment="MIME类型")
    
    # 存储信息
    stored_filename = Column(String(255), nullable=False, comment="存储的文件名(UUID)")
    file_path = Column(String(500), nullable=False, comment="文件存储路径")
    
    # 文件描述
    description = Column(Text, comment="文件描述")
    
    # 上传信息
    uploaded_by = Column(String(100), nullable=False, comment="上传人")
    upload_time = Column(DateTime(timezone=True), server_default=func.now(), comment="上传时间")
    
    # 系统字段
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="更新时间")
    
    # 关系映射
    project = relationship("Project", backref="files")
    
    def __repr__(self):
        return f"<ProjectFile(id={self.id}, name='{self.file_name}', type='{self.file_type}')>"
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "project_id": self.project_id,
            "file_name": self.file_name,
            "file_type": self.file_type.value if self.file_type else None,
            "file_size": self.file_size,
            "file_extension": self.file_extension,
            "mime_type": self.mime_type,
            "description": self.description,
            "uploaded_by": self.uploaded_by,
            "upload_time": self.upload_time.isoformat() if self.upload_time else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
    
    @property
    def file_size_formatted(self):
        """格式化文件大小显示"""
        size = self.file_size
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        elif size < 1024 * 1024 * 1024:
            return f"{size / (1024 * 1024):.1f} MB"
        else:
            return f"{size / (1024 * 1024 * 1024):.1f} GB"