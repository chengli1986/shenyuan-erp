"""
权限管理相关模型
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from app.core.database import Base


class RolePermission(Base):
    """角色权限配置表"""
    __tablename__ = "role_permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    role = Column(String(50), nullable=False)  # 角色名称
    permission_code = Column(String(100), nullable=False)  # 权限代码
    permission_name = Column(String(100), nullable=False)  # 权限名称
    description = Column(Text)  # 权限描述
    is_active = Column(Boolean, default=True)  # 是否启用
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    class Config:
        table = True
    
    def __repr__(self):
        return f"<RolePermission(role='{self.role}', permission='{self.permission_code}')>"


class PermissionCategory(Base):
    """权限分类表"""
    __tablename__ = "permission_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    category_name = Column(String(50), unique=True, nullable=False)  # 分类名称
    category_code = Column(String(50), unique=True, nullable=False)  # 分类代码
    description = Column(Text)  # 描述
    sort_order = Column(Integer, default=0)  # 排序
    is_active = Column(Boolean, default=True)
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    def __repr__(self):
        return f"<PermissionCategory(name='{self.category_name}', code='{self.category_code}')>"