# backend/app/models/contract.py
"""
合同清单数据模型
基于实际的投标清单Excel格式设计
支持按系统分类管理，支持版本控制和优化功能
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Numeric, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class ContractFileVersion(Base):
    """
    合同清单版本表
    
    每次上传投标清单或进行重大优化时，都会创建一个新版本
    支持版本历史查看和回滚功能
    
    业务场景：
    - 版本1：初始投标清单上传
    - 版本2：中标后工程师技术优化
    - 版本3：业主签证变更（需要上传签证单）
    """
    __tablename__ = "contract_file_versions"
    
    # 主键和关联
    id = Column(Integer, primary_key=True, index=True, comment="版本ID")
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, comment="关联的项目ID")
    
    # 版本信息
    version_number = Column(Integer, nullable=False, comment="版本号，从1开始自动递增")
    
    # 上传信息
    upload_time = Column(DateTime(timezone=True), server_default=func.now(), comment="上传时间")
    upload_user_name = Column(String(100), nullable=False, comment="上传人员姓名")
    
    # 文件信息
    original_filename = Column(String(255), nullable=False, comment="原始Excel文件名")
    stored_filename = Column(String(255), nullable=False, comment="服务器存储的文件名（防重名）")
    file_size = Column(Integer, comment="文件大小（字节）")
    
    # 版本说明和变更信息
    upload_reason = Column(Text, comment="上传原因，如：初始投标清单、技术优化、业主变更等")
    change_description = Column(Text, comment="变更详细说明")
    
    # 状态管理
    is_current = Column(Boolean, default=True, comment="是否为当前生效版本（只能有一个）")
    is_optimized = Column(Boolean, default=False, comment="是否为优化版本（区别于原始投标清单）")
    
    # 变更依据（如业主签证单）
    change_evidence_file = Column(String(255), comment="变更依据文件路径（如业主签证单PDF）")
    
    # 系统时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="更新时间")
    
    # 关系定义
    contract_items = relationship("ContractItem", back_populates="version", cascade="all, delete-orphan")
    system_categories = relationship("SystemCategory", back_populates="version", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ContractFileVersion(id={self.id}, project_id={self.project_id}, version={self.version_number})>"


class SystemCategory(Base):
    """
    系统分类表
    
    根据投标清单的Excel sheet页面自动创建
    每个系统分类对应Excel中的一个sheet（如：视频监控系统、门禁系统等）
    
    特点：
    - 支持项目级别的自定义分类
    - 每个版本可以有不同的系统分类
    """
    __tablename__ = "system_categories"
    
    # 主键和关联
    id = Column(Integer, primary_key=True, index=True, comment="分类ID")
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, comment="项目ID")
    version_id = Column(Integer, ForeignKey("contract_file_versions.id"), nullable=False, comment="版本ID")
    
    # 分类信息
    category_name = Column(String(100), nullable=False, comment="系统分类名称，如：视频安防监控系统")
    category_code = Column(String(50), comment="系统编码，如：VIDEO_SURVEILLANCE")
    excel_sheet_name = Column(String(100), comment="对应的Excel sheet名称")
    
    # 预算和统计信息
    budget_amount = Column(Numeric(15, 2), comment="该系统的预算金额")
    total_items_count = Column(Integer, default=0, comment="该系统下的设备总数")
    
    # 描述和备注
    description = Column(Text, comment="系统描述")
    remarks = Column(Text, comment="备注信息")
    
    # 系统时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="更新时间")
    
    # 关系定义
    version = relationship("ContractFileVersion", back_populates="system_categories")
    contract_items = relationship("ContractItem", back_populates="category")
    
    def __repr__(self):
        return f"<SystemCategory(id={self.id}, name='{self.category_name}')>"


class ContractItem(Base):
    """
    合同清单明细表
    
    存储投标清单中每一行的设备信息
    对应Excel中的数据行：序号、设备名称、品牌型号、规格、单价、数量等
    
    这是系统的核心数据表，所有采购申请都要基于这个表进行校验
    """
    __tablename__ = "contract_items"
    
    # 主键和关联关系
    id = Column(Integer, primary_key=True, index=True, comment="明细ID")
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, comment="项目ID")
    version_id = Column(Integer, ForeignKey("contract_file_versions.id"), nullable=False, comment="版本ID")
    category_id = Column(Integer, ForeignKey("system_categories.id"), comment="系统分类ID")
    
    # Excel原始数据字段（对应投标清单的列）
    serial_number = Column(String(50), comment="Excel中的序号")
    item_name = Column(String(200), nullable=False, comment="设备名称")
    brand_model = Column(String(200), comment="设备品牌型号")
    specification = Column(Text, comment="规格描述")
    unit = Column(String(20), comment="单位，如：台、米、个、套")
    quantity = Column(Numeric(10, 2), nullable=False, comment="数量")
    unit_price = Column(Numeric(15, 2), comment="单价（元）")
    total_price = Column(Numeric(15, 2), comment="小计（元）= 数量 × 单价")
    origin_place = Column(String(100), comment="原产地")
    
    # 扩展字段（用于后续功能）
    item_type = Column(String(20), default='主材', comment="物料类型：主材/辅材")
    is_key_equipment = Column(Boolean, default=False, comment="是否为关键设备")
    technical_params = Column(Text, comment="详细技术参数（JSON格式存储）")
    
    # 优化和变更记录
    is_optimized = Column(Boolean, default=False, comment="是否为优化后的项目")
    optimization_reason = Column(Text, comment="优化原因说明")
    original_item_id = Column(Integer, ForeignKey("contract_items.id"), comment="原始项目ID（用于追溯优化历史）")
    
    # 状态管理
    is_active = Column(Boolean, default=True, comment="是否有效（删除标记）")
    remarks = Column(Text, comment="备注信息")
    
    # 系统时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="更新时间")
    
    # 关系定义
    version = relationship("ContractFileVersion", back_populates="contract_items")
    category = relationship("SystemCategory", back_populates="contract_items")
    
    # 自关联：用于追溯优化历史
    original_item = relationship("ContractItem", remote_side=[id], backref="optimized_versions")
    
    def __repr__(self):
        return f"<ContractItem(id={self.id}, name='{self.item_name}', quantity={self.quantity})>"
    
    def to_dict(self):
        """
        将数据库对象转换为字典格式
        用于API响应和前端显示
        """
        return {
            "id": self.id,
            "project_id": self.project_id,
            "version_id": self.version_id,
            "category_id": self.category_id,
            "serial_number": self.serial_number,
            "item_name": self.item_name,
            "brand_model": self.brand_model,
            "specification": self.specification,
            "unit": self.unit,
            "quantity": float(self.quantity) if self.quantity else 0,
            "unit_price": float(self.unit_price) if self.unit_price else 0,
            "total_price": float(self.total_price) if self.total_price else 0,
            "origin_place": self.origin_place,
            "item_type": self.item_type,
            "is_key_equipment": self.is_key_equipment,
            "technical_params": self.technical_params,
            "is_optimized": self.is_optimized,
            "optimization_reason": self.optimization_reason,
            "is_active": self.is_active,
            "remarks": self.remarks,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def calculate_total_price(self):
        """
        自动计算总价
        总价 = 数量 × 单价
        """
        if self.quantity and self.unit_price:
            self.total_price = self.quantity * self.unit_price
        return self.total_price