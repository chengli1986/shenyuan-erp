from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from datetime import datetime

# 创建FastAPI应用
app = FastAPI(
    title="弱电工程ERP系统",
    description="专业的弱电工程项目管理与采购系统",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",   # Create-React-App默认端口
        "http://localhost:5173",   # Vite默认端口
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# 安全设置
security = HTTPBearer()

# 数据模型定义
class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    budget: float
    manager: str
    status: str = "planning"

class Project(ProjectBase):
    id: str
    created_at: datetime
    updated_at: datetime
    progress: float = 0.0

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    budget: Optional[float] = None
    manager: Optional[str] = None
    status: Optional[str] = None
    progress: Optional[float] = None

class HealthStatus(BaseModel):
    status: str
    message: str
    timestamp: datetime
    version: str

class SystemStats(BaseModel):
    total_projects: int
    completed_projects: int
    ongoing_projects: int
    delayed_projects: int

# 模拟数据库（实际项目中应该使用真实数据库）
fake_projects_db = [
    {
        "id": "P2024001",
        "name": "某大厦弱电工程",
        "description": "包含监控、门禁、网络布线等系统",
        "budget": 500000.0,
        "manager": "张三",
        "status": "ongoing",
        "progress": 65.0,
        "created_at": "2024-01-15T09:00:00",
        "updated_at": "2024-01-20T14:30:00"
    },
    {
        "id": "P2024002", 
        "name": "工厂监控系统",
        "description": "工厂安防监控系统建设",
        "budget": 300000.0,
        "manager": "李四",
        "status": "completed",
        "progress": 100.0,
        "created_at": "2024-01-10T08:00:00",
        "updated_at": "2024-01-25T16:00:00"
    },
    {
        "id": "P2024003",
        "name": "某小区网络布线及弱电系统建设", 
        "description": "小区智能化弱电系统全套建设",
        "budget": 800000.0,
        "manager": "王五",
        "status": "ongoing",
        "progress": 40.0,
        "created_at": "2024-01-20T10:00:00",
        "updated_at": "2024-01-22T11:00:00"
    }
]

# API路由定义

@app.get("/", summary="根路径", description="系统欢迎页面")
async def root():
    """
    系统根路径，返回欢迎信息
    """
    return {
        "message": "欢迎使用弱电工程ERP系统！",
        "system": "弱电工程ERP系统",
        "version": "1.0.0",
        "docs": "/docs",
        "api_prefix": "/api"
    }

@app.get("/api/health", response_model=HealthStatus, summary="健康检查", description="检查系统运行状态")
async def health_check():
    """
    系统健康检查接口
    - 返回系统运行状态
    - 包含时间戳和版本信息
    """
    return HealthStatus(
        status="healthy",
        message="系统运行正常",
        timestamp=datetime.now(),
        version="1.0.0"
    )

@app.get("/api/stats", response_model=SystemStats, summary="系统统计", description="获取系统统计数据")
async def get_system_stats():
    """
    获取系统统计数据
    - 总项目数
    - 已完成项目数  
    - 进行中项目数
    - 延期项目数
    """
    total = len(fake_projects_db)
    completed = len([p for p in fake_projects_db if p["status"] == "completed"])
    ongoing = len([p for p in fake_projects_db if p["status"] == "ongoing"])
    delayed = len([p for p in fake_projects_db if p["status"] == "delayed"])
    
    return SystemStats(
        total_projects=total,
        completed_projects=completed,
        ongoing_projects=ongoing,
        delayed_projects=delayed
    )

@app.get("/api/projects", response_model=List[Project], summary="获取项目列表", description="获取所有项目的列表")
async def get_projects():
    """
    获取所有项目列表
    - 返回所有项目的基本信息
    - 包含项目状态和进度
    """
    return fake_projects_db

@app.get("/api/projects/{project_id}", response_model=Project, summary="获取项目详情", description="根据项目ID获取项目详细信息")
async def get_project(project_id: str):
    """
    根据项目ID获取项目详情
    - project_id: 项目唯一标识符
    - 返回项目的详细信息
    """
    project = next((p for p in fake_projects_db if p["id"] == project_id), None)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    return project

@app.post("/api/projects", response_model=Project, summary="创建新项目", description="创建一个新的项目")
async def create_project(project: ProjectCreate):
    """
    创建新项目
    - 接收项目基本信息
    - 自动生成项目ID和时间戳
    - 返回创建的项目信息
    """
    # 生成新的项目ID
    project_count = len(fake_projects_db) + 1
    new_id = f"P2024{project_count:03d}"
    
    # 创建新项目
    new_project = {
        "id": new_id,
        "name": project.name,
        "description": project.description,
        "budget": project.budget,
        "manager": project.manager,
        "status": project.status,
        "progress": 0.0,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    fake_projects_db.append(new_project)
    return new_project

@app.put("/api/projects/{project_id}", response_model=Project, summary="更新项目", description="更新指定项目的信息")
async def update_project(project_id: str, project_update: ProjectUpdate):
    """
    更新项目信息
    - project_id: 要更新的项目ID
    - 只更新提供的字段
    - 自动更新修改时间
    """
    project_index = next((i for i, p in enumerate(fake_projects_db) if p["id"] == project_id), None)
    if project_index is None:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    # 更新项目信息
    stored_project = fake_projects_db[project_index]
    update_data = project_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        stored_project[field] = value
    
    stored_project["updated_at"] = datetime.now().isoformat()
    fake_projects_db[project_index] = stored_project
    
    return stored_project

@app.delete("/api/projects/{project_id}", summary="删除项目", description="删除指定的项目")
async def delete_project(project_id: str):
    """
    删除项目
    - project_id: 要删除的项目ID
    - 返回删除结果
    """
    project_index = next((i for i, p in enumerate(fake_projects_db) if p["id"] == project_id), None)
    if project_index is None:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    deleted_project = fake_projects_db.pop(project_index)
    return {"message": f"项目 {deleted_project['name']} 已成功删除", "deleted_project_id": project_id}

# 用户认证相关接口（示例）
@app.post("/api/auth/login", summary="用户登录", description="用户认证登录")
async def login(username: str, password: str):
    """
    用户登录接口
    - 验证用户名和密码
    - 返回认证token（示例实现）
    """
    # 这里是示例实现，实际项目中需要真实的用户验证
    if username == "admin" and password == "admin123":
        return {
            "access_token": "fake_jwt_token_here",
            "token_type": "bearer",
            "user": {
                "username": username,
                "role": "admin",
                "name": "系统管理员"
            }
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

@app.get("/api/auth/me", summary="获取当前用户信息", description="获取当前登录用户的信息")
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    获取当前用户信息
    - 需要Bearer token认证
    - 返回用户基本信息
    """
    # 这里是示例实现，实际项目中需要验证JWT token
    return {
        "username": "admin",
        "role": "admin", 
        "name": "系统管理员",
        "permissions": ["read", "write", "delete"]
    }

# 合同清单相关接口（示例）
@app.get("/api/contracts", summary="获取合同清单", description="获取项目合同清单")
async def get_contracts():
    """
    获取合同清单列表
    """
    return [
        {
            "id": "C001",
            "project_id": "P2024001",
            "name": "某大厦弱电工程合同清单",
            "version": "v1.0",
            "upload_date": "2024-01-15",
            "status": "active"
        }
    ]

# 申购管理相关接口（示例）
@app.get("/api/purchases", summary="获取申购单列表", description="获取所有申购单")
async def get_purchases():
    """
    获取申购单列表
    """
    return [
        {
            "id": "PR001",
            "project_id": "P2024001", 
            "requester": "张三",
            "status": "pending",
            "total_amount": 50000,
            "request_date": "2024-01-20"
        }
    ]

# 库存管理相关接口（示例）
@app.get("/api/inventory", summary="获取库存信息", description="获取库存统计信息")
async def get_inventory():
    """
    获取库存信息
    """
    return [
        {
            "item_name": "六类网线",
            "specification": "305米/箱",
            "current_stock": 50,
            "unit": "箱",
            "location": "仓库A"
        },
        {
            "item_name": "监控摄像头",
            "specification": "200万像素红外球机",
            "current_stock": 25,
            "unit": "台", 
            "location": "仓库B"
        }
    ]

# 启动应用（用于开发测试）
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )