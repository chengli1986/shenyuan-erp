"""
采购请购API接口 - CRUD操作
"""

from typing import List, Optional
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.api import deps
from app.core.database import get_db
from app.models.purchase import (
    PurchaseRequest, PurchaseRequestItem, PurchaseApproval,
    PurchaseStatus, PurchaseWorkflowLog
)
from app.models.project import Project
from app.models.user import User
from app.schemas.purchase import (
    PurchaseRequestCreate, PurchaseRequestUpdate, PurchaseRequestInDB,
    PurchaseRequestWithItems, PurchaseRequestWithoutPrice,
    PurchaseRequestListResponse
)
from app.services.purchase_service import PurchaseService
from app.api.v1.purchase_utils import (
    get_managed_project_ids,
    check_project_manager_access,
    enrich_purchase_item_details,
    get_project_and_requester_names
)

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

    # 权限过滤 - 项目级权限控制
    managed_ids = get_managed_project_ids(db, current_user)
    if managed_ids is not None:
        if managed_ids:
            query = query.filter(PurchaseRequest.project_id.in_(managed_ids))
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
        # 获取项目名称和申请人名称
        project_name, requester_name = get_project_and_requester_names(db, item)

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
    if not check_project_manager_access(db, current_user, request.project_id):
        raise HTTPException(status_code=403, detail="无权查看此申购单")

    # 获取项目名称和申请人名称
    project_name, requester_name = get_project_and_requester_names(db, request)

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
    enrich_purchase_item_details(db, result)

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


# ========== 申购单删除 ==========

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
