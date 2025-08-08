"""
API依赖模块
"""

from fastapi import HTTPException, status
from app.models.user import User, UserRole


def get_current_user():
    """获取当前用户 - 临时模拟实现"""
    # TODO: 实现真正的用户认证
    # 创建模拟的User对象用于测试
    user = User(
        id=1,
        username="admin",
        email="admin@example.com",
        name="系统管理员",
        role=UserRole.ADMIN,
        is_active=True,
        is_superuser=True
    )
    return user