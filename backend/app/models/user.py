"""
用户模型
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class UserRole(str, enum.Enum):
    """用户角色枚举"""
    ADMIN = "admin"                    # 管理员
    GENERAL_MANAGER = "general_manager"  # 总经理
    DEPT_MANAGER = "dept_manager"      # 部门主管/项目主管
    PROJECT_MANAGER = "project_manager"  # 项目经理
    PURCHASER = "purchaser"            # 采购员
    WAREHOUSE_KEEPER = "warehouse_keeper"  # 仓库管理员
    FINANCE = "finance"                # 财务
    WORKER = "worker"                  # 施工队长


class User(Base):
    """用户表"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True)
    password_hash = Column(String(128), nullable=False)
    
    # 用户信息
    name = Column(String(50), nullable=False)  # 真实姓名
    role = Column(Enum(UserRole), nullable=False)
    department = Column(String(50))  # 部门
    phone = Column(String(20))  # 电话
    
    # 状态
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    last_login = Column(DateTime)
    
    def has_permission(self, permission: str) -> bool:
        """检查用户是否有特定权限"""
        # 管理员有所有权限
        if self.is_superuser or self.role == UserRole.ADMIN:
            return True
        
        # 基于角色的权限控制
        permissions = {
            UserRole.GENERAL_MANAGER: [
                "view_all", "approve_final", "view_price", "manage_users"
            ],
            UserRole.DEPT_MANAGER: [
                "view_department", "approve_dept", "view_price", "manage_suppliers"
            ],
            UserRole.PROJECT_MANAGER: [
                "create_purchase", "view_own_purchase", "manage_project"
            ],
            UserRole.PURCHASER: [
                "quote_price", "manage_suppliers", "view_price"
            ],
            UserRole.WAREHOUSE_KEEPER: [
                "manage_inventory", "inbound", "outbound"
            ],
            UserRole.FINANCE: [
                "view_finance", "view_price", "financial_report"
            ],
            UserRole.WORKER: [
                "view_inventory", "request_material"
            ]
        }
        
        user_permissions = permissions.get(self.role, [])
        return permission in user_permissions
    
    def can_view_price(self) -> bool:
        """是否可以查看价格信息"""
        return self.role in [
            UserRole.ADMIN,
            UserRole.GENERAL_MANAGER,
            UserRole.DEPT_MANAGER,
            UserRole.PURCHASER,
            UserRole.FINANCE
        ]
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"