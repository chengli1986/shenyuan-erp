# backend/app/models/project.py
"""
项目数据模型
这个文件定义了项目在数据库中的结构
就像设计一张表格，告诉数据库每一列是什么类型的数据
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Numeric, Enum
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class ProjectStatus(str, enum.Enum):
    """项目状态枚举 - 定义项目可能的状态"""
    PLANNING = "planning"      # 规划中
    IN_PROGRESS = "in_progress"  # 进行中  
    COMPLETED = "completed"    # 已完成
    SUSPENDED = "suspended"    # 暂停


class Project(Base):
    """
    项目数据表模型
    这就像Excel表格的表头，定义每一列存什么数据
    """
    __tablename__ = "projects"  # 数据库中的表名
    
    # 主键ID - 每个项目的唯一标识符（自动递增）
    id = Column(Integer, primary_key=True, index=True, comment="项目ID")
    
    # 项目基本信息
    project_code = Column(String(50), unique=True, index=True, nullable=False, comment="项目编号")
    project_name = Column(String(200), nullable=False, comment="项目名称")
    
    # 合同金额 - 使用Numeric确保精确计算
    contract_amount = Column(Numeric(15, 2), comment="合同金额")
    
    # 项目时间
    start_date = Column(DateTime, comment="项目开始日期")
    end_date = Column(DateTime, comment="项目结束日期")
    
    # 项目负责人
    project_manager = Column(String(100), comment="项目经理")
    
    # 项目状态 - 使用枚举确保数据一致性
    status = Column(Enum(ProjectStatus), default=ProjectStatus.PLANNING, comment="项目状态")
    
    # 项目描述
    description = Column(Text, comment="项目描述")
    
    # 进度信息（百分比 0-100）
    overall_progress = Column(Numeric(5, 2), default=0, comment="整体进度")
    purchase_progress = Column(Numeric(5, 2), default=0, comment="采购进度")
    
    # 系统自动字段 - 记录创建和更新时间
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="更新时间")
    
    def __repr__(self):
        """
        定义对象的字符串表示
        在调试时很有用，可以清楚看到对象内容
        """
        return f"<Project(id={self.id}, name='{self.project_name}', status='{self.status}')>"
    
    def to_dict(self):
        """
        将对象转换为字典格式
        方便转换为JSON格式传给前端
        """
        return {
            "id": self.id,
            "project_code": self.project_code,
            "project_name": self.project_name,
            "contract_amount": float(self.contract_amount) if self.contract_amount else None,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "project_manager": self.project_manager,
            "status": self.status.value if self.status else None,
            "description": self.description,
            "overall_progress": float(self.overall_progress) if self.overall_progress else 0,
            "purchase_progress": float(self.purchase_progress) if self.purchase_progress else 0,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }