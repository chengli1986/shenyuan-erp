# backend/app/schemas/contract.py
"""
合同清单API数据格式定义

这个文件定义了合同清单相关API的输入和输出数据格式
包括请求数据验证和响应数据结构
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class ContractFileVersionBase(BaseModel):
    """
    合同清单版本基础字段
    用于创建和更新合同清单版本时的数据验证
    """
    upload_user_name: str = Field(..., min_length=1, max_length=100, description="上传人员姓名")
    upload_reason: Optional[str] = Field(None, description="上传原因说明")
    change_description: Optional[str] = Field(None, description="变更详细说明")
    is_optimized: Optional[bool] = Field(False, description="是否为优化版本")
    change_evidence_file: Optional[str] = Field(None, description="变更依据文件路径")


class ContractFileVersionCreate(ContractFileVersionBase):
    """
    创建合同清单版本时的数据格式
    包含文件信息等必要字段
    """
    project_id: int = Field(..., description="项目ID")
    original_filename: str = Field(..., min_length=1, max_length=255, description="原始文件名")
    
    @validator('original_filename')
    def validate_filename(cls, v):
        """验证文件名必须是Excel格式"""
        if not v.lower().endswith(('.xlsx', '.xls')):
            raise ValueError('文件必须是Excel格式(.xlsx或.xls)')
        return v


class ContractFileVersionUpdate(BaseModel):
    """
    更新合同清单版本时的数据格式
    所有字段都是可选的
    """
    upload_reason: Optional[str] = Field(None, description="上传原因说明")
    change_description: Optional[str] = Field(None, description="变更详细说明")
    is_current: Optional[bool] = Field(None, description="是否为当前版本")


class ContractFileVersionResponse(ContractFileVersionBase):
    """
    合同清单版本响应数据格式
    返回给前端的完整版本信息
    """
    id: int
    project_id: int
    version_number: int
    original_filename: str
    stored_filename: str
    file_size: Optional[int]
    upload_time: datetime
    is_current: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        """允许从SQLAlchemy模型自动转换"""
        from_attributes = True


class SystemCategoryBase(BaseModel):
    """
    系统分类基础字段
    """
    category_name: str = Field(..., min_length=1, max_length=100, description="系统分类名称")
    category_code: Optional[str] = Field(None, max_length=50, description="系统编码")
    excel_sheet_name: Optional[str] = Field(None, max_length=100, description="Excel sheet名称")
    budget_amount: Optional[Decimal] = Field(None, description="预算金额")
    description: Optional[str] = Field(None, description="系统描述")
    remarks: Optional[str] = Field(None, description="备注信息")
    
    @validator('budget_amount')
    def validate_budget_amount(cls, v):
        """验证预算金额必须为正数"""
        if v is not None and v <= 0:
            raise ValueError('预算金额必须大于0')
        return v


class SystemCategoryCreate(SystemCategoryBase):
    """
    创建系统分类时的数据格式
    """
    project_id: int = Field(..., description="项目ID")
    version_id: int = Field(..., description="版本ID")


class SystemCategoryUpdate(BaseModel):
    """
    更新系统分类时的数据格式
    """
    category_name: Optional[str] = Field(None, min_length=1, max_length=100)
    category_code: Optional[str] = Field(None, max_length=50)
    budget_amount: Optional[Decimal] = None
    description: Optional[str] = None
    remarks: Optional[str] = None


class SystemCategoryResponse(SystemCategoryBase):
    """
    系统分类响应数据格式
    """
    id: int
    project_id: int
    version_id: int
    total_items_count: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class ContractItemBase(BaseModel):
    """
    合同清单明细基础字段
    """
    serial_number: Optional[str] = Field(None, max_length=50, description="序号")
    item_name: str = Field(..., min_length=1, max_length=200, description="设备名称")
    brand_model: Optional[str] = Field(None, max_length=200, description="品牌型号")
    specification: Optional[str] = Field(None, description="规格描述")
    unit: Optional[str] = Field(None, max_length=20, description="单位")
    quantity: Decimal = Field(..., gt=0, description="数量，必须大于0")
    unit_price: Optional[Decimal] = Field(None, description="单价")
    origin_place: Optional[str] = Field(None, max_length=100, description="原产地")
    item_type: Optional[str] = Field("主材", description="物料类型")
    is_key_equipment: Optional[bool] = Field(False, description="是否为关键设备")
    technical_params: Optional[str] = Field(None, description="技术参数JSON")
    optimization_reason: Optional[str] = Field(None, description="优化原因")
    remarks: Optional[str] = Field(None, description="备注信息")
    
    @validator('quantity')
    def validate_quantity(cls, v):
        """验证数量必须大于0"""
        if v <= 0:
            raise ValueError('数量必须大于0')
        return v
    
    @validator('unit_price')
    def validate_unit_price(cls, v):
        """验证单价必须为正数（如果提供）"""
        if v is not None and v <= 0:
            raise ValueError('单价必须大于0')
        return v
    
    @validator('item_type')
    def validate_item_type(cls, v):
        """验证物料类型只能是主材或辅材"""
        if v not in ['主材', '辅材']:
            raise ValueError('物料类型只能是主材或辅材')
        return v


class ContractItemCreate(ContractItemBase):
    """
    创建合同清单明细时的数据格式
    """
    project_id: int = Field(..., description="项目ID")
    version_id: int = Field(..., description="版本ID")
    category_id: Optional[int] = Field(None, description="系统分类ID")


class ContractItemUpdate(BaseModel):
    """
    更新合同清单明细时的数据格式
    """
    serial_number: Optional[str] = Field(None, max_length=50)
    item_name: Optional[str] = Field(None, min_length=1, max_length=200)
    brand_model: Optional[str] = Field(None, max_length=200)
    specification: Optional[str] = None
    unit: Optional[str] = Field(None, max_length=20)
    quantity: Optional[Decimal] = Field(None, gt=0)
    unit_price: Optional[Decimal] = Field(None, gt=0)
    origin_place: Optional[str] = Field(None, max_length=100)
    item_type: Optional[str] = None
    is_key_equipment: Optional[bool] = None
    technical_params: Optional[str] = None
    optimization_reason: Optional[str] = None
    remarks: Optional[str] = None


class ContractItemResponse(ContractItemBase):
    """
    合同清单明细响应数据格式
    """
    id: int
    project_id: int
    version_id: int
    category_id: Optional[int]
    total_price: Optional[Decimal]
    is_optimized: bool
    original_item_id: Optional[int]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class ContractItemListResponse(BaseModel):
    """
    合同清单明细列表响应格式
    包含分页信息和明细列表
    """
    items: List[ContractItemResponse] = Field(description="明细列表")
    total: int = Field(description="总数量")
    page: int = Field(description="当前页码")
    size: int = Field(description="每页数量")
    pages: int = Field(description="总页数")


class ContractSummaryResponse(BaseModel):
    """
    合同清单汇总信息响应格式
    用于显示项目的合同清单概况
    """
    project_id: int
    current_version: Optional[ContractFileVersionResponse]
    total_versions: int
    total_categories: int
    total_items: int
    total_amount: Optional[Decimal]
    
    class Config:
        from_attributes = True


class ExcelUploadResponse(BaseModel):
    """
    Excel文件上传响应格式
    """
    success: bool = Field(description="是否上传成功")
    message: str = Field(description="响应消息")
    version_id: Optional[int] = Field(description="创建的版本ID")
    parsed_data: Optional[dict] = Field(description="解析的数据统计")
    errors: Optional[List[str]] = Field(description="错误信息列表")
    
    class Config:
        from_attributes = True