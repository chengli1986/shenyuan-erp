"""
合同清单明细管理API接口
"""

import math
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.contract import ContractFileVersion, SystemCategory, ContractItem
from app.schemas.contract import (
    ContractItemCreate,
    ContractItemUpdate,
    ContractItemResponse,
)

router = APIRouter()


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
