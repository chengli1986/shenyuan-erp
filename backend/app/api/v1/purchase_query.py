"""
采购请购模块 - 合同清单物料查询和系统分类查询
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from app.api import deps
from app.core.database import get_db
from app.models.purchase import (
    PurchaseRequest, PurchaseRequestItem, PurchaseStatus
)
from app.models.contract import ContractItem
from app.models.user import User
from app.schemas.purchase import AuxiliaryTemplateCreate, AuxiliaryTemplateInDB
from app.services.purchase_service import PurchaseService

router = APIRouter()


# ========== 合同清单物料查询 ==========

@router.get("/contract-items/by-project/{project_id}")
async def get_contract_items_by_project(
    project_id: int,
    item_type: Optional[str] = Query(None, description="物料类型：主材/辅材"),
    search: Optional[str] = Query(None, description="搜索关键字"),
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    根据项目获取合同清单物料
    用于申购单表单的智能选择功能
    """
    # 获取项目的最新版本合同清单
    from app.models.contract import ContractFileVersion

    latest_version = db.query(ContractFileVersion).filter(
        ContractFileVersion.project_id == project_id,
        ContractFileVersion.is_current == True
    ).first()

    if not latest_version:
        raise HTTPException(
            status_code=404,
            detail="该项目还没有上传合同清单"
        )

    # 查询合同清单项目
    query = db.query(ContractItem).filter(
        ContractItem.project_id == project_id,
        ContractItem.version_id == latest_version.id,
        ContractItem.is_active == True
    )

    # 按物料类型筛选（主要用于限制主材只能从清单选择）
    if item_type:
        query = query.filter(ContractItem.item_type == item_type)

    # 搜索功能
    if search:
        query = query.filter(
            or_(
                ContractItem.item_name.ilike(f"%{search}%"),
                ContractItem.brand_model.ilike(f"%{search}%"),
                ContractItem.specification.ilike(f"%{search}%")
            )
        )

    items = query.all()

    return {
        "items": [item.to_dict() for item in items],
        "project_id": project_id,
        "version_id": latest_version.id,
        "total": len(items)
    }


@router.get("/contract-items/{item_id}/details")
async def get_contract_item_details(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    获取合同清单物料详细信息
    用于自动填充申购表单的相关字段
    """
    item = db.query(ContractItem).filter(
        ContractItem.id == item_id,
        ContractItem.is_active == True
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="合同清单物料不存在")

    # 计算已申购数量（只统计总经理已批准和已完成的申购单）
    purchased_quantity = db.query(func.sum(PurchaseRequestItem.quantity)).join(
        PurchaseRequest
    ).filter(
        PurchaseRequestItem.contract_item_id == item_id,
        PurchaseRequest.status.in_([PurchaseStatus.FINAL_APPROVED, PurchaseStatus.COMPLETED])
    ).scalar() or 0

    # 计算剩余可申购数量
    remaining_quantity = float(item.quantity) - float(purchased_quantity)

    return {
        "item": item.to_dict(),
        "purchased_quantity": float(purchased_quantity),
        "remaining_quantity": max(0, remaining_quantity),
        "can_purchase": remaining_quantity > 0
    }


@router.get("/material-names/by-project/{project_id}")
async def get_material_names_by_project(
    project_id: int,
    item_type: str = Query("主材", description="物料类型：主材/辅材"),
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    获取项目的物料名称列表
    用于申购表单的下拉选择
    """
    from app.models.contract import ContractFileVersion

    latest_version = db.query(ContractFileVersion).filter(
        ContractFileVersion.project_id == project_id,
        ContractFileVersion.is_current == True
    ).first()

    if not latest_version:
        return {"material_names": []}

    # 获取去重的物料名称
    material_names = db.query(ContractItem.item_name).distinct().filter(
        ContractItem.project_id == project_id,
        ContractItem.version_id == latest_version.id,
        ContractItem.item_type == item_type,
        ContractItem.is_active == True
    ).all()

    return {
        "material_names": [name[0] for name in material_names],
        "item_type": item_type,
        "project_id": project_id
    }


@router.get("/specifications/by-material")
async def get_specifications_by_material(
    project_id: int,
    item_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    根据物料名称获取可选的规格型号
    用于联动选择功能
    """
    from app.models.contract import ContractFileVersion

    latest_version = db.query(ContractFileVersion).filter(
        ContractFileVersion.project_id == project_id,
        ContractFileVersion.is_current == True
    ).first()

    if not latest_version:
        return {"specifications": []}

    # 获取该物料名称下的所有规格选项
    items = db.query(ContractItem).filter(
        ContractItem.project_id == project_id,
        ContractItem.version_id == latest_version.id,
        ContractItem.item_name == item_name,
        ContractItem.is_active == True
    ).all()

    specifications = []
    for item in items:
        # 计算已申购数量（只统计总经理已批准和已完成的申购单）
        purchased_quantity = db.query(func.sum(PurchaseRequestItem.quantity)).join(
            PurchaseRequest
        ).filter(
            PurchaseRequestItem.contract_item_id == item.id,
            PurchaseRequest.status.in_([PurchaseStatus.FINAL_APPROVED, PurchaseStatus.COMPLETED])
        ).scalar() or 0

        remaining_quantity = float(item.quantity) - float(purchased_quantity)

        specifications.append({
            "contract_item_id": item.id,
            "specification": item.specification,
            "brand_model": item.brand_model,
            "unit": item.unit,
            "total_quantity": float(item.quantity),
            "purchased_quantity": float(purchased_quantity),
            "remaining_quantity": max(0, remaining_quantity),
            "unit_price": float(item.unit_price) if item.unit_price else None
        })

    return {
        "specifications": specifications,
        "item_name": item_name,
        "project_id": project_id
    }


# ========== 辅材智能推荐 ==========

@router.get("/auxiliary/recommend")
async def recommend_auxiliary_materials(
    main_material_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    根据主材推荐相关辅材
    基于历史数据和模板库
    """
    service = PurchaseService(db)
    recommendations = service.recommend_auxiliary_materials(main_material_id)
    return recommendations


@router.post("/auxiliary/templates/", response_model=AuxiliaryTemplateInDB)
async def create_auxiliary_template(
    template_data: AuxiliaryTemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """创建辅材模板"""
    if current_user.role.value not in ["purchaser", "admin"]:
        raise HTTPException(status_code=403, detail="只有采购员可以创建辅材模板")

    service = PurchaseService(db)
    template = service.create_auxiliary_template(
        template_data=template_data,
        created_by=current_user.id
    )
    return template


# ========== 系统分类相关API ==========

@router.get("/system-categories/by-project/{project_id}")
async def get_system_categories_by_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    获取项目的所有系统分类
    用于申购表单的系统选择下拉框
    """
    from app.models.contract import SystemCategory, ContractFileVersion

    # 获取项目当前生效的版本
    current_version = db.query(ContractFileVersion).filter(
        and_(
            ContractFileVersion.project_id == project_id,
            ContractFileVersion.is_current == True
        )
    ).first()

    if not current_version:
        raise HTTPException(status_code=404, detail="项目未找到有效的合同清单版本")

    # 获取该版本的所有系统分类
    categories = db.query(SystemCategory).filter(
        SystemCategory.version_id == current_version.id
    ).all()

    return {
        "project_id": project_id,
        "version_id": current_version.id,
        "categories": [
            {
                "id": cat.id,
                "category_name": cat.category_name,
                "category_code": cat.category_code,
                "description": cat.description,
                "total_items_count": cat.total_items_count
            }
            for cat in categories
        ]
    }


@router.get("/system-categories/by-material")
async def get_system_categories_by_material(
    project_id: int = Query(..., description="项目ID"),
    material_name: str = Query(..., description="物料名称"),
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    根据物料名称获取可能的系统分类
    处理一个物料出现在多个系统的情况
    """
    from app.models.contract import SystemCategory, ContractFileVersion

    # 获取项目当前生效的版本
    current_version = db.query(ContractFileVersion).filter(
        and_(
            ContractFileVersion.project_id == project_id,
            ContractFileVersion.is_current == True
        )
    ).first()

    if not current_version:
        raise HTTPException(status_code=404, detail="项目未找到有效的合同清单版本")

    # 查找该物料名称在合同清单中的所有记录
    contract_items = db.query(ContractItem).filter(
        and_(
            ContractItem.version_id == current_version.id,
            ContractItem.item_name == material_name,
            ContractItem.is_active == True
        )
    ).all()

    if not contract_items:
        # 如果不是合同清单中的物料，返回所有可选系统（辅材情况）
        all_categories = db.query(SystemCategory).filter(
            SystemCategory.version_id == current_version.id
        ).all()

        return {
            "material_name": material_name,
            "is_contract_item": False,
            "message": "该物料不在合同清单中，可选择任意系统分类",
            "available_systems": [
                {
                    "id": cat.id,
                    "category_name": cat.category_name,
                    "category_code": cat.category_code,
                    "is_suggested": False
                }
                for cat in all_categories
            ]
        }

    # 获取该物料所属的系统分类
    category_ids = list(set([item.category_id for item in contract_items if item.category_id]))

    if not category_ids:
        # 物料存在但没有分类信息
        all_categories = db.query(SystemCategory).filter(
            SystemCategory.version_id == current_version.id
        ).all()

        return {
            "material_name": material_name,
            "is_contract_item": True,
            "message": "该物料在合同清单中但未分配系统分类",
            "available_systems": [
                {
                    "id": cat.id,
                    "category_name": cat.category_name,
                    "category_code": cat.category_code,
                    "is_suggested": False
                }
                for cat in all_categories
            ]
        }

    # 获取物料所属的系统分类信息
    categories = db.query(SystemCategory).filter(
        SystemCategory.id.in_(category_ids)
    ).all()

    # 如果物料属于多个系统，提供选择
    if len(categories) > 1:
        return {
            "material_name": material_name,
            "is_contract_item": True,
            "message": f"该物料出现在 {len(categories)} 个系统中，请选择适用的系统",
            "available_systems": [
                {
                    "id": cat.id,
                    "category_name": cat.category_name,
                    "category_code": cat.category_code,
                    "is_suggested": True,
                    "items_count": len([item for item in contract_items if item.category_id == cat.id])
                }
                for cat in categories
            ]
        }

    # 物料只属于一个系统，自动选择
    category = categories[0]
    return {
        "material_name": material_name,
        "is_contract_item": True,
        "auto_selected": True,
        "message": f"该物料属于 {category.category_name}",
        "selected_system": {
            "id": category.id,
            "category_name": category.category_name,
            "category_code": category.category_code,
            "items_count": len([item for item in contract_items if item.category_id == category.id])
        }
    }
