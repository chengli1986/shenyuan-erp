# backend/app/api/v1/__init__.py
"""
API v1版本路由汇总
这个文件把所有的API接口"打包"在一起
就像把所有菜单页面装订成一本菜单册
"""

from fastapi import APIRouter
from . import projects, project_files, contracts, file_upload, test_results, test_simple, test_minimal, purchases

# 创建v1版本的主路由
api_router = APIRouter()

# 注册项目相关的API路由
api_router.include_router(
    projects.router, 
    prefix="/projects", 
    tags=["projects"]
)

# 注册项目文件相关的API路由
api_router.include_router(
    project_files.router,
    prefix="/projects", 
    tags=["project-files"]
)

# 注册合同清单相关的API路由
api_router.include_router(
    contracts.router,
    prefix="/contracts",
    tags=["contracts"]
)

# 注册文件上传相关的API路由
api_router.include_router(
    file_upload.router,
    prefix="/upload",
    tags=["file-upload"]
)

# 注册测试结果相关的API路由
api_router.include_router(
    test_results.router,
    prefix="/tests",
    tags=["test-results"]
)

# 注册简化测试API路由
api_router.include_router(
    test_simple.router,
    prefix="/tests",
    tags=["test-simple"]
)

# 注册最小化测试API路由
api_router.include_router(
    test_minimal.router,
    prefix="/tests",
    tags=["test-minimal"]
)

# 注册采购请购相关的API路由
api_router.include_router(
    purchases.router,
    prefix="/purchases",
    tags=["purchases"]
)

