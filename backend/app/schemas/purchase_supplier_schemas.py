"""
供应商、辅材模板、入库批次相关的Pydantic模型
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field


# ========== 供应商相关 ==========

class SupplierBase(BaseModel):
    """供应商基础信息"""
    supplier_name: str
    supplier_code: Optional[str] = None
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    business_license: Optional[str] = None
    tax_number: Optional[str] = None
    bank_account: Optional[str] = None
    rating: Optional[int] = Field(default=3, ge=1, le=5)
    remarks: Optional[str] = None


class SupplierCreate(SupplierBase):
    """创建供应商"""
    pass


class SupplierUpdate(BaseModel):
    """更新供应商"""
    supplier_name: Optional[str] = None
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    rating: Optional[int] = Field(None, ge=1, le=5)
    is_active: Optional[bool] = None
    remarks: Optional[str] = None


class SupplierInDB(SupplierBase):
    """数据库中的供应商"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SupplierListResponse(BaseModel):
    """供应商列表响应"""
    items: List[SupplierInDB]
    total: int
    page: int
    size: int
    pages: int


# ========== 辅材模板相关 ==========

class AuxiliaryTemplateItemBase(BaseModel):
    """辅材模板项基础信息"""
    item_name: str
    specification: Optional[str] = None
    unit: Optional[str] = None
    ratio: Optional[Decimal] = None
    is_required: bool = False
    reference_price: Optional[Decimal] = None
    remarks: Optional[str] = None
    sort_order: int = 0


class AuxiliaryTemplateBase(BaseModel):
    """辅材模板基础信息"""
    template_name: str
    project_type: Optional[str] = None
    description: Optional[str] = None


class AuxiliaryTemplateCreate(AuxiliaryTemplateBase):
    """创建辅材模板"""
    items: List[AuxiliaryTemplateItemBase]


class AuxiliaryTemplateInDB(AuxiliaryTemplateBase):
    """数据库中的辅材模板"""
    id: int
    usage_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    items: List[AuxiliaryTemplateItemBase]

    class Config:
        from_attributes = True


# ========== 入库批次相关 ==========

class InboundBatchBase(BaseModel):
    """入库批次基础信息"""
    purchase_request_item_id: int
    inbound_quantity: Decimal = Field(..., gt=0)
    unit_price: Optional[Decimal] = None
    quality_status: str = "qualified"
    quality_check_notes: Optional[str] = None
    storage_location: Optional[str] = None
    supplier_batch_info: Optional[Dict[str, Any]] = None
    remarks: Optional[str] = None


class InboundBatchCreate(InboundBatchBase):
    """创建入库批次"""
    pass


class InboundBatchInDB(InboundBatchBase):
    """数据库中的入库批次"""
    id: int
    batch_number: str
    inbound_date: datetime
    operator_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True
