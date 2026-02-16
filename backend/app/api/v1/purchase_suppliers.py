"""
采购请购API接口 - 供应商管理
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.api import deps
from app.core.database import get_db
from app.models.purchase import Supplier
from app.models.user import User
from app.schemas.purchase import (
    SupplierCreate, SupplierUpdate, SupplierInDB, SupplierListResponse
)

router = APIRouter()


# ========== 供应商管理 ==========

@router.get("/suppliers/", response_model=SupplierListResponse)
async def get_suppliers(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """获取供应商列表"""
    query = db.query(Supplier)

    if search:
        query = query.filter(
            or_(
                Supplier.supplier_name.contains(search),
                Supplier.supplier_code.contains(search),
                Supplier.contact_person.contains(search)
            )
        )

    if is_active is not None:
        query = query.filter(Supplier.is_active == is_active)

    total = query.count()
    items = query.offset((page - 1) * size).limit(size).all()

    return {
        "items": items,
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size
    }


@router.post("/suppliers/", response_model=SupplierInDB)
async def create_supplier(
    supplier_data: SupplierCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """创建供应商（采购员）"""
    if current_user.role.value not in ["purchaser", "admin"]:
        raise HTTPException(status_code=403, detail="只有采购员可以创建供应商")

    # 检查供应商名称是否已存在
    existing = db.query(Supplier).filter(
        Supplier.supplier_name == supplier_data.supplier_name
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="供应商名称已存在")

    # 生成供应商编码
    if not supplier_data.supplier_code:
        count = db.query(Supplier).count()
        supplier_data.supplier_code = f"SUP{str(count + 1).zfill(6)}"

    supplier = Supplier(
        **supplier_data.dict(),
        created_by=current_user.id
    )
    db.add(supplier)
    db.commit()
    db.refresh(supplier)

    return supplier


@router.put("/suppliers/{supplier_id}", response_model=SupplierInDB)
async def update_supplier(
    supplier_id: int,
    update_data: SupplierUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """更新供应商信息"""
    if current_user.role.value not in ["purchaser", "admin"]:
        raise HTTPException(status_code=403, detail="只有采购员可以更新供应商")

    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="供应商不存在")

    for field, value in update_data.dict(exclude_unset=True).items():
        setattr(supplier, field, value)

    db.commit()
    db.refresh(supplier)

    return supplier
