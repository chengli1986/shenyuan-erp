"""
用户认证相关的数据模型
"""

from typing import Optional
from pydantic import BaseModel, EmailStr
from app.models.user import UserRole


class Token(BaseModel):
    """访问令牌响应"""
    access_token: str
    token_type: str
    expires_in: int
    user: dict


class TokenData(BaseModel):
    """Token数据"""
    user_id: Optional[str] = None


class UserLogin(BaseModel):
    """用户登录请求"""
    username: str
    password: str


class UserRegister(BaseModel):
    """用户注册请求"""
    username: str
    email: Optional[EmailStr] = None
    name: str
    password: str
    role: UserRole
    department: Optional[str] = None
    phone: Optional[str] = None


class UserResponse(BaseModel):
    """用户响应数据"""
    id: int
    username: str
    email: Optional[str] = None
    name: str
    role: UserRole
    department: Optional[str] = None
    phone: Optional[str] = None
    is_active: bool
    is_superuser: bool
    created_at: Optional[str] = None
    last_login: Optional[str] = None

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """用户更新请求"""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    department: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None


class UserPasswordChange(BaseModel):
    """密码修改请求"""
    old_password: str
    new_password: str