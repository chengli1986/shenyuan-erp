"""
采购请购API接口
"""

from typing import List, Optional, Any
from datetime import datetime
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from app.api import deps
from app.core.database import get_db
from app.models.purchase import (
    PurchaseRequest, PurchaseRequestItem, PurchaseApproval,
    Supplier, PurchaseStatus, ItemType, ApprovalStatus,
    PurchaseWorkflowLog, WorkflowStep
)
from app.models.project import Project
from app.models.contract import ContractItem
from app.models.user import User, UserRole
from app.schemas.purchase import (
    PurchaseRequestCreate, PurchaseRequestUpdate, PurchaseRequestInDB,
    PurchaseRequestWithItems, PurchaseRequestWithoutPrice,
    PurchaseRequestSubmit, PurchaseRequestQuote, PurchaseRequestApprove,
    PurchaseRequestPriceQuote, PurchaseItemPriceQuote, 
    SupplierCreate, SupplierUpdate, SupplierInDB,
    PurchaseRequestListResponse, SupplierListResponse,
    AuxiliaryTemplateCreate, AuxiliaryTemplateInDB
)
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
    
    # 计算已申购数量（所有状态的申购单）
    purchased_quantity = db.query(func.sum(PurchaseRequestItem.quantity)).filter(
        PurchaseRequestItem.contract_item_id == item_id
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
        # 计算已申购数量
        purchased_quantity = db.query(func.sum(PurchaseRequestItem.quantity)).filter(
            PurchaseRequestItem.contract_item_id == item.id
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
    
    # 权限过滤 - 项目级权限控制
    if current_user.role.value == "project_manager":
        # 项目经理只能看到自己负责的项目的申购单
        # 通过项目经理姓名匹配来确定负责的项目
        managed_projects = db.query(Project.id).filter(
            Project.project_manager == current_user.name
        ).all()
        
        if managed_projects:
            managed_project_ids = [p.id for p in managed_projects]
            query = query.filter(PurchaseRequest.project_id.in_(managed_project_ids))
        else:
            # 如果没有负责的项目，返回空结果
            query = query.filter(PurchaseRequest.id == -1)  # 永远不匹配
    
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
        
        if current_user.role.value == "project_manager":
            # 项目经理看不到价格信息
            item_dict = PurchaseRequestWithoutPrice.from_orm(item).dict()
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
    
    # 权限检查 - 项目级权限控制
    if current_user.role.value == "project_manager":
        # 项目经理只能查看自己负责项目的申购单
        managed_projects = db.query(Project.id).filter(
            Project.project_manager == current_user.name
        ).all()
        
        if managed_projects:
            managed_project_ids = [p.id for p in managed_projects]
            if request.project_id not in managed_project_ids:
                raise HTTPException(status_code=403, detail="无权查看此申购单")
        else:
            # 如果没有负责的项目，拒绝访问
            raise HTTPException(status_code=403, detail="无权查看此申购单")
    
    # 获取项目名称
    project = db.query(Project).filter(Project.id == request.project_id).first()
    project_name = project.project_name if project else None
    
    # 获取申请人名称
    requester = db.query(User).filter(User.id == request.requester_id).first()
    requester_name = requester.name if requester else "系统管理员"
    
    # 根据角色返回不同视图
    if current_user.role.value == "project_manager":
        result = PurchaseRequestWithoutPrice.from_orm(request).dict()
        result['project_name'] = project_name
        result['requester_name'] = requester_name
    else:
        result = PurchaseRequestWithItems.from_orm(request).dict()
        result['project_name'] = project_name
        result['requester_name'] = requester_name
    
    # 为申购明细添加系统分类名称和剩余数量信息
    if 'items' in result and result['items']:
        from app.models.contract import SystemCategory, ContractItem
        for item in result['items']:
            # 添加系统分类名称
            if item.get('system_category_id'):
                category = db.query(SystemCategory).filter(
                    SystemCategory.id == item['system_category_id']
                ).first()
                item['system_category_name'] = category.category_name if category else None
            else:
                item['system_category_name'] = None
            
            # 为主材添加合同清单的剩余数量信息
            if item.get('item_type') == 'main' and item.get('contract_item_id'):
                contract_item = db.query(ContractItem).filter(
                    ContractItem.id == item['contract_item_id']
                ).first()
                if contract_item:
                    # 计算剩余数量：合同数量 - 已申购数量
                    from sqlalchemy import func
                    from app.models.purchase import PurchaseRequestItem, ItemType
                    
                    # 获取该合同清单项已申购的总数量
                    purchased_quantity = db.query(func.sum(PurchaseRequestItem.quantity)).filter(
                        PurchaseRequestItem.contract_item_id == contract_item.id,
                        PurchaseRequestItem.item_type == "main"
                    ).scalar() or 0
                    
                    # 计算剩余数量
                    remaining = float(contract_item.quantity) - float(purchased_quantity)
                    item['remaining_quantity'] = max(0, remaining)
                    item['max_quantity'] = float(contract_item.quantity)
    
    return result


@router.post("/", response_model=PurchaseRequestInDB)
async def create_purchase_request(
    request_data: PurchaseRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    创建申购单（项目经理、采购员）
    - 主材必须关联合同清单项并进行数量校验
    - 辅材可以自由添加
    """
    if current_user.role.value not in ["project_manager", "purchaser", "admin"]:
        raise HTTPException(status_code=403, detail="只有项目经理和采购员可以创建申购单")
    
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


@router.put("/{request_id}", response_model=PurchaseRequestWithItems)
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
    
    # 权限检查 - 支持项目经理编辑负责项目的申购单
    can_edit = False
    
    # 1. 申请人可以编辑自己的申购单
    if request.requester_id == current_user.id:
        can_edit = True
    
    # 2. 项目经理可以编辑负责项目的草稿申购单
    elif current_user.role.value == "project_manager":
        project = db.query(Project).filter(Project.id == request.project_id).first()
        if project and project.project_manager == current_user.name:
            can_edit = True
    
    # 3. 管理员可以编辑任何申购单
    elif current_user.role.value == "admin":
        can_edit = True
    
    if not can_edit:
        raise HTTPException(status_code=403, detail="无权修改此申购单")
    
    # 状态检查
    if request.status != PurchaseStatus.DRAFT:
        raise HTTPException(status_code=400, detail="只能修改草稿状态的申购单")
    
    # 更新基本信息
    update_dict = update_data.dict(exclude_unset=True, exclude={'items'})
    for field, value in update_dict.items():
        setattr(request, field, value)
    
    # 如果提供了items，更新申购明细
    if update_data.items is not None:
        # 删除现有的申购明细
        db.query(PurchaseRequestItem).filter(
            PurchaseRequestItem.request_id == request_id
        ).delete()
        
        # 添加新的申购明细
        for item_data in update_data.items:
            item = PurchaseRequestItem(
                request_id=request_id,
                contract_item_id=item_data.contract_item_id,
                system_category_id=item_data.system_category_id,
                item_name=item_data.item_name,
                specification=item_data.specification,
                brand=item_data.brand,
                unit=item_data.unit,
                quantity=item_data.quantity,
                unit_price=getattr(item_data, 'unit_price', None),
                total_price=getattr(item_data, 'total_price', None),
                item_type=item_data.item_type,
                remarks=item_data.remarks
            )
            db.add(item)
    
    # 重新计算总金额
    items = db.query(PurchaseRequestItem).filter(
        PurchaseRequestItem.request_id == request_id
    ).all()
    
    total_amount = sum(
        item.total_price or Decimal('0') for item in items
    )
    request.total_amount = total_amount if total_amount > 0 else None
    
    db.commit()
    db.refresh(request)
    
    # 返回完整的申购单信息
    return await get_purchase_request(request_id, db, current_user)


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
    
    # 权限检查 - 只有项目经理可以提交
    if current_user.role.value != "project_manager":
        raise HTTPException(status_code=403, detail="只有项目经理可以提交申购单")
    
    # 项目权限检查
    if current_user.role.value == "project_manager":
        managed_projects = db.query(Project.id).filter(
            Project.project_manager == current_user.name
        ).all()
        
        if managed_projects:
            managed_project_ids = [p.id for p in managed_projects]
            if request.project_id not in managed_project_ids:
                raise HTTPException(status_code=403, detail="无权提交此申购单")
        else:
            raise HTTPException(status_code=403, detail="无权提交此申购单")
    
    # 状态检查
    if request.status != PurchaseStatus.DRAFT:
        raise HTTPException(status_code=400, detail="只能提交草稿状态的申购单")
    
    # 工作流步骤检查
    if request.current_step != "project_manager":
        raise HTTPException(status_code=400, detail="当前步骤不允许提交操作")
    
    # 验证申购项完整性
    if not request.items:
        raise HTTPException(status_code=400, detail="申购单必须包含至少一个申购项")
    
    # 验证必填字段 - 检查所有申购明细是否都有系统分类
    for item in request.items:
        if not item.system_category_id:
            raise HTTPException(status_code=400, detail=f"申购明细'{item.item_name}'缺少所属系统信息，请在编辑页面选择系统分类")
    
    # 主材数量校验
    service = PurchaseService(db)
    try:
        service.validate_main_material_quantities(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # 查找采购员（下一步审批人）
    purchaser = db.query(User).filter(User.role == UserRole.PURCHASER).first()
    if not purchaser:
        raise HTTPException(status_code=500, detail="系统中未找到采购员角色")
    
    # 更新申购单状态和工作流
    request.status = PurchaseStatus.SUBMITTED
    request.current_step = "purchaser"
    request.current_approver_id = purchaser.id
    
    # 记录工作流操作
    workflow_log = PurchaseWorkflowLog(
        request_id=request_id,
        from_step="project_manager",
        to_step="purchaser",
        operation="submit",
        operator_id=current_user.id,
        operator_role=current_user.role.value,
        operation_notes=f"项目经理 {current_user.name} 提交申购单"
    )
    db.add(workflow_log)
    
    db.commit()
    db.refresh(request)
    
    # TODO: 发送通知给采购员
    
    return request


@router.post("/{request_id}/quote", response_model=PurchaseRequestInDB)
async def quote_purchase_request(
    request_id: int,
    quote_data: PurchaseRequestPriceQuote,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    申购单询价（采购员）
    - 填写供应商信息和价格
    - 预计到货时间和付款方式
    """
    if current_user.role.value not in ["purchaser", "admin"]:
        raise HTTPException(status_code=403, detail="只有采购员可以进行询价")
    
    request = db.query(PurchaseRequest).filter(PurchaseRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="申购单不存在")
    
    # 状态检查
    if request.status != PurchaseStatus.SUBMITTED:
        raise HTTPException(status_code=400, detail="只能对已提交的申购单进行询价")
    
    # 工作流步骤检查
    if request.current_step != "purchaser":
        raise HTTPException(status_code=400, detail="当前步骤不允许询价操作")
    
    # 权限检查：是否为当前审批人
    if request.current_approver_id and request.current_approver_id != current_user.id:
        raise HTTPException(status_code=403, detail="非当前指定审批人，无权操作")
    
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
        
        # 更新supplier_info JSON字段来存储新的信息
        supplier_info = item.supplier_info or {}
        if item_quote.supplier_contact_person:
            supplier_info['contact_person'] = item_quote.supplier_contact_person
        if item_quote.payment_method:
            supplier_info['payment_method'] = item_quote.payment_method.value if hasattr(item_quote.payment_method, 'value') else item_quote.payment_method
        item.supplier_info = supplier_info
        
        total_amount += item.total_price
    
    # 查找部门主管（下一步审批人）
    dept_manager = db.query(User).filter(User.role == UserRole.DEPT_MANAGER).first()
    if not dept_manager:
        raise HTTPException(status_code=500, detail="系统中未找到部门主管角色")
    
    # 更新申购单信息
    request.total_amount = total_amount
    request.status = PurchaseStatus.PRICE_QUOTED
    # payment_method和estimated_delivery_date已移动到物料级别，这里不再设置
    request.current_step = "dept_manager"
    request.current_approver_id = dept_manager.id
    
    # 记录工作流操作
    workflow_log = PurchaseWorkflowLog(
        request_id=request_id,
        from_step="purchaser",
        to_step="dept_manager",
        operation="quote",
        operator_id=current_user.id,
        operator_role=current_user.role.value,
        operation_notes=f"采购员 {current_user.name} 完成询价，总金额: {total_amount}",
        operation_data={
            "total_amount": float(total_amount),
            "quote_notes": quote_data.quote_notes,
            "items_count": len(quote_data.items)
        }
    )
    db.add(workflow_log)
    
    db.commit()
    db.refresh(request)
    
    # TODO: 发送通知给部门主管审批
    
    return request


@router.post("/{request_id}/return", response_model=PurchaseRequestInDB)
async def return_purchase_request(
    request_id: int,
    return_data: PurchaseRequestApprove,  # 复用审批结构，但只用notes字段
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    退回申购单
    - 采购员退回：submitted状态 -> draft状态，回到project_manager
    - 项目经理退回：price_quoted状态 -> submitted状态，回到purchaser
    - 退回原因必填
    """
    if current_user.role.value not in ["purchaser", "project_manager", "admin"]:
        raise HTTPException(status_code=403, detail="只有采购员和项目经理可以退回申购单")
    
    request = db.query(PurchaseRequest).filter(PurchaseRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="申购单不存在")
    
    # 退回原因必填
    if not return_data.approval_notes:
        raise HTTPException(status_code=400, detail="退回原因不能为空")
    
    # 根据当前用户角色和申购单状态决定退回逻辑
    if current_user.role.value == "purchaser":
        # 采购员退回逻辑
        if request.status != PurchaseStatus.SUBMITTED:
            raise HTTPException(status_code=400, detail="只能退回已提交的申购单")
        if request.current_step != "purchaser":
            raise HTTPException(status_code=400, detail="当前步骤不允许退回操作")
        
        # 查找原申请人（项目经理）
        requester = db.query(User).filter(User.id == request.requester_id).first()
        if not requester:
            raise HTTPException(status_code=500, detail="未找到原申请人")
        
        # 更新申购单状态
        request.status = PurchaseStatus.DRAFT
        request.current_step = "project_manager"
        request.current_approver_id = request.requester_id
        
        from_step = WorkflowStep.PURCHASER
        to_step = WorkflowStep.PROJECT_MANAGER
        operation_notes = f"采购员 {current_user.name} 退回申购单：{return_data.approval_notes}"
        returned_to = requester.name
        
    elif current_user.role.value == "project_manager":
        # 项目经理退回逻辑
        if request.status != PurchaseStatus.PRICE_QUOTED:
            raise HTTPException(status_code=400, detail="只能退回已询价的申购单")
        if request.current_step != "dept_manager":
            raise HTTPException(status_code=400, detail="当前步骤不允许退回操作")
        
        # 项目级权限检查：只能退回自己负责项目的申购单
        from app.models.project import Project
        project = db.query(Project).filter(Project.id == request.project_id).first()
        if not project or project.project_manager != current_user.name:
            raise HTTPException(status_code=403, detail="只能退回自己负责项目的申购单")
        
        # 查找采购员
        purchaser = db.query(User).filter(User.role == UserRole.PURCHASER).first()
        if not purchaser:
            raise HTTPException(status_code=500, detail="未找到采购员")
        
        # 更新申购单状态
        request.status = PurchaseStatus.SUBMITTED
        request.current_step = "purchaser"
        request.current_approver_id = purchaser.id
        
        from_step = WorkflowStep.DEPT_MANAGER
        to_step = WorkflowStep.PURCHASER
        operation_notes = f"项目经理 {current_user.name} 退回申购单：{return_data.approval_notes}"
        returned_to = purchaser.name
    
    request.approval_notes = return_data.approval_notes
    
    # 记录工作流操作
    workflow_log = PurchaseWorkflowLog(
        request_id=request_id,
        from_step=from_step,
        to_step=to_step,
        operation="return",
        operator_id=current_user.id,
        operator_role=current_user.role.value,
        operation_notes=operation_notes,
        operation_data={
            "return_reason": return_data.approval_notes,
            "returned_to": returned_to
        }
    )
    db.add(workflow_log)
    
    db.commit()
    db.refresh(request)
    
    # TODO: 发送通知给项目经理
    
    return request


@router.post("/{request_id}/dept-approve", response_model=PurchaseRequestInDB)
async def dept_approve_purchase_request(
    request_id: int,
    approval_data: PurchaseRequestApprove,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    部门主管审批申购单
    - 技术审查和预算控制
    """
    if current_user.role.value not in ["dept_manager", "admin"]:
        raise HTTPException(status_code=403, detail="只有部门主管可以进行部门审批")
    
    request = db.query(PurchaseRequest).filter(PurchaseRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="申购单不存在")
    
    # 状态检查
    if request.status != PurchaseStatus.PRICE_QUOTED:
        raise HTTPException(status_code=400, detail="只能对已询价的申购单进行审批")
    
    # 工作流步骤检查
    if request.current_step != "dept_manager":
        raise HTTPException(status_code=400, detail="当前步骤不允许部门审批操作")
    
    # 权限检查：是否为当前审批人
    if request.current_approver_id and request.current_approver_id != current_user.id:
        raise HTTPException(status_code=403, detail="非当前指定审批人，无权操作")
    
    # 处理审批结果
    if approval_data.approval_status.value == ApprovalStatus.APPROVED.value:
        # 查找总经理（下一步审批人）
        general_manager = db.query(User).filter(User.role == UserRole.GENERAL_MANAGER).first()
        if not general_manager:
            raise HTTPException(status_code=500, detail="系统中未找到总经理角色")
        
        # 更新申购单状态和工作流
        request.status = PurchaseStatus.DEPT_APPROVED
        request.current_step = "general_manager"
        request.current_approver_id = general_manager.id
        operation = "approve"
        to_step = "general_manager"
        
    elif approval_data.approval_status.value == ApprovalStatus.REJECTED.value:
        # 拒绝：重置到采购员步骤重新询价
        purchaser = db.query(User).filter(User.role == UserRole.PURCHASER).first()
        request.status = PurchaseStatus.SUBMITTED
        request.current_step = "purchaser"
        request.current_approver_id = purchaser.id if purchaser else None
        operation = "reject"
        to_step = "purchaser"
    else:
        raise HTTPException(status_code=400, detail=f"无效的审批状态: {approval_data.approval_status.value}")
    
    # 更新审批意见
    request.approval_notes = approval_data.approval_notes
    
    # 创建审批记录
    approval = PurchaseApproval(
        request_id=request_id,
        approver_id=current_user.id,
        approver_role=current_user.role.value,
        approval_level=1,  # 部门审批为第一级
        approval_status=approval_data.approval_status,
        approval_notes=approval_data.approval_notes,
        can_view_price=True
    )
    db.add(approval)
    
    # 记录工作流操作
    workflow_log = PurchaseWorkflowLog(
        request_id=request_id,
        from_step="dept_manager",
        to_step=to_step,
        operation=operation,
        operator_id=current_user.id,
        operator_role=current_user.role.value,
        operation_notes=f"部门主管 {current_user.name} {operation}申购单：{approval_data.approval_notes or '无备注'}"
    )
    db.add(workflow_log)
    
    db.commit()
    db.refresh(request)
    
    # TODO: 发送通知给下一步审批人
    
    return request


@router.post("/{request_id}/final-approve", response_model=PurchaseRequestInDB)
async def final_approve_purchase_request(
    request_id: int,
    approval_data: PurchaseRequestApprove,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    总经理最终审批申购单
    - 最终决策和预算批准
    """
    if current_user.role.value not in ["general_manager", "admin"]:
        raise HTTPException(status_code=403, detail="只有总经理可以进行最终审批")
    
    request = db.query(PurchaseRequest).filter(PurchaseRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="申购单不存在")
    
    # 状态检查
    if request.status != PurchaseStatus.DEPT_APPROVED:
        raise HTTPException(status_code=400, detail="只能对部门已审批的申购单进行最终审批")
    
    # 工作流步骤检查
    if request.current_step != "general_manager":
        raise HTTPException(status_code=400, detail="当前步骤不允许最终审批操作")
    
    # 权限检查：是否为当前审批人
    if request.current_approver_id and request.current_approver_id != current_user.id:
        raise HTTPException(status_code=403, detail="非当前指定审批人，无权操作")
    
    # 处理审批结果
    if approval_data.approval_status.value == ApprovalStatus.APPROVED.value:
        # 最终批准：完成工作流
        request.status = PurchaseStatus.FINAL_APPROVED
        request.current_step = "completed"
        request.current_approver_id = None
        operation = "final_approve"
        to_step = "completed"
        
    elif approval_data.approval_status.value == ApprovalStatus.REJECTED.value:
        # 拒绝：重置到部门主管步骤重新审批
        dept_manager = db.query(User).filter(User.role == UserRole.DEPT_MANAGER).first()
        request.status = PurchaseStatus.PRICE_QUOTED
        request.current_step = "dept_manager"
        request.current_approver_id = dept_manager.id if dept_manager else None
        operation = "reject"
        to_step = "dept_manager"
    else:
        raise HTTPException(status_code=400, detail=f"无效的审批状态: {approval_data.approval_status.value}")
    
    # 更新审批意见
    request.approval_notes = approval_data.approval_notes
    
    # 创建审批记录
    approval = PurchaseApproval(
        request_id=request_id,
        approver_id=current_user.id,
        approver_role=current_user.role.value,
        approval_level=2,  # 总经理审批为第二级
        approval_status=approval_data.approval_status,
        approval_notes=approval_data.approval_notes,
        can_view_price=True
    )
    db.add(approval)
    
    # 记录工作流操作
    workflow_log = PurchaseWorkflowLog(
        request_id=request_id,
        from_step="general_manager",
        to_step=to_step,
        operation=operation,
        operator_id=current_user.id,
        operator_role=current_user.role.value,
        operation_notes=f"总经理 {current_user.name} {operation}申购单：{approval_data.approval_notes or '无备注'}"
    )
    db.add(workflow_log)
    
    db.commit()
    db.refresh(request)
    
    # TODO: 发送完成通知给相关人员
    # TODO: 如果最终批准，准备PDF生成
    
    return request


# 保留原有通用审批API作为兼容性接口
@router.post("/{request_id}/approve", response_model=PurchaseRequestInDB)
async def approve_purchase_request(
    request_id: int,
    approval_data: PurchaseRequestApprove,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    通用审批接口（兼容性保留）
    根据用户角色自动路由到对应审批流程
    """
    if current_user.role.value == "dept_manager":
        return await dept_approve_purchase_request(request_id, approval_data, db, current_user)
    elif current_user.role.value in ["general_manager", "admin"]:
        return await final_approve_purchase_request(request_id, approval_data, db, current_user)
    else:
        raise HTTPException(status_code=403, detail="无审批权限")


@router.get("/{request_id}/workflow-logs")
async def get_purchase_workflow_logs(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    获取申购单工作流操作历史
    """
    # 检查申购单是否存在
    request = db.query(PurchaseRequest).filter(PurchaseRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="申购单不存在")
    
    # 项目权限检查
    if current_user.role.value == "project_manager":
        managed_projects = db.query(Project.id).filter(
            Project.project_manager == current_user.name
        ).all()
        
        if managed_projects:
            managed_project_ids = [p.id for p in managed_projects]
            if request.project_id not in managed_project_ids:
                raise HTTPException(status_code=403, detail="无权查看此申购单的工作流历史")
        else:
            raise HTTPException(status_code=403, detail="无权查看此申购单的工作流历史")
    
    # 查询工作流日志
    logs = db.query(PurchaseWorkflowLog).filter(
        PurchaseWorkflowLog.request_id == request_id
    ).order_by(PurchaseWorkflowLog.created_at.asc()).all()
    
    # 获取操作人信息
    result_logs = []
    for log in logs:
        operator = db.query(User).filter(User.id == log.operator_id).first()
        operator_name = operator.name if operator else "未知用户"
        
        result_logs.append({
            "id": log.id,
            "from_step": log.from_step.value if log.from_step else None,
            "to_step": log.to_step.value,
            "operation": log.operation,
            "operator_id": log.operator_id,
            "operator_name": operator_name,
            "operator_role": log.operator_role,
            "operation_notes": log.operation_notes,
            "operation_data": log.operation_data,
            "created_at": log.created_at.isoformat()
        })
    
    return {
        "request_id": request_id,
        "request_code": request.request_code,
        "current_step": request.current_step,
        "current_status": request.status.value,
        "total_logs": len(result_logs),
        "logs": result_logs
    }


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
    
    # 权限检查 - 扩展项目经理和采购员权限
    can_delete = False
    
    # 1. 申购单创建者可以删除
    if request.requester_id == current_user.id:
        can_delete = True
    
    # 2. 管理员可以删除任何申购单
    elif current_user.role.value == "admin":
        can_delete = True
    
    # 3. 项目经理可以删除其负责项目的草稿申购单
    elif current_user.role.value == "project_manager":
        # 查询项目信息确认项目经理权限
        # 避免lazy loading问题，只查询需要的字段
        project_result = db.query(Project.project_manager).filter(Project.id == request.project_id).first()
        if project_result and project_result[0] == current_user.name:
            can_delete = True
    
    # 4. 采购员可以删除任何草稿申购单（采购员需要管理所有申购单）
    elif current_user.role.value == "purchaser":
        can_delete = True
    
    if not can_delete:
        raise HTTPException(status_code=403, detail="无权删除此申购单")
    
    # 状态检查
    if request.status != PurchaseStatus.DRAFT:
        raise HTTPException(status_code=400, detail="只能删除草稿状态的申购单")
    
    # 先删除相关的申购明细项（避免外键约束）
    db.query(PurchaseRequestItem).filter(PurchaseRequestItem.request_id == request_id).delete()
    
    # 删除相关的工作流日志（避免外键约束）
    db.query(PurchaseWorkflowLog).filter(PurchaseWorkflowLog.request_id == request_id).delete()
    
    # 删除相关的审批记录（如果有）
    db.query(PurchaseApproval).filter(PurchaseApproval.request_id == request_id).delete()
    
    # 最后删除申购单主记录
    db.delete(request)
    db.commit()
    
    return {"detail": "申购单已删除"}


@router.post("/batch-delete")
async def batch_delete_purchase_requests(
    request_ids: List[int],
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """批量删除申购单（仅草稿状态）"""
    if not request_ids:
        raise HTTPException(status_code=400, detail="请提供要删除的申购单ID列表")
    
    if len(request_ids) > 100:
        raise HTTPException(status_code=400, detail="单次最多删除100条申购单")
    
    # 查询所有要删除的申购单
    requests = db.query(PurchaseRequest).filter(
        PurchaseRequest.id.in_(request_ids)
    ).all()
    
    if not requests:
        raise HTTPException(status_code=404, detail="没有找到要删除的申购单")
    
    deleted_count = 0
    failed_requests = []
    
    for request in requests:
        try:
            # 权限检查 - 扩展项目经理权限
            can_delete = False
            
            # 1. 申购单创建者可以删除
            if request.requester_id == current_user.id:
                can_delete = True
            
            # 2. 管理员可以删除任何申购单
            elif current_user.role.value == "admin":
                can_delete = True
            
            # 3. 项目经理可以删除其负责项目的草稿申购单
            elif current_user.role.value == "project_manager":
                # 查询项目信息确认项目经理权限
                project = db.query(Project).filter(Project.id == request.project_id).first()
                if project and project.project_manager == current_user.name:
                    can_delete = True
            
            # 4. 采购员可以删除任何草稿申购单（采购员需要管理所有申购单）
            elif current_user.role.value == "purchaser":
                can_delete = True
            
            if not can_delete:
                failed_requests.append({
                    "id": request.id,
                    "request_code": request.request_code,
                    "reason": "无权删除此申购单"
                })
                continue
            
            # 状态检查
            if request.status != PurchaseStatus.DRAFT:
                failed_requests.append({
                    "id": request.id,
                    "request_code": request.request_code,
                    "reason": "只能删除草稿状态的申购单"
                })
                continue
            
            # 删除申购单（数据库会自动删除关联的items）
            db.delete(request)
            deleted_count += 1
            
        except Exception as e:
            failed_requests.append({
                "id": request.id,
                "request_code": request.request_code,
                "reason": f"删除失败: {str(e)}"
            })
    
    db.commit()
    
    return {
        "detail": f"批量删除完成",
        "deleted_count": deleted_count,
        "total_requested": len(request_ids),
        "failed_requests": failed_requests
    }


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