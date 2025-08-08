"""
采购请购API接口
"""

from typing import List, Optional, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from app.api import deps
from app.core.database import get_db
from app.models.purchase import (
    PurchaseRequest, PurchaseRequestItem, PurchaseApproval,
    Supplier, PurchaseStatus, ItemType, ApprovalStatus
)
from app.models.project import Project
from app.models.contract import ContractItem
from app.models.user import User
from app.schemas.purchase import (
    PurchaseRequestCreate, PurchaseRequestUpdate, PurchaseRequestInDB,
    PurchaseRequestWithItems, PurchaseRequestWithoutPrice,
    PurchaseRequestSubmit, PurchaseRequestQuote, PurchaseRequestApprove,
    PurchaseItemPriceQuote, SupplierCreate, SupplierUpdate, SupplierInDB,
    PurchaseRequestListResponse, SupplierListResponse,
    AuxiliaryTemplateCreate, AuxiliaryTemplateInDB
)
from app.services.purchase_service import PurchaseService

router = APIRouter()


# ========== 申购单管理 ==========

@router.get("/", response_model=PurchaseRequestListResponse)
async def get_purchase_requests(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    project_id: Optional[int] = None,
    status: Optional[PurchaseStatus] = None,
    requester_id: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    获取申购单列表
    - 项目经理只能看到自己的申购单，且不显示价格
    - 采购员、项目主管、总经理可以看到所有申购单和价格
    """
    query = db.query(PurchaseRequest)
    
    # 权限过滤
    if current_user.role == "project_manager":
        query = query.filter(PurchaseRequest.requester_id == current_user.id)
    
    # 条件过滤
    if project_id:
        query = query.filter(PurchaseRequest.project_id == project_id)
    if status:
        query = query.filter(PurchaseRequest.status == status)
    if requester_id:
        query = query.filter(PurchaseRequest.requester_id == requester_id)
    if search:
        query = query.filter(
            or_(
                PurchaseRequest.request_code.contains(search),
                PurchaseRequest.approval_notes.contains(search)
            )
        )
    
    # 分页
    total = query.count()
    items = query.offset((page - 1) * size).limit(size).all()
    
    # 根据角色返回不同的数据视图
    result_items = []
    for item in items:
        # 获取项目名称
        project = db.query(Project).filter(Project.id == item.project_id).first()
        project_name = project.project_name if project else None
        
        # 获取申请人名称
        requester = db.query(User).filter(User.id == item.requester_id).first()
        requester_name = requester.name if requester else "系统管理员"
        
        if current_user.role == "project_manager":
            # 项目经理看不到价格信息
            item_dict = PurchaseRequestWithoutPrice.from_orm(item).dict()
            item_dict['total_amount'] = None  # 隐藏总金额
            item_dict['project_name'] = project_name
            item_dict['requester_name'] = requester_name
            result_items.append(item_dict)
        else:
            item_dict = PurchaseRequestWithItems.from_orm(item).dict()
            item_dict['project_name'] = project_name
            item_dict['requester_name'] = requester_name
            result_items.append(item_dict)
    
    return {
        "items": result_items,
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size
    }


@router.get("/{request_id}", response_model=PurchaseRequestWithItems)
async def get_purchase_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """获取申购单详情"""
    request = db.query(PurchaseRequest).filter(PurchaseRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="申购单不存在")
    
    # 权限检查
    if current_user.role == "project_manager" and request.requester_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权查看此申购单")
    
    # 获取项目名称
    project = db.query(Project).filter(Project.id == request.project_id).first()
    project_name = project.project_name if project else None
    
    # 获取申请人名称
    requester = db.query(User).filter(User.id == request.requester_id).first()
    requester_name = requester.name if requester else "系统管理员"
    
    # 根据角色返回不同视图
    if current_user.role == "project_manager":
        result = PurchaseRequestWithoutPrice.from_orm(request).dict()
        result['project_name'] = project_name
        result['requester_name'] = requester_name
        return result
    else:
        result = PurchaseRequestWithItems.from_orm(request).dict()
        result['project_name'] = project_name
        result['requester_name'] = requester_name
        return result


@router.post("/", response_model=PurchaseRequestInDB)
async def create_purchase_request(
    request_data: PurchaseRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    创建申购单（项目经理）
    - 主材必须关联合同清单项并进行数量校验
    - 辅材可以自由添加
    """
    if current_user.role not in ["project_manager", "admin"]:
        raise HTTPException(status_code=403, detail="只有项目经理可以创建申购单")
    
    # 验证项目存在
    project = db.query(Project).filter(Project.id == request_data.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    # 创建申购单
    service = PurchaseService(db)
    try:
        purchase_request = service.create_purchase_request(
            request_data=request_data,
            requester_id=current_user.id
        )
        return purchase_request
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{request_id}", response_model=PurchaseRequestInDB)
async def update_purchase_request(
    request_id: int,
    update_data: PurchaseRequestUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """更新申购单（仅草稿状态）"""
    request = db.query(PurchaseRequest).filter(PurchaseRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="申购单不存在")
    
    # 权限检查
    if request.requester_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权修改此申购单")
    
    # 状态检查
    if request.status != PurchaseStatus.DRAFT:
        raise HTTPException(status_code=400, detail="只能修改草稿状态的申购单")
    
    # 更新数据
    for field, value in update_data.dict(exclude_unset=True).items():
        setattr(request, field, value)
    
    db.commit()
    db.refresh(request)
    return request


@router.post("/{request_id}/submit", response_model=PurchaseRequestInDB)
async def submit_purchase_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """提交申购单（项目经理）"""
    request = db.query(PurchaseRequest).filter(PurchaseRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="申购单不存在")
    
    # 权限检查
    if request.requester_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权提交此申购单")
    
    # 状态检查
    if request.status != PurchaseStatus.DRAFT:
        raise HTTPException(status_code=400, detail="只能提交草稿状态的申购单")
    
    # 验证申购项完整性
    if not request.items:
        raise HTTPException(status_code=400, detail="申购单必须包含至少一个申购项")
    
    # 主材数量校验
    service = PurchaseService(db)
    try:
        service.validate_main_material_quantities(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # 更新状态
    request.status = PurchaseStatus.SUBMITTED
    db.commit()
    db.refresh(request)
    
    # TODO: 发送通知给采购员
    
    return request


@router.post("/{request_id}/quote", response_model=PurchaseRequestInDB)
async def quote_purchase_request(
    request_id: int,
    quote_data: PurchaseRequestQuote,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    申购单询价（采购员）
    - 填写供应商信息和价格
    - 预计到货时间
    """
    if current_user.role not in ["purchaser", "admin"]:
        raise HTTPException(status_code=403, detail="只有采购员可以进行询价")
    
    request = db.query(PurchaseRequest).filter(PurchaseRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="申购单不存在")
    
    # 状态检查
    if request.status != PurchaseStatus.SUBMITTED:
        raise HTTPException(status_code=400, detail="只能对已提交的申购单进行询价")
    
    # 更新申购项价格信息
    total_amount = 0
    for item_quote in quote_data.items:
        item = db.query(PurchaseRequestItem).filter(
            and_(
                PurchaseRequestItem.id == item_quote.item_id,
                PurchaseRequestItem.request_id == request_id
            )
        ).first()
        
        if not item:
            raise HTTPException(status_code=404, detail=f"申购项 {item_quote.item_id} 不存在")
        
        # 更新价格和供应商信息
        item.unit_price = item_quote.unit_price
        item.total_price = item_quote.unit_price * item.quantity
        item.supplier_id = item_quote.supplier_id
        item.supplier_name = item_quote.supplier_name
        item.supplier_contact = item_quote.supplier_contact
        item.estimated_delivery = item_quote.estimated_delivery
        
        total_amount += item.total_price
    
    # 更新申购单总金额和状态
    request.total_amount = total_amount
    request.status = PurchaseStatus.PRICE_QUOTED
    
    db.commit()
    db.refresh(request)
    
    # TODO: 发送通知给项目主管审批
    
    return request


@router.post("/{request_id}/approve", response_model=PurchaseRequestInDB)
async def approve_purchase_request(
    request_id: int,
    approval_data: PurchaseRequestApprove,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    审批申购单
    - 项目主管：一级审批
    - 总经理：最终审批
    """
    request = db.query(PurchaseRequest).filter(PurchaseRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="申购单不存在")
    
    # 确定审批级别
    if current_user.role == "dept_manager":
        approval_level = 1
        next_status = PurchaseStatus.DEPT_APPROVED if approval_data.approval_status == ApprovalStatus.APPROVED else PurchaseStatus.REJECTED
    elif current_user.role in ["general_manager", "admin"]:
        approval_level = 2
        next_status = PurchaseStatus.FINAL_APPROVED if approval_data.approval_status == ApprovalStatus.APPROVED else PurchaseStatus.REJECTED
    else:
        raise HTTPException(status_code=403, detail="无审批权限")
    
    # 状态检查
    if approval_level == 1 and request.status != PurchaseStatus.PRICE_QUOTED:
        raise HTTPException(status_code=400, detail="申购单状态不正确")
    if approval_level == 2 and request.status != PurchaseStatus.DEPT_APPROVED:
        raise HTTPException(status_code=400, detail="申购单需要先经过部门审批")
    
    # 创建审批记录
    approval = PurchaseApproval(
        request_id=request_id,
        approver_id=current_user.id,
        approver_role=current_user.role,
        approval_level=approval_level,
        approval_status=approval_data.approval_status,
        approval_notes=approval_data.approval_notes,
        can_view_price=True  # 审批人可以看到价格
    )
    db.add(approval)
    
    # 更新申购单状态
    request.status = next_status
    request.approval_notes = approval_data.approval_notes
    
    db.commit()
    db.refresh(request)
    
    # TODO: 发送通知
    
    return request


@router.delete("/{request_id}")
async def delete_purchase_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """删除申购单（仅草稿状态）"""
    request = db.query(PurchaseRequest).filter(PurchaseRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="申购单不存在")
    
    # 权限检查
    if request.requester_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="无权删除此申购单")
    
    # 状态检查
    if request.status != PurchaseStatus.DRAFT:
        raise HTTPException(status_code=400, detail="只能删除草稿状态的申购单")
    
    db.delete(request)
    db.commit()
    
    return {"detail": "申购单已删除"}


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
    if current_user.role not in ["purchaser", "admin"]:
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
    if current_user.role not in ["purchaser", "admin"]:
        raise HTTPException(status_code=403, detail="只有采购员可以更新供应商")
    
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="供应商不存在")
    
    for field, value in update_data.dict(exclude_unset=True).items():
        setattr(supplier, field, value)
    
    db.commit()
    db.refresh(supplier)
    
    return supplier


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
    if current_user.role not in ["purchaser", "admin"]:
        raise HTTPException(status_code=403, detail="只有采购员可以创建辅材模板")
    
    service = PurchaseService(db)
    template = service.create_auxiliary_template(
        template_data=template_data,
        created_by=current_user.id
    )
    return template