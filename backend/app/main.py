# backend/app/main.py
"""
FastAPI主程序入口 - 包含项目管理API
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from contextlib import asynccontextmanager

# 导入数据库相关
from app.core.database import engine, Base

# 导入所有模型（确保数据库表创建）
from app.models import project, project_file, contract, test_result

# 导入API路由
from app.api.v1 import api_router

# 导入测试调度器
from app.core.test_scheduler import start_test_scheduler, stop_test_scheduler

# 应用生命周期管理
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时执行
    print("正在创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("数据库表创建完成！")
    
    # 启动测试调度器（后台任务）
    print("启动测试调度器...")
    scheduler_task = asyncio.create_task(start_test_scheduler())
    
    yield
    
    # 关闭时执行
    print("正在关闭测试调度器...")
    stop_test_scheduler()
    scheduler_task.cancel()

# 创建FastAPI应用实例
app = FastAPI(
    title="弱电工程ERP系统",
    description="专为弱电工程公司设计的ERP系统",
    version="1.0.0",
    lifespan=lifespan
)

# 配置CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# 注册API路由
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    """根路径，返回欢迎信息"""
    return {
        "message": "弱电工程ERP系统API", 
        "version": "1.0.0",
        "status": "running",
        "available_endpoints": [
            "/docs - API文档",
            "/api/v1/projects - 项目管理API"
        ]
    }

@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy", "database": "connected"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)