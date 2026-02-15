"""
API依赖模块
"""

from typing import Generator, Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.security import verify_token, SecurityException
from app.models.user import User, UserRole


# JWT Token认证（Authorization header方式，设为可选）
security = HTTPBearer(auto_error=False)

# Cookie名称（与auth.py保持一致）
COOKIE_NAME = "access_token"


def get_db() -> Generator:
    """获取数据库会话"""
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> User:
    """获取当前用户 - 优先从HttpOnly Cookie读取token，兼容Authorization header"""
    token = None

    # 优先从HttpOnly Cookie获取token
    cookie_token = request.cookies.get(COOKIE_NAME)
    if cookie_token:
        token = cookie_token

    # 兼容：如果cookie中没有，从Authorization header获取
    if not token and credentials:
        token = credentials.credentials

    if not token:
        raise SecurityException("未提供访问令牌")

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
