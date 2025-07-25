# backend/app/api/v1/__init__.py
"""
API v1版本路由汇总
这个文件把所有的API接口"打包"在一起
就像把所有菜单页面装订成一本菜单册
"""

from fastapi import APIRouter
from . import projects

# 创建v1版本的主路由
api_router = APIRouter()

# 注册项目相关的API路由
# prefix="/projects" 意思是所有项目API都以 /projects 开头
# tags=["projects"] 用于API文档分类，让文档更整洁
api_router.include_router(
    projects.router, 
    prefix="/projects", 
    tags=["projects"]
)