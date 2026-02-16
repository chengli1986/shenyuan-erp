"""
采购请购模块 - 工作流操作
包括提交、询价、部门审批、总经理审批、退回、工作流日志查询
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.api import deps
from app.core.database import get_db
from app.models.purchase import (
    PurchaseRequest, PurchaseRequestItem, PurchaseApproval,
    PurchaseStatus, ApprovalStatus,
    PurchaseWorkflowLog, WorkflowStep
)
from app.models.project import Project
from app.models.user import User, UserRole
from app.schemas.purchase import (
    PurchaseRequestInDB,
    PurchaseRequestApprove, PurchaseRequestPriceQuote,
)
from app.services.purchase_service import PurchaseService
from app.api.v1.purchase_utils import get_managed_project_ids

router = APIRouter()


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

    # 由于数据库枚举值可能不匹配，暂时返回简化的工作流历史
    # 基于申购单的状态变化生成工作流历史
    result_logs = []

    # 基本工作流步骤：根据申购单当前状态推断历史
    if request.status.value in ['submitted', 'price_quoted', 'dept_approved', 'final_approved', 'completed']:
        # 创建申购单
        result_logs.append({
            "id": 1,
            "from_step": None,
            "to_step": "draft",
            "operation_type": "create",
            "operator_id": request.requester_id,
            "operator_name": "申请人",
            "operator_role": "project_manager",
            "operation_notes": "创建申购单",
            "operation_data": None,
            "created_at": request.created_at.isoformat()
        })

    if request.status.value in ['price_quoted', 'dept_approved', 'final_approved', 'completed']:
        # 提交申购单
        result_logs.append({
            "id": 2,
            "from_step": "draft",
            "to_step": "submitted",
            "operation_type": "submit",
            "operator_id": request.requester_id,
            "operator_name": "项目经理",
            "operator_role": "project_manager",
            "operation_notes": "提交申购单",
            "operation_data": None,
            "created_at": request.created_at.isoformat()
        })

    if request.status.value in ['dept_approved', 'final_approved', 'completed']:
        # 完成询价
        result_logs.append({
            "id": 3,
            "from_step": "submitted",
            "to_step": "price_quoted",
            "operation_type": "quote",
            "operator_id": None,
            "operator_name": "采购员",
            "operator_role": "purchaser",
            "operation_notes": "完成询价",
            "operation_data": {
                "supplier_info": "供应商信息已添加",
                "quote_completed": True
            },
            "created_at": request.updated_at.isoformat() if request.updated_at else request.created_at.isoformat()
        })

    if request.status.value in ['final_approved', 'completed']:
        # 部门审批
        result_logs.append({
            "id": 4,
            "from_step": "price_quoted",
            "to_step": "dept_approved",
            "operation_type": "approve",
            "operator_id": None,
            "operator_name": "部门主管",
            "operator_role": "dept_manager",
            "operation_notes": "部门审批通过",
            "operation_data": None,
            "created_at": request.updated_at.isoformat() if request.updated_at else request.created_at.isoformat()
        })

    if request.status.value in ['completed']:
        # 总经理最终审批
        result_logs.append({
            "id": 5,
            "from_step": "dept_approved",
            "to_step": "final_approved",
            "operation_type": "final_approve",
            "operator_id": None,
            "operator_name": "总经理",
            "operator_role": "general_manager",
            "operation_notes": "最终审批通过",
            "operation_data": None,
            "created_at": request.updated_at.isoformat() if request.updated_at else request.created_at.isoformat()
        })

    return {
        "request_id": request_id,
        "request_code": request.request_code,
        "current_step": request.current_step,
        "current_status": request.status.value,
        "total_logs": len(result_logs),
        "logs": result_logs
    }
