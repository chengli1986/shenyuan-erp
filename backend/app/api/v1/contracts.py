"""
合同清单API接口 - 系统分类、汇总和文件下载
"""

from fastapi import APIRouter, Depends, HTTPException, Path
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import logging
import os

from app.api import deps
from app.core.database import get_db
from app.models.user import User
from app.models.project import Project
from app.models.contract import ContractFileVersion, SystemCategory, ContractItem
from app.schemas.contract import (
    SystemCategoryCreate,
    SystemCategoryResponse,
    ContractSummaryResponse,
)

# 创建路由器
router = APIRouter()

# 配置日志
logger = logging.getLogger(__name__)


# ============================
# 系统分类管理 API
# ============================

@router.get("/projects/{project_id}/versions/{version_id}/categories")
async def get_system_categories_list(project_id: int, version_id: int, db: Session = Depends(get_db), current_user: User = Depends(deps.get_current_user)):
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
async def get_system_categories_working(project_id: int, version_id: int, db: Session = Depends(get_db), current_user: User = Depends(deps.get_current_user)):
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
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
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
# 汇总信息 API
# ============================

@router.get("/projects/{project_id}/contract-summary", response_model=ContractSummaryResponse)
async def get_contract_summary(
    project_id: int = Path(..., description="项目ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
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
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
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

    logger.debug(f"查找文件路径: {file_path}")
    logger.debug(f"文件是否存在: {os.path.exists(file_path)}")
    logger.debug(f"存储文件名: {version.stored_filename}")

    # 检查文件是否存在
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")

    # 返回文件下载响应
    return FileResponse(
        path=file_path,
        filename=version.original_filename,
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
