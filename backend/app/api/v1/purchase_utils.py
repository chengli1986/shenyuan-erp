"""
采购请购模块 - 共享工具函数
提供权限检查、数据转换等通用功能
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from app.models.purchase import (
    PurchaseRequest, PurchaseRequestItem, PurchaseStatus
)
from app.models.project import Project
from app.models.user import User


def get_managed_project_ids(db: Session, current_user: User) -> Optional[List[int]]:
    """
    获取项目经理负责的项目ID列表
    返回None表示用户不是项目经理（无需过滤）
    返回空列表表示项目经理没有负责任何项目
    """
    if current_user.role.value != "project_manager":
        return None

    # Fall back to name-based matching when project_manager_id is NULL
    # (handles rows created before the FK column was backfilled)
    # TODO: TEMPORARY FALLBACK — remove the name-based branch once all
    # Project rows have been backfilled with a valid project_manager_id FK.
    # Name-based matching is fragile: duplicate display names would let a
    # project manager see/manage projects they don't own.
    managed_projects = db.query(Project.id).filter(
        or_(
            Project.project_manager_id == current_user.id,
            Project.project_manager == current_user.name
        )
    ).all()

    if managed_projects:
        return [p.id for p in managed_projects]
    else:
        return []


def check_project_manager_access(db: Session, current_user: User, project_id: int) -> bool:
    """
    检查项目经理是否有权访问指定项目
    非项目经理角色默认返回True
    """
    if current_user.role.value != "project_manager":
        return True

    managed_ids = get_managed_project_ids(db, current_user)
    if managed_ids is None:
        return True
    return project_id in managed_ids


def enrich_purchase_item_details(db: Session, result: dict):
    """
    为申购明细添加系统分类名称和剩余数量信息
    直接修改传入的result字典
    使用批量查询避免N+1问题
    """
    if 'items' not in result or not result['items']:
        return

    from app.models.contract import SystemCategory, ContractItem

    # 批量获取所有需要的系统分类
    category_ids = list({
        item['system_category_id'] for item in result['items']
        if item.get('system_category_id')
    })
    category_map = {}
    if category_ids:
        categories = db.query(SystemCategory).filter(
            SystemCategory.id.in_(category_ids)
        ).all()
        category_map = {c.id: c.category_name for c in categories}

    # 批量获取所有需要的合同清单项
    contract_item_ids = list({
        item['contract_item_id'] for item in result['items']
        if item.get('item_type') == 'main' and item.get('contract_item_id')
    })
    contract_item_map = {}
    if contract_item_ids:
        contract_items = db.query(ContractItem).filter(
            ContractItem.id.in_(contract_item_ids)
        ).all()
        contract_item_map = {ci.id: ci for ci in contract_items}

    # 批量获取已申购数量（按contract_item_id分组）
    # NOTE: This intentionally sums ALL approved/completed purchases globally for each
    # contract_item_id, matching the original per-item loop behavior. The current purchase
    # request's own items are included in the sum because the remaining quantity should
    # reflect the total already committed against the contract line item.
    purchased_qty_map = {}
    if contract_item_ids:
        purchased_rows = db.query(
            PurchaseRequestItem.contract_item_id,
            func.sum(PurchaseRequestItem.quantity)
        ).join(
            PurchaseRequest
        ).filter(
            PurchaseRequestItem.contract_item_id.in_(contract_item_ids),
            PurchaseRequestItem.item_type == "main",
            PurchaseRequest.status.in_([PurchaseStatus.FINAL_APPROVED, PurchaseStatus.COMPLETED])
        ).group_by(
            PurchaseRequestItem.contract_item_id
        ).all()
        purchased_qty_map = {row[0]: row[1] or 0 for row in purchased_rows}

    for item in result['items']:
        # 添加系统分类名称
        if item.get('system_category_id'):
            item['system_category_name'] = category_map.get(item['system_category_id'])
        else:
            item['system_category_name'] = None

        # 为主材添加合同清单的剩余数量信息
        if item.get('item_type') == 'main' and item.get('contract_item_id'):
            contract_item = contract_item_map.get(item['contract_item_id'])
            if contract_item:
                purchased_quantity = purchased_qty_map.get(contract_item.id, 0)
                remaining = float(contract_item.quantity) - float(purchased_quantity)
                item['remaining_quantity'] = max(0, remaining)
                item['max_quantity'] = float(contract_item.quantity)


def get_project_and_requester_names(db: Session, purchase_request: PurchaseRequest):
    """
    获取申购单关联的项目名称和申请人名称
    返回 (project_name, requester_name) 元组
    """
    project = db.query(Project).filter(Project.id == purchase_request.project_id).first()
    project_name = project.project_name if project else None

    requester = db.query(User).filter(User.id == purchase_request.requester_id).first()
    requester_name = requester.name if requester else "系统管理员"

    return project_name, requester_name
