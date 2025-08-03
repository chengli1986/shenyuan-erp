# backend/app/api/v1/contracts.py
"""
合同清单API接口

提供合同清单管理的REST API端点：
1. 合同清单版本管理（创建、查询、更新）
2. 系统分类管理（增删改查）
3. 合同清单明细管理（增删改查）
4. 项目合同清单汇总信息
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import math
import logging
import os

from app.core.database import get_db
from app.models.project import Project
from app.models.contract import ContractFileVersion, SystemCategory, ContractItem
from app.schemas.contract import (
    # 版本相关
    ContractFileVersionCreate,
    ContractFileVersionUpdate,
    ContractFileVersionResponse,
    # 系统分类相关
    SystemCategoryCreate,
    SystemCategoryUpdate,
    SystemCategoryResponse,
    # 明细相关
    ContractItemCreate,
    ContractItemUpdate,
    ContractItemResponse,
    ContractItemListResponse,
    # 汇总信息
    ContractSummaryResponse
)

# 创建路由器
router = APIRouter()

# 配置日志
logger = logging.getLogger(__name__)


# ============================
# 合同清单版本管理 API
# ============================

@router.get("/projects/{project_id}/contract-versions", response_model=List[ContractFileVersionResponse])
async def get_contract_versions(
    project_id: int = Path(..., description="项目ID"),
    db: Session = Depends(get_db)
):
    """
    获取项目的所有合同清单版本
    
    返回指定项目的所有合同清单版本列表，按版本号倒序排列
    """
    
    # 验证项目是否存在
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail=f"项目ID {project_id} 不存在")
    
    # 查询版本列表
    versions = db.query(ContractFileVersion).filter(
        ContractFileVersion.project_id == project_id
    ).order_by(ContractFileVersion.version_number.desc()).all()
    
    return versions


@router.get("/projects/{project_id}/contract-versions/current", response_model=ContractFileVersionResponse)
async def get_current_contract_version(
    project_id: int = Path(..., description="项目ID"),
    db: Session = Depends(get_db)
):
    """
    获取项目的当前合同清单版本
    
    返回当前生效的合同清单版本
    """
    
    # 验证项目是否存在
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail=f"项目ID {project_id} 不存在")
    
    # 查询当前版本
    current_version = db.query(ContractFileVersion).filter(
        ContractFileVersion.project_id == project_id,
        ContractFileVersion.is_current == True
    ).first()
    
    if not current_version:
        raise HTTPException(status_code=404, detail="该项目暂无当前生效的合同清单版本")
    
    return current_version


@router.post("/projects/{project_id}/contract-versions", response_model=ContractFileVersionResponse)
async def create_contract_version(
    version_data: ContractFileVersionCreate,
    project_id: int = Path(..., description="项目ID"),
    db: Session = Depends(get_db)
):
    """
    创建新的合同清单版本
    
    注意：创建新版本时，会自动将当前版本设为非当前状态
    """
    
    # 验证项目是否存在
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail=f"项目ID {project_id} 不存在")
    
    # 验证项目ID匹配
    if version_data.project_id != project_id:
        raise HTTPException(status_code=400, detail="请求路径中的项目ID与数据中的项目ID不匹配")
    
    try:
        # 获取下一个版本号
        latest_version = db.query(ContractFileVersion).filter(
            ContractFileVersion.project_id == project_id
        ).order_by(ContractFileVersion.version_number.desc()).first()
        
        next_version_number = (latest_version.version_number + 1) if latest_version else 1
        
        # 如果设为当前版本，需要将其他版本设为非当前
        if getattr(version_data, 'is_current', True):  # 默认新版本为当前版本
            db.query(ContractFileVersion).filter(
                ContractFileVersion.project_id == project_id,
                ContractFileVersion.is_current == True
            ).update({"is_current": False})
        
        # 创建新版本
        new_version = ContractFileVersion(
            project_id=project_id,
            version_number=next_version_number,
            upload_user_name=version_data.upload_user_name,
            original_filename=version_data.original_filename,
            stored_filename=f"contract_v{next_version_number}_{project_id}_{version_data.original_filename}",
            upload_reason=version_data.upload_reason,
            change_description=version_data.change_description,
            is_optimized=version_data.is_optimized,
            change_evidence_file=version_data.change_evidence_file,
            is_current=True  # 新版本默认为当前版本
        )
        
        db.add(new_version)
        db.commit()
        db.refresh(new_version)
        
        return new_version
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"创建合同清单版本失败：{str(e)}")


# ============================
# 系统分类管理 API
# ============================

@router.get("/test")
async def test_api():
    """测试API是否工作"""
    return {"status": "working"}

@router.get("/test-pagination")
async def test_pagination(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """测试分页功能"""
    try:
        query = db.query(ContractItem).filter(
            ContractItem.version_id == 7,
            ContractItem.is_active == True
        )
        
        total = query.count()
        offset = (page - 1) * size
        items = query.offset(offset).limit(size).all()
        
        # 手动转换为简单字典
        simple_items = []
        for item in items:
            simple_items.append({
                "id": item.id,
                "item_name": item.item_name,
                "brand_model": item.brand_model,
                "specification": item.specification
            })
        
        return {
            "items": simple_items,
            "total": total,
            "page": page,
            "size": size,
            "count": len(simple_items)
        }
    except Exception as e:
        return {"error": str(e)}

@router.get("/projects/{project_id}/versions/{version_id}/categories")
async def get_system_categories_list(project_id: int, version_id: int, db: Session = Depends(get_db)):
    """Get system categories for a specific version"""
    categories = db.query(SystemCategory).filter(
        SystemCategory.project_id == project_id,
        SystemCategory.version_id == version_id
    ).all()
    
    # 转换为响应格式
    result = []
    for category in categories:
        result.append({
            "id": category.id,
            "project_id": category.project_id,
            "version_id": category.version_id,
            "category_name": category.category_name,
            "category_code": category.category_code,
            "excel_sheet_name": category.excel_sheet_name,
            "budget_amount": str(category.budget_amount) if category.budget_amount else "0",
            "total_items_count": category.total_items_count,
            "description": category.description,
            "remarks": category.remarks,
            "created_at": category.created_at.isoformat() if category.created_at else None,
            "updated_at": category.updated_at.isoformat() if category.updated_at else None
        })
    
    return result

@router.get("/projects/{project_id}/versions/{version_id}/categories-working")
async def get_system_categories_working(project_id: int, version_id: int, db: Session = Depends(get_db)):
    """Get system categories for a specific version - proper implementation"""
    try:
        categories = db.query(SystemCategory).filter(
            SystemCategory.project_id == project_id,
            SystemCategory.version_id == version_id
        ).all()
        
        # 转换为响应格式
        result = []
        for category in categories:
            result.append({
                "id": category.id,
                "project_id": category.project_id,
                "version_id": category.version_id,
                "category_name": category.category_name,
                "category_code": category.category_code,
                "excel_sheet_name": category.excel_sheet_name,
                "budget_amount": str(category.budget_amount) if category.budget_amount else "0",
                "total_items_count": category.total_items_count,
                "description": category.description,
                "remarks": category.remarks,
                "created_at": category.created_at.isoformat() if category.created_at else None,
                "updated_at": category.updated_at.isoformat() if category.updated_at else None
            })
        
        return result
        
    except Exception as e:
        logger.error(f"获取系统分类失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取系统分类失败: {str(e)}")


@router.post("/projects/{project_id}/versions/{version_id}/categories", response_model=SystemCategoryResponse)
async def create_system_category(
    category_data: SystemCategoryCreate,
    project_id: int = Path(..., description="项目ID"),
    version_id: int = Path(..., description="版本ID"),
    db: Session = Depends(get_db)
):
    """
    创建新的系统分类
    """
    
    # 验证版本是否存在
    version = db.query(ContractFileVersion).filter(
        ContractFileVersion.id == version_id,
        ContractFileVersion.project_id == project_id
    ).first()
    
    if not version:
        raise HTTPException(status_code=404, detail="指定的版本不存在")
    
    # 验证数据匹配
    if category_data.project_id != project_id or category_data.version_id != version_id:
        raise HTTPException(status_code=400, detail="请求路径与数据不匹配")
    
    # 检查分类名称是否重复
    existing_category = db.query(SystemCategory).filter(
        SystemCategory.version_id == version_id,
        SystemCategory.category_name == category_data.category_name
    ).first()
    
    if existing_category:
        raise HTTPException(status_code=400, detail=f"系统分类 '{category_data.category_name}' 已存在")
    
    try:
        # 创建新分类
        new_category = SystemCategory(**category_data.dict())
        
        db.add(new_category)
        db.commit()
        db.refresh(new_category)
        
        return new_category
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"创建系统分类失败：{str(e)}")


# ============================
# 合同清单明细管理 API
# ============================

@router.get("/projects/{project_id}/versions/{version_id}/items")
async def get_contract_items(
    project_id: int = Path(..., description="项目ID"),
    version_id: int = Path(..., description="版本ID"),
    category_id: Optional[int] = Query(None, description="系统分类ID筛选"),
    item_type: Optional[str] = Query(None, description="物料类型筛选"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db)
):
    """
    获取合同清单明细列表
    
    支持按系统分类、物料类型筛选，支持关键词搜索和分页
    """
    
    # 验证版本是否存在
    version = db.query(ContractFileVersion).filter(
        ContractFileVersion.id == version_id,
        ContractFileVersion.project_id == project_id
    ).first()
    
    if not version:
        raise HTTPException(status_code=404, detail="指定的版本不存在")
    
    # 构建查询
    query = db.query(ContractItem).filter(
        ContractItem.version_id == version_id,
        ContractItem.is_active == True
    )
    
    # 应用筛选条件
    if category_id:
        query = query.filter(ContractItem.category_id == category_id)
    
    if item_type:
        query = query.filter(ContractItem.item_type == item_type)
    
    if search:
        query = query.filter(
            (ContractItem.item_name.contains(search)) |
            (ContractItem.brand_model.contains(search)) |
            (ContractItem.specification.contains(search))
        )
    
    # 计算总数
    total = query.count()
    
    # 分页查询
    offset = (page - 1) * size
    items = query.offset(offset).limit(size).all()
    
    # 计算总页数
    pages = math.ceil(total / size)
    
    # 将数据库对象转换为字典格式，避免Pydantic序列化问题
    items_dict = [item.to_dict() for item in items]
    
    return {
        "items": items_dict,
        "total": total,
        "page": page,
        "size": size,
        "pages": pages
    }


@router.post("/projects/{project_id}/versions/{version_id}/items", response_model=ContractItemResponse)
async def create_contract_item(
    item_data: ContractItemCreate,
    project_id: int = Path(..., description="项目ID"),
    version_id: int = Path(..., description="版本ID"),
    db: Session = Depends(get_db)
):
    """
    创建新的合同清单明细
    """
    
    # 验证版本是否存在
    version = db.query(ContractFileVersion).filter(
        ContractFileVersion.id == version_id,
        ContractFileVersion.project_id == project_id
    ).first()
    
    if not version:
        raise HTTPException(status_code=404, detail="指定的版本不存在")
    
    # 验证数据匹配
    if item_data.project_id != project_id or item_data.version_id != version_id:
        raise HTTPException(status_code=400, detail="请求路径与数据不匹配")
    
    # 验证系统分类是否存在（如果提供）
    if item_data.category_id:
        category = db.query(SystemCategory).filter(
            SystemCategory.id == item_data.category_id,
            SystemCategory.version_id == version_id
        ).first()
        
        if not category:
            raise HTTPException(status_code=400, detail="指定的系统分类不存在")
    
    try:
        # 创建新明细
        new_item = ContractItem(**item_data.dict())
        
        # 计算总价
        new_item.calculate_total_price()
        
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        
        return new_item
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"创建合同清单明细失败：{str(e)}")


@router.get("/projects/{project_id}/versions/{version_id}/items/{item_id}", response_model=ContractItemResponse)
async def get_contract_item(
    project_id: int = Path(..., description="项目ID"),
    version_id: int = Path(..., description="版本ID"),
    item_id: int = Path(..., description="明细ID"),
    db: Session = Depends(get_db)
):
    """
    获取单个合同清单明细
    """
    
    item = db.query(ContractItem).filter(
        ContractItem.id == item_id,
        ContractItem.version_id == version_id,
        ContractItem.project_id == project_id,
        ContractItem.is_active == True
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="指定的合同清单明细不存在")
    
    return item


@router.put("/projects/{project_id}/versions/{version_id}/items/{item_id}", response_model=ContractItemResponse)
async def update_contract_item(
    item_update: ContractItemUpdate,
    project_id: int = Path(..., description="项目ID"),
    version_id: int = Path(..., description="版本ID"),
    item_id: int = Path(..., description="明细ID"),
    db: Session = Depends(get_db)
):
    """
    更新合同清单明细
    """
    
    item = db.query(ContractItem).filter(
        ContractItem.id == item_id,
        ContractItem.version_id == version_id,
        ContractItem.project_id == project_id,
        ContractItem.is_active == True
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="指定的合同清单明细不存在")
    
    try:
        # 更新字段
        update_data = item_update.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(item, field, value)
        
        # 重新计算总价
        item.calculate_total_price()
        
        db.commit()
        db.refresh(item)
        
        return item
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"更新合同清单明细失败：{str(e)}")


# ============================
# 汇总信息 API
# ============================

@router.get("/projects/{project_id}/contract-summary", response_model=ContractSummaryResponse)
async def get_contract_summary(
    project_id: int = Path(..., description="项目ID"),
    db: Session = Depends(get_db)
):
    """
    获取项目合同清单汇总信息
    
    包括当前版本、总版本数、总分类数、总明细数、总金额等
    """
    
    # 验证项目是否存在
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail=f"项目ID {project_id} 不存在")
    
    # 获取当前版本
    current_version = db.query(ContractFileVersion).filter(
        ContractFileVersion.project_id == project_id,
        ContractFileVersion.is_current == True
    ).first()
    
    # 统计总版本数
    total_versions = db.query(ContractFileVersion).filter(
        ContractFileVersion.project_id == project_id
    ).count()
    
    # 统计当前版本的数据
    total_categories = 0
    total_items = 0
    total_amount = 0
    
    if current_version:
        total_categories = db.query(SystemCategory).filter(
            SystemCategory.version_id == current_version.id
        ).count()
        
        items_query = db.query(ContractItem).filter(
            ContractItem.version_id == current_version.id,
            ContractItem.is_active == True
        )
        
        total_items = items_query.count()
        
        # 计算总金额
        total_amount = sum([
            float(item.total_price) for item in items_query.all() 
            if item.total_price
        ])
    
    return ContractSummaryResponse(
        project_id=project_id,
        current_version=current_version,
        total_versions=total_versions,
        total_categories=total_categories,
        total_items=total_items,
        total_amount=total_amount
    )


# ============================
# 文件下载 API
# ============================

@router.get("/projects/{project_id}/contract-versions/{version_id}/download")
async def download_contract_file(
    project_id: int = Path(..., description="项目ID"),
    version_id: int = Path(..., description="版本ID"),
    db: Session = Depends(get_db)
):
    """
    下载合同清单文件
    """
    
    # 验证项目是否存在
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail=f"项目ID {project_id} 不存在")
    
    # 验证版本是否存在
    version = db.query(ContractFileVersion).filter(
        ContractFileVersion.id == version_id,
        ContractFileVersion.project_id == project_id
    ).first()
    
    if not version:
        raise HTTPException(status_code=404, detail="指定的版本不存在")
    
    # 构建文件路径 - 使用绝对路径
    backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    file_path = os.path.join(backend_dir, "uploads", "contracts", version.stored_filename)
    
    print(f"查找文件路径: {file_path}")
    print(f"文件是否存在: {os.path.exists(file_path)}")
    print(f"存储文件名: {version.stored_filename}")
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")
    
    # 返回文件下载响应
    return FileResponse(
        path=file_path,
        filename=version.original_filename,
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )