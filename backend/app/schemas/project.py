# backend/app/schemas/project.py
"""
项目数据格式定义
这个文件定义API输入和输出的数据格式
就像定义"合同"一样，规定前后端交换数据的格式
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from decimal import Decimal
from app.models.project import ProjectStatus


class ProjectBase(BaseModel):
    """
    项目基础字段
    包含项目的核心信息，用于创建和更新
    """
    project_code: str = Field(..., min_length=1, max_length=50, description="项目编号")
    project_name: str = Field(..., min_length=1, max_length=200, description="项目名称")
    contract_amount: Optional[Decimal] = Field(None, description="合同金额")
    start_date: Optional[datetime] = Field(None, description="开始日期")
    end_date: Optional[datetime] = Field(None, description="结束日期")
    project_manager: Optional[str] = Field(None, max_length=100, description="项目经理")
    status: Optional[ProjectStatus] = Field(ProjectStatus.PLANNING, description="项目状态")
    description: Optional[str] = Field(None, description="项目描述")

    @validator('end_date')
    def validate_end_date(cls, v, values):
        """
        验证结束日期必须晚于开始日期
        这是业务规则的体现
        """
        if v and 'start_date' in values and values['start_date']:
            if v <= values['start_date']:
                raise ValueError('结束日期必须晚于开始日期')
        return v

    @validator('contract_amount')
    def validate_contract_amount(cls, v):
        """验证合同金额必须为正数"""
        if v is not None and v <= 0:
            raise ValueError('合同金额必须大于0')
        return v


class ProjectCreate(ProjectBase):
    """
    创建项目时的数据格式
    继承基础字段，可以添加创建时特有的字段
    """
    pass


class ProjectUpdate(BaseModel):
    """
    更新项目时的数据格式
    所有字段都是可选的，只更新传入的字段
    """
    project_code: Optional[str] = Field(None, min_length=1, max_length=50)
    project_name: Optional[str] = Field(None, min_length=1, max_length=200)
    contract_amount: Optional[Decimal] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    project_manager: Optional[str] = Field(None, max_length=100)
    status: Optional[ProjectStatus] = None
    description: Optional[str] = None
    overall_progress: Optional[Decimal] = Field(None, ge=0, le=100, description="整体进度(0-100)")
    purchase_progress: Optional[Decimal] = Field(None, ge=0, le=100, description="采购进度(0-100)")


class ProjectInDB(ProjectBase):
    """
    数据库中的项目数据格式
    包含所有字段，包括系统自动生成的字段
    """
    id: int
    overall_progress: Decimal = Field(default=0)
    purchase_progress: Decimal = Field(default=0)
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        """
        Pydantic配置
        from_attributes=True 允许从SQLAlchemy模型自动转换
        """
        from_attributes = True


class ProjectResponse(ProjectInDB):
    """
    API响应格式
    返回给前端的项目数据格式
    """
    pass


class ProjectListResponse(BaseModel):
    """
    项目列表响应格式
    包含分页信息和项目列表
    """
    items: list[ProjectResponse] = Field(description="项目列表")
    total: int = Field(description="总数量")
    page: int = Field(description="当前页码")
    size: int = Field(description="每页数量")
    pages: int = Field(description="总页数")

    class Config:
        from_attributes = True