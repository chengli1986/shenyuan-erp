# backend/app/main.py
"""
FastAPI主程序入口 - 包含项目管理API
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 导入数据库相关
from app.core.database import engine, Base

# 导入API路由
from app.api.v1 import api_router

# 创建数据库表
print("正在创建数据库表...")
Base.metadata.create_all(bind=engine)
print("数据库表创建完成！")

# 创建FastAPI应用实例
app = FastAPI(
    title="弱电工程ERP系统",
    description="专为弱电工程公司设计的ERP系统",
    version="1.0.0",
)

# 配置CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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