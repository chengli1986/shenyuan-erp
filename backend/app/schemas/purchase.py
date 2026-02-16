"""
采购请购相关的Pydantic模型
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, validator
from enum import Enum

# 供应商、辅材模板、入库批次 schemas — 从子模块导入并重新导出
from app.schemas.purchase_supplier_schemas import (  # noqa: F401
    SupplierBase,
    SupplierCreate,
    SupplierUpdate,
    SupplierInDB,
    SupplierListResponse,
    AuxiliaryTemplateItemBase,
    AuxiliaryTemplateBase,
    AuxiliaryTemplateCreate,
    AuxiliaryTemplateInDB,
    InboundBatchBase,
    InboundBatchCreate,
    InboundBatchInDB,
)


class PurchaseStatus(str, Enum):
    """申购单状态"""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    PRICE_QUOTED = "price_quoted"
    DEPT_APPROVED = "dept_approved"
    FINAL_APPROVED = "final_approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class ItemType(str, Enum):
    """物料类型"""
    MAIN_MATERIAL = "main"
    AUXILIARY_MATERIAL = "auxiliary"


class ApprovalStatus(str, Enum):
    """审批状态"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class WorkflowStep(str, Enum):
    """工作流步骤"""
    PROJECT_MANAGER = "project_manager"
    PURCHASER = "purchaser"
    DEPT_MANAGER = "dept_manager"
    GENERAL_MANAGER = "general_manager"
    COMPLETED = "completed"


class PaymentMethod(str, Enum):
    """付款方式"""
    PREPAYMENT = "PREPAYMENT"
    DELIVERY_PAYMENT = "DELIVERY_PAYMENT"
    MONTHLY_SETTLEMENT = "MONTHLY_SETTLEMENT"
    CASH = "CASH"
    BANK_TRANSFER = "BANK_TRANSFER"


# ========== 申购明细相关 ==========

class PurchaseItemBase(BaseModel):
    """申购明细基础信息"""
    contract_item_id: Optional[int] = None  # 主材必须关联
    system_category_id: Optional[int] = None  # 系统分类
    item_name: str
    specification: Optional[str] = None
    brand: Optional[str] = None
    unit: str
    quantity: Decimal = Field(..., gt=0)
    item_type: ItemType
    remarks: Optional[str] = None


class PurchaseItemCreate(PurchaseItemBase):
    """创建申购明细（项目经理）"""
    pass

    @validator('contract_item_id')
    def validate_contract_item(cls, v, values):
        """主材必须关联合同清单项"""
        item_type = values.get('item_type')
        # 主材必须关联合同清单项
        if item_type == ItemType.MAIN_MATERIAL and not v:
            raise ValueError('主材必须关联合同清单项')
        return v


class PurchaseItemPriceQuote(BaseModel):
    """询价信息（采购员）"""
    item_id: int
    unit_price: Decimal = Field(..., gt=0)
    total_price: Optional[Decimal] = None
    supplier_id: Optional[int] = None
    supplier_name: Optional[str] = None
    supplier_contact: Optional[str] = None
    supplier_contact_person: Optional[str] = None  # 新增：供应商联系人全名
    payment_method: Optional[str] = None  # 修改为字符串，支持自由输入付款方式
    estimated_delivery: Optional[datetime] = None

    @validator('total_price', always=True)
    def calculate_total(cls, v, values):
        """自动计算总价"""
        if not v and 'unit_price' in values:
            # 这里需要从数据库获取数量来计算
            pass
        return v


class PurchaseItemInDB(PurchaseItemBase):
    """数据库中的申购明细"""
    id: int
    request_id: int
    unit_price: Optional[Decimal] = None
    total_price: Optional[Decimal] = None
    supplier_id: Optional[int] = None
    supplier_name: Optional[str] = None
    supplier_contact: Optional[str] = None
    supplier_info: Optional[Dict[str, Any]] = None
    estimated_delivery: Optional[datetime] = None
    received_quantity: Decimal = Field(default=Decimal(0))
    remaining_quantity: Decimal = Field(default=Decimal(0))
    status: str = "pending"

    # 关联字段（动态添加）
    system_category_name: Optional[str] = None

    class Config:
        from_attributes = True


class PurchaseItemWithPrice(PurchaseItemInDB):
    """包含价格信息的申购明细（仅特定角色可见）"""
    pass


class PurchaseItemWithoutPrice(BaseModel):
    """不包含价格信息的申购明细（项目经理视图）"""
    id: int
    request_id: int
    contract_item_id: Optional[int] = None
    system_category_id: Optional[int] = None
    item_name: str
    specification: Optional[str] = None
    brand: Optional[str] = None
    unit: str
    quantity: Decimal
    item_type: ItemType
    supplier_name: Optional[str] = None
    estimated_delivery: Optional[datetime] = None
    received_quantity: Decimal
    remaining_quantity: Decimal
    status: str
    remarks: Optional[str] = None

    # 关联字段（动态添加）
    system_category_name: Optional[str] = None

    class Config:
        from_attributes = True


# ========== 申购单相关 ==========

class PurchaseRequestBase(BaseModel):
    """申购单基础信息"""
    project_id: int
    required_date: Optional[datetime] = None
    system_category: Optional[str] = None  # 所属系统
    remarks: Optional[str] = None


class PurchaseRequestCreate(PurchaseRequestBase):
    """创建申购单"""
    items: List[PurchaseItemCreate]

    @validator('items')
    def validate_items(cls, v):
        """至少包含一个申购项"""
        if not v:
            raise ValueError('申购单必须包含至少一个申购项')
        return v


class PurchaseRequestUpdate(BaseModel):
    """更新申购单"""
    required_date: Optional[datetime] = None
    remarks: Optional[str] = None
    status: Optional[PurchaseStatus] = None
    items: Optional[List[PurchaseItemCreate]] = None


class PurchaseRequestSubmit(BaseModel):
    """提交申购单"""
    pass


class PurchaseRequestQuote(BaseModel):
    """申购单询价"""
    items: List[PurchaseItemPriceQuote]


class PurchaseRequestApprove(BaseModel):
    """审批申购单"""
    approval_status: ApprovalStatus
    approval_notes: Optional[str] = None


class PurchaseRequestPriceQuote(BaseModel):
    """采购员询价"""
    items: List[PurchaseItemPriceQuote]
    quote_notes: Optional[str] = None
    # 移除统一的payment_method和estimated_delivery_date，改为物料级别


class PurchaseWorkflowOperation(BaseModel):
    """工作流操作"""
    operation: str  # submit, approve, reject, return
    notes: Optional[str] = None
    operation_data: Optional[Dict[str, Any]] = None


class PurchaseRequestInDB(PurchaseRequestBase):
    """数据库中的申购单"""
    id: int
    request_code: str
    request_date: datetime
    requester_id: int
    status: PurchaseStatus
    total_amount: Optional[Decimal] = None

    # 工作流字段
    current_step: str  # 暂时使用字符串类型
    current_approver_id: Optional[int] = None

    # 采购信息
    payment_method: Optional[PaymentMethod] = None
    estimated_delivery_date: Optional[datetime] = None

    # 审批信息
    approval_notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PurchaseRequestWithItems(PurchaseRequestInDB):
    """包含明细的申购单"""
    items: List[PurchaseItemInDB]
    requester_name: Optional[str] = None
    project_name: Optional[str] = None


class PurchaseRequestWithoutPrice(BaseModel):
    """不包含价格的申购单（项目经理视图）"""
    id: int
    request_code: str
    project_id: int
    request_date: datetime
    requester_id: int
    required_date: Optional[datetime] = None
    system_category: Optional[str] = None
    status: PurchaseStatus

    # 工作流字段（项目经理需要看到）
    current_step: str  # 暂时使用字符串类型
    current_approver_id: Optional[int] = None

    approval_notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    items: List[PurchaseItemWithoutPrice] = []
    requester_name: Optional[str] = None
    project_name: Optional[str] = None
    # 不包含 total_amount, payment_method, estimated_delivery_date 等价格和采购信息

    class Config:
        from_attributes = True


class PurchaseWorkflowLog(BaseModel):
    """工作流操作记录"""
    id: int
    request_id: int
    from_step: Optional[WorkflowStep] = None
    to_step: WorkflowStep
    operation: str
    operator_id: int
    operator_role: str
    operation_notes: Optional[str] = None
    operation_data: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ========== 审批相关 ==========

class ApprovalRecordBase(BaseModel):
    """审批记录基础信息"""
    approver_id: int
    approver_role: str
    approval_level: int
    approval_status: ApprovalStatus
    approval_notes: Optional[str] = None
    can_view_price: bool = False


class ApprovalRecordInDB(ApprovalRecordBase):
    """数据库中的审批记录"""
    id: int
    request_id: int
    approval_date: datetime
    approver_name: Optional[str] = None

    class Config:
        from_attributes = True


# ========== 列表响应 ==========

class PurchaseRequestListResponse(BaseModel):
    """申购单列表响应"""
    items: List[PurchaseRequestWithItems]
    total: int
    page: int
    size: int
    pages: int
