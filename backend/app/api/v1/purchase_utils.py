"""
采购请购模块 - 共享工具函数
提供权限检查、数据转换等通用功能
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

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

    managed_projects = db.query(Project.id).filter(
        Project.project_manager == current_user.name
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
    """
    if 'items' not in result or not result['items']:
        return

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
                # 获取该合同清单项已申购的总数量（只统计总经理已批准和已完成的申购单）
                purchased_quantity = db.query(func.sum(PurchaseRequestItem.quantity)).join(
                    PurchaseRequest
                ).filter(
                    PurchaseRequestItem.contract_item_id == contract_item.id,
                    PurchaseRequestItem.item_type == "main",
                    PurchaseRequest.status.in_([PurchaseStatus.FINAL_APPROVED, PurchaseStatus.COMPLETED])
                ).scalar() or 0

                # 计算剩余数量
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
