"""
初始化角色权限配置
根据v62开发文档的用户角色定义创建权限配置
"""

import logging

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models import RolePermission, PermissionCategory, User
from app.models.user import UserRole
from app.core.security import get_password_hash

logger = logging.getLogger(__name__)


def create_permission_categories(db: Session):
    """创建权限分类"""
    categories = [
        {"name": "项目管理", "code": "project", "description": "项目创建、编辑、查看权限"},
        {"name": "申购管理", "code": "purchase", "description": "申购单创建、审批权限"},
        {"name": "库存管理", "code": "inventory", "description": "库存操作、查询权限"},
        {"name": "合同管理", "code": "contract", "description": "合同清单管理权限"},
        {"name": "财务管理", "code": "finance", "description": "财务数据查看权限"},
        {"name": "用户管理", "code": "user", "description": "用户账号管理权限"},
        {"name": "系统管理", "code": "system", "description": "系统配置管理权限"},
    ]
    
    for cat_data in categories:
        existing = db.query(PermissionCategory).filter(
            PermissionCategory.category_code == cat_data["code"]
        ).first()
        
        if not existing:
            category = PermissionCategory(
                category_name=cat_data["name"],
                category_code=cat_data["code"],
                description=cat_data["description"]
            )
            db.add(category)
    
    db.commit()


def create_role_permissions(db: Session):
    """根据v62文档创建角色权限配置"""
    
    # 权限定义
    permissions = [
        # 项目管理相关权限
        {"code": "view_all_projects", "name": "查看所有项目", "desc": "可以查看系统中的所有项目"},
        {"code": "view_own_projects", "name": "查看自己的项目", "desc": "只能查看自己负责的项目"},
        {"code": "create_project", "name": "创建项目", "desc": "创建新项目"},
        {"code": "edit_project", "name": "编辑项目", "desc": "编辑项目信息"},
        {"code": "manage_project_files", "name": "项目文件管理", "desc": "上传和管理项目文件"},
        
        # 申购管理相关权限
        {"code": "create_purchase", "name": "创建申购单", "desc": "创建申购单"},
        {"code": "view_own_purchase", "name": "查看自己的申购单", "desc": "查看自己创建的申购单"},
        {"code": "view_all_purchase", "name": "查看所有申购单", "desc": "查看系统中所有申购单"},
        {"code": "approve_purchase", "name": "审批申购单", "desc": "审批申购单"},
        {"code": "final_approve", "name": "最终审批", "desc": "申购单最终审批权限"},
        {"code": "quote_price", "name": "询价录入", "desc": "录入供应商报价信息"},
        
        # 价格信息相关权限
        {"code": "view_price", "name": "查看价格信息", "desc": "查看价格敏感信息"},
        {"code": "view_cost", "name": "查看成本信息", "desc": "查看成本相关信息"},
        {"code": "view_profit", "name": "查看利润信息", "desc": "查看利润信息"},
        
        # 库存管理相关权限
        {"code": "view_inventory", "name": "查看库存", "desc": "查看库存信息"},
        {"code": "manage_inventory", "name": "库存管理", "desc": "库存数据管理"},
        {"code": "inbound", "name": "入库操作", "desc": "执行入库操作"},
        {"code": "outbound", "name": "出库操作", "desc": "执行出库操作"},
        {"code": "approve_outbound", "name": "出库审批", "desc": "审批出库申请"},
        
        # 合同清单相关权限
        {"code": "upload_contract", "name": "上传合同清单", "desc": "上传合同清单文件"},
        {"code": "manage_contract", "name": "合同清单管理", "desc": "管理合同清单版本"},
        {"code": "approve_contract_change", "name": "合同变更审批", "desc": "审批合同清单变更"},
        
        # 供应商管理相关权限
        {"code": "manage_suppliers", "name": "供应商管理", "desc": "供应商信息维护"},
        {"code": "optimize_suppliers", "name": "供应商优化", "desc": "优化供应商选择"},
        
        # 财务相关权限
        {"code": "view_finance", "name": "财务数据查看", "desc": "查看财务相关数据"},
        {"code": "financial_report", "name": "财务报表", "desc": "查看和生成财务报表"},
        {"code": "cost_analysis", "name": "成本分析", "desc": "查看成本分析报表"},
        
        # 系统管理相关权限
        {"code": "manage_users", "name": "用户管理", "desc": "管理用户账号"},
        {"code": "system_config", "name": "系统配置", "desc": "系统参数配置"},
        {"code": "view_logs", "name": "日志查看", "desc": "查看系统日志"},
        {"code": "backup_restore", "name": "备份恢复", "desc": "数据备份和恢复"},
    ]
    
    # 角色权限映射（基于v62文档）
    role_permissions_map = {
        # 🔴 总经理（最高决策层）- L1最高权限
        UserRole.GENERAL_MANAGER: [
            # 全局权限
            "view_all_projects", "create_project", "edit_project",
            "view_all_purchase", "final_approve", 
            "view_price", "view_cost", "view_profit",
            "view_finance", "financial_report", "cost_analysis",
            "manage_users", "system_config",
            # 可查看所有敏感信息
        ],
        
        # 🔵 项目主管/工程部负责人（管理层）- L2管理权限  
        UserRole.DEPT_MANAGER: [
            "view_all_projects", "create_project", "edit_project",
            "view_all_purchase", "approve_purchase",
            "view_price", "view_cost",  # 可查看价格
            "manage_suppliers", "optimize_suppliers",
            "approve_contract_change",
            "financial_report", "cost_analysis",
        ],
        
        # 🟢 项目经理（执行层）- L4执行权限
        UserRole.PROJECT_MANAGER: [
            "view_own_projects", "edit_project", "manage_project_files",
            "create_purchase", "view_own_purchase",
            "view_inventory",
            # 注意：不能查看价格信息
        ],
        
        # 🟡 采购员（专业岗位）- L3专业权限
        UserRole.PURCHASER: [
            "view_own_purchase", "quote_price", 
            "view_price", "view_cost",  # 掌握价格信息
            "manage_suppliers",
        ],
        
        # 🟠 管理员（技术支持）- L6系统权限
        UserRole.ADMIN: [
            "upload_contract", "manage_contract",
            "manage_users", "system_config", 
            "view_logs", "backup_restore",
            # 技术角色，不参与业务决策，不能查看价格
        ],
        
        # 🟣 施工队长（现场执行）- L5操作权限  
        UserRole.WORKER: [
            "view_inventory", "outbound",
            # 只能操作自己项目的库存
        ],
        
        # 🔵 财务部（支持部门）- L2管理权限
        UserRole.FINANCE: [
            "view_price", "view_cost", "view_finance",
            "financial_report", "cost_analysis",
            # 可查看价格，但不参与采购决策
        ],
    }
    
    # 清除现有权限配置
    db.query(RolePermission).delete()
    db.commit()
    
    # 创建权限配置
    for role, perm_codes in role_permissions_map.items():
        for perm_code in perm_codes:
            # 找到对应的权限定义
            perm_def = next((p for p in permissions if p["code"] == perm_code), None)
            if perm_def:
                role_perm = RolePermission(
                    role=role.value,
                    permission_code=perm_def["code"],
                    permission_name=perm_def["name"],
                    description=perm_def["desc"]
                )
                db.add(role_perm)
    
    db.commit()
    logger.info("权限配置创建完成")


def create_default_users(db: Session):
    """创建默认测试用户"""
    default_users = [
        {
            "username": "admin",
            "name": "系统管理员", 
            "role": UserRole.ADMIN,
            "email": "admin@example.com",
            "password": "admin123",
            "department": "系统管理部",
            "is_superuser": True
        },
        {
            "username": "general_manager",
            "name": "张总经理",
            "role": UserRole.GENERAL_MANAGER,
            "email": "gm@example.com", 
            "password": "gm123",
            "department": "总经理办公室",
            "is_superuser": False
        },
        {
            "username": "dept_manager", 
            "name": "李工程部主管",
            "role": UserRole.DEPT_MANAGER,
            "email": "dept@example.com",
            "password": "dept123", 
            "department": "工程部",
            "is_superuser": False
        },
        {
            "username": "project_manager",
            "name": "王项目经理", 
            "role": UserRole.PROJECT_MANAGER,
            "email": "pm@example.com",
            "password": "pm123",
            "department": "工程部",
            "is_superuser": False
        },
        {
            "username": "purchaser",
            "name": "赵采购员",
            "role": UserRole.PURCHASER, 
            "email": "purchase@example.com",
            "password": "purchase123",
            "department": "采购部",
            "is_superuser": False
        },
        {
            "username": "worker",
            "name": "刘施工队长",
            "role": UserRole.WORKER,
            "email": "worker@example.com", 
            "password": "worker123",
            "department": "施工部",
            "is_superuser": False
        },
        {
            "username": "finance",
            "name": "陈财务",
            "role": UserRole.FINANCE,
            "email": "finance@example.com",
            "password": "finance123", 
            "department": "财务部",
            "is_superuser": False
        }
    ]
    
    for user_data in default_users:
        existing = db.query(User).filter(User.username == user_data["username"]).first()
        if not existing:
            user = User(
                username=user_data["username"],
                name=user_data["name"],
                role=user_data["role"],
                email=user_data["email"],
                password_hash=get_password_hash(user_data["password"]),
                department=user_data["department"],
                is_active=True,
                is_superuser=user_data["is_superuser"]
            )
            db.add(user)
    
    db.commit()
    logger.info("默认测试用户创建完成")


def main():
    """主初始化函数"""
    logger.info("开始初始化权限系统...")

    # 创建数据库表
    from app.core.database import Base
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        create_permission_categories(db)
        logger.info("权限分类创建完成")

        create_role_permissions(db)
        logger.info("角色权限映射创建完成")

        create_default_users(db)
        logger.info("默认用户创建完成")

        logger.info("权限系统初始化完成")

    except Exception as e:
        logger.error(f"初始化失败: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()