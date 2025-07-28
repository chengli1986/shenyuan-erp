"""
API依赖模块
"""

from fastapi import HTTPException, status


def get_current_user():
    """获取当前用户 - 临时模拟实现"""
    # TODO: 实现真正的用户认证
    return {
        "id": 1,
        "username": "admin",
        "email": "admin@example.com"
    }