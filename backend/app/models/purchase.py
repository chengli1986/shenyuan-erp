"""
采购请购相关数据模型
"""

from sqlalchemy import (
    Column, Integer, String, Float, Text, DateTime, 
    Boolean, ForeignKey, Enum, JSON, DECIMAL
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class PurchaseStatus(enum.Enum):
    """申购单状态枚举"""
    DRAFT = "draft"                    # 草稿
    SUBMITTED = "submitted"             # 已提交
    PRICE_QUOTED = "price_quoted"       # 已询价
    DEPT_APPROVED = "dept_approved"     # 部门已审批
    FINAL_APPROVED = "final_approved"   # 最终审批通过
    REJECTED = "rejected"               # 已拒绝
    CANCELLED = "cancelled"             # 已取消
    COMPLETED = "completed"             # 已完成


class ItemType(enum.Enum):
    """物料类型枚举"""
    MAIN_MATERIAL = "main"         # 主材
    AUXILIARY_MATERIAL = "auxiliary"  # 辅材


class ApprovalStatus(enum.Enum):
    """审批状态枚举"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class PurchaseRequest(Base):
    """申购单主表"""
    __tablename__ = "purchase_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    request_code = Column(String(50), unique=True, index=True, nullable=False)  # 申购单号
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    
    # 申购信息
    request_date = Column(DateTime, server_default=func.now(), nullable=False)
    requester_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # 申购人
    required_date = Column(DateTime)  # 需求日期
    
    # 状态和金额
    status = Column(Enum(PurchaseStatus), default=PurchaseStatus.DRAFT, nullable=False)
    total_amount = Column(DECIMAL(15, 2), default=0)  # 总金额
    
    # 审批信息
    approval_notes = Column(Text)  # 审批意见
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # 关系
    project = relationship("Project", back_populates="purchase_requests")
    items = relationship("PurchaseRequestItem", back_populates="purchase_request", cascade="all, delete-orphan")
    approvals = relationship("PurchaseApproval", back_populates="purchase_request", cascade="all, delete-orphan")


class PurchaseRequestItem(Base):
    """申购明细表"""
    __tablename__ = "purchase_request_items"
    
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("purchase_requests.id"), nullable=False)
    
    # 关联合同清单项（主材必须关联）
    contract_item_id = Column(Integer, ForeignKey("contract_items.id"), nullable=True)
    
    # 物料信息
    item_name = Column(String(200), nullable=False)
    specification = Column(Text)  # 规格参数
    brand = Column(String(100))  # 品牌
    unit = Column(String(20))  # 单位
    quantity = Column(DECIMAL(10, 2), nullable=False)  # 申购数量
    
    # 价格信息（采购员填写）
    unit_price = Column(DECIMAL(15, 2))  # 单价
    total_price = Column(DECIMAL(15, 2))  # 总价
    
    # 类型标识
    item_type = Column(Enum(ItemType), default=ItemType.MAIN_MATERIAL, nullable=False)
    
    # 供应商信息（采购员维护）
    supplier_id = Column(Integer, ForeignKey("suppliers.id"))
    supplier_name = Column(String(100))
    supplier_contact = Column(String(50))
    supplier_info = Column(JSON)  # 供应商详细信息
    
    # 交付信息
    estimated_delivery = Column(DateTime)  # 预计到货时间
    
    # 入库跟踪
    received_quantity = Column(DECIMAL(10, 2), default=0)  # 已到货数量
    remaining_quantity = Column(DECIMAL(10, 2), default=0)  # 剩余数量
    
    # 状态和备注
    status = Column(String(20), default="pending")
    remarks = Column(Text)
    
    # 关系
    purchase_request = relationship("PurchaseRequest", back_populates="items")
    contract_item = relationship("ContractItem", backref="purchase_items")
    supplier = relationship("Supplier", backref="purchase_items")
    inbound_batches = relationship("InboundBatch", back_populates="purchase_item")


class PurchaseApproval(Base):
    """申购审批记录表"""
    __tablename__ = "purchase_approvals"
    
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("purchase_requests.id"), nullable=False)
    
    # 审批信息
    approver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    approver_role = Column(String(50), nullable=False)  # 审批角色
    approval_level = Column(Integer, nullable=False)  # 审批级别 1-项目主管 2-总经理
    
    # 审批结果
    approval_date = Column(DateTime, server_default=func.now())
    approval_status = Column(Enum(ApprovalStatus), nullable=False)
    approval_notes = Column(Text)
    
    # 权限标识
    can_view_price = Column(Boolean, default=False)  # 是否可查看价格
    
    # 关系
    purchase_request = relationship("PurchaseRequest", back_populates="approvals")
    approver = relationship("User", backref="purchase_approvals")


class Supplier(Base):
    """供应商信息表"""
    __tablename__ = "suppliers"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 基本信息
    supplier_name = Column(String(100), unique=True, nullable=False)
    supplier_code = Column(String(50), unique=True, index=True)
    
    # 联系信息
    contact_person = Column(String(50))
    phone = Column(String(20))
    email = Column(String(100))
    address = Column(Text)
    
    # 工商信息
    business_license = Column(String(50))  # 营业执照号
    tax_number = Column(String(50))  # 税号
    bank_account = Column(String(100))  # 银行账号
    
    # 评级和状态
    rating = Column(Integer, default=3)  # 评级 1-5
    is_active = Column(Boolean, default=True)
    
    # 备注
    remarks = Column(Text)
    
    # 时间戳
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


class InboundBatch(Base):
    """分批入库记录表"""
    __tablename__ = "inbound_batches"
    
    id = Column(Integer, primary_key=True, index=True)
    purchase_request_item_id = Column(Integer, ForeignKey("purchase_request_items.id"), nullable=False)
    
    # 入库信息
    batch_number = Column(String(50), unique=True, nullable=False)  # 批次号
    inbound_date = Column(DateTime, server_default=func.now())
    inbound_quantity = Column(DECIMAL(10, 2), nullable=False)  # 本批入库数量
    
    # 价格信息（实际入库价格）
    unit_price = Column(DECIMAL(15, 2))
    
    # 质量信息
    quality_status = Column(String(20), default="qualified")  # 质量状态
    quality_check_notes = Column(Text)
    
    # 操作信息
    operator_id = Column(Integer, ForeignKey("users.id"))
    storage_location = Column(String(100))  # 存放位置
    
    # 供应商批次信息
    supplier_batch_info = Column(JSON)
    
    # 备注
    remarks = Column(Text)
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now())
    
    # 关系
    purchase_item = relationship("PurchaseRequestItem", back_populates="inbound_batches")
    operator = relationship("User", backref="inbound_operations")


class AuxiliaryTemplate(Base):
    """辅材模板表"""
    __tablename__ = "auxiliary_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 模板信息
    template_name = Column(String(100), unique=True, nullable=False)
    project_type = Column(String(50))  # 项目类型
    description = Column(Text)
    
    # 使用统计
    usage_count = Column(Integer, default=0)  # 使用次数
    
    # 时间戳
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # 关系
    items = relationship("AuxiliaryTemplateItem", back_populates="template", cascade="all, delete-orphan")


class AuxiliaryTemplateItem(Base):
    """辅材模板明细表"""
    __tablename__ = "auxiliary_template_items"
    
    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("auxiliary_templates.id"), nullable=False)
    
    # 物料信息
    item_name = Column(String(200), nullable=False)
    specification = Column(Text)
    unit = Column(String(20))
    
    # 配比信息
    ratio = Column(DECIMAL(10, 4))  # 相对于主材的配比
    is_required = Column(Boolean, default=False)  # 是否必选
    
    # 参考价格
    reference_price = Column(DECIMAL(15, 2))
    
    # 备注
    remarks = Column(Text)
    
    # 排序
    sort_order = Column(Integer, default=0)
    
    # 关系
    template = relationship("AuxiliaryTemplate", back_populates="items")