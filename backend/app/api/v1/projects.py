# backend/app/api/v1/projects.py
"""
项目管理API接口
这是前端和后端对话的"翻译官"
定义了前端可以调用哪些功能URL
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
import math

from app.core.database import get_db
from app.models.project import Project
from app.schemas.project import (
    ProjectCreate, 
    ProjectUpdate, 
    ProjectResponse, 
    ProjectListResponse
)

# 创建路由器 - 就像创建一个"服务台"
router = APIRouter()


@router.get("/", response_model=ProjectListResponse)
async def get_projects(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
    search: str = Query(None, description="搜索关键词"),
    status: str = Query(None, description="状态筛选"),
    db: Session = Depends(get_db)
):
    """
    获取项目列表
    
    这个函数处理 GET /projects 请求
    就像餐厅服务员问你："要什么菜？"
    """
    
    # 构建查询 - 就像在数据库里找东西
    query = db.query(Project)
    
    # 如果有搜索词，就按项目名称或编号搜索
    if search:
        query = query.filter(
            (Project.project_name.contains(search)) |
            (Project.project_code.contains(search))
        )
    
    # 如果有状态筛选
    if status:
        query = query.filter(Project.status == status)
    
    # 计算总数
    total = query.count()
    
    # 分页查询 - 就像翻书，一页一页看
    offset = (page - 1) * size
    projects = query.offset(offset).limit(size).all()
    
    # 计算总页数
    pages = math.ceil(total / size)
    
    # 返回结果
    return ProjectListResponse(
        items=projects,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.post("/", response_model=ProjectResponse)
async def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db)
):
    """
    创建新项目
    
    处理 POST /projects 请求
    就像填写一张新的项目申请表
    """
    
    # 检查项目编号是否已存在
    existing_project = db.query(Project).filter(
        Project.project_code == project.project_code
    ).first()
    
    if existing_project:
        raise HTTPException(
            status_code=400,
            detail=f"项目编号 {project.project_code} 已存在"
        )
    
    # 创建新项目 - 就像填写新的档案卡
    db_project = Project(**project.dict())
    
    # 保存到数据库
    db.add(db_project)      # 添加到"待保存"列表
    db.commit()             # 正式保存
    db.refresh(db_project)  # 刷新获取自动生成的ID等信息
    
    return db_project


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    db: Session = Depends(get_db)
):
    """
    获取单个项目详情
    
    处理 GET /projects/{id} 请求
    就像查看某个特定的档案卡
    """
    
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(
            status_code=404,
            detail=f"项目 ID {project_id} 不存在"
        )
    
    return project


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_update: ProjectUpdate,
    db: Session = Depends(get_db)
):
    """
    更新项目信息
    
    处理 PUT /projects/{id} 请求
    就像修改档案卡上的信息
    """
    
    # 先找到要更新的项目
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(
            status_code=404,
            detail=f"项目 ID {project_id} 不存在"
        )
    
    # 只更新传入的字段
    update_data = project_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(project, field, value)
    
    # 保存更改
    db.commit()
    db.refresh(project)
    
    return project


@router.delete("/{project_id}")
async def delete_project(
    project_id: int,
    db: Session = Depends(get_db)
):
    """
    删除项目
    
    处理 DELETE /projects/{id} 请求
    就像销毁某个档案卡
    """
    
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(
            status_code=404,
            detail=f"项目 ID {project_id} 不存在"
        )
    
    # 删除项目
    db.delete(project)
    db.commit()
    
    return {"message": f"项目 {project.project_name} 已删除"}