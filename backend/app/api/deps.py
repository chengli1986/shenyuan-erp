"""
API依赖模块
"""

from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.security import verify_token, SecurityException
from app.models.user import User, UserRole


# JWT Token认证
security = HTTPBearer()


def get_db() -> Generator:
    """获取数据库会话"""
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_current_user(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """获取当前用户"""
    token = credentials.credentials
    user_id = verify_token(token)
    if user_id is None:
        raise SecurityException("无效的访问令牌")
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise SecurityException("用户不存在")
    
    if not user.is_active:
        raise SecurityException("用户已被禁用")
    
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """获取当前活跃用户"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户已被禁用"
        )
    return current_user


def get_current_superuser(
    current_user: User = Depends(get_current_user)
) -> User:
    """获取当前超级用户"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="权限不足"
        )
    return current_user


def require_permission(permission: str):
    """权限验证装饰器"""
    def permission_checker(current_user: User = Depends(get_current_user)) -> User:
        if not current_user.has_permission(permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"缺少权限: {permission}"
            )
        return current_user
    return permission_checker


def require_role(*roles: UserRole):
    """角色验证装饰器"""
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"角色权限不足，需要: {[role.value for role in roles]}"
            )
        return current_user
    return role_checker


# 临时测试用的模拟用户（用于开发阶段）
def get_mock_user(role: UserRole = UserRole.ADMIN) -> User:
    """获取模拟用户 - 仅用于测试"""
    user = User(
        id=1,
        username="admin",
        email="admin@example.com",
        name="系统管理员",
        role=role,
        is_active=True,
        is_superuser=True
    )
    return user