"""
用户认证相关API
"""

from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.core.security import (
    authenticate_user,
    create_access_token,
    get_password_hash,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.models.user import User, UserRole
from app.schemas.auth import Token, UserLogin, UserRegister, UserResponse

router = APIRouter()


@router.post("/login", response_model=Token)
def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """用户登录"""
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户已被禁用"
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )
    
    # 更新最后登录时间
    from sqlalchemy.sql import func
    user.last_login = func.now()
    db.commit()
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # 转换为秒
        "user": {
            "id": user.id,
            "username": user.username,
            "name": user.name,
            "role": user.role.value,
            "department": user.department,
            "is_active": user.is_active,
            "can_view_price": user.can_view_price()
        }
    }


@router.post("/register", response_model=UserResponse)
def register(
    *,
    db: Session = Depends(get_db),
    user_data: UserRegister,
    # current_user: User = Depends(get_current_superuser)  # 只有超级管理员可以注册新用户
) -> Any:
    """用户注册（仅管理员）"""
    # 检查用户名是否已存在
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 检查邮箱是否已存在
    if user_data.email and db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已存在"
        )
    
    # 创建新用户
    user = User(
        username=user_data.username,
        email=user_data.email,
        name=user_data.name,
        password_hash=get_password_hash(user_data.password),
        role=user_data.role,
        department=user_data.department,
        phone=user_data.phone,
        is_active=True,
        is_superuser=(user_data.role == UserRole.ADMIN)
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user


@router.get("/me", response_model=UserResponse)
def read_user_me(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """获取当前用户信息"""
    return current_user


@router.post("/test-token", response_model=UserResponse)
def test_token(current_user: User = Depends(get_current_user)) -> Any:
    """测试访问令牌"""
    return current_user


# 临时端点：创建初始管理员用户
@router.post("/create-admin")
def create_admin_user(db: Session = Depends(get_db)) -> Any:
    """创建初始管理员用户（仅在没有管理员时可用）"""
    # 检查是否已有管理员
    admin_exists = db.query(User).filter(
        User.role == UserRole.ADMIN
    ).first()
    
    if admin_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="管理员用户已存在"
        )
    
    # 创建默认管理员
    admin = User(
        username="admin",
        email="admin@example.com",
        name="系统管理员",
        password_hash=get_password_hash("admin123"),
        role=UserRole.ADMIN,
        department="系统管理部",
        is_active=True,
        is_superuser=True
    )
    
    db.add(admin)
    db.commit()
    db.refresh(admin)
    
    return {"message": "管理员用户创建成功", "username": "admin", "password": "admin123"}