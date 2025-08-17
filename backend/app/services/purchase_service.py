"""
采购请购业务逻辑服务
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from app.models.purchase import (
    PurchaseRequest, PurchaseRequestItem, PurchaseApproval,
    Supplier, AuxiliaryTemplate, AuxiliaryTemplateItem,
    PurchaseStatus, ItemType, ApprovalStatus
)
from app.models.project import Project
from app.models.contract import ContractItem, ContractFileVersion
from app.models.user import User
from app.schemas.purchase import (
    PurchaseRequestCreate, AuxiliaryTemplateCreate
)


class PurchaseService:
    """采购请购服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_purchase_request(
        self, 
        request_data: PurchaseRequestCreate,
        requester_id: int
    ) -> PurchaseRequest:
        """
        创建申购单
        - 生成申购单号
        - 验证主材数量
        - 创建申购明细
        """
        # 生成申购单号
        request_code = self._generate_request_code()
        
        # 创建申购单主表
        purchase_request = PurchaseRequest(
            request_code=request_code,
            project_id=request_data.project_id,
            requester_id=requester_id,
            required_date=request_data.required_date,
            system_category=request_data.system_category,  # 添加所属系统字段
            status=PurchaseStatus.DRAFT
        )
        self.db.add(purchase_request)
        self.db.flush()  # 获取ID但不提交
        
        # 创建申购明细
        for item_data in request_data.items:
            # 主材验证
            if item_data.item_type == ItemType.MAIN_MATERIAL:
                if not item_data.contract_item_id:
                    raise ValueError(f"主材 {item_data.item_name} 必须关联合同清单项")
                
                # 验证合同清单项存在
                contract_item = self.db.query(ContractItem).filter(
                    ContractItem.id == item_data.contract_item_id
                ).first()
                
                if not contract_item:
                    raise ValueError(f"合同清单项 {item_data.contract_item_id} 不存在")
                
                # 检查是否超量（累计申购量）
                total_requested = self._get_total_requested_quantity(
                    contract_item.id, 
                    exclude_request_id=None
                )
                
                if total_requested + item_data.quantity > contract_item.quantity:
                    raise ValueError(
                        f"主材 {item_data.item_name} 申购数量超出合同限制。"
                        f"合同数量: {contract_item.quantity}, "
                        f"已申购: {total_requested}, "
                        f"本次申购: {item_data.quantity}"
                    )
                
                # 使用合同清单的信息
                item = PurchaseRequestItem(
                    request_id=purchase_request.id,
                    contract_item_id=contract_item.id,
                    system_category_id=item_data.system_category_id,
                    item_name=contract_item.item_name,
                    specification=contract_item.specification or item_data.specification,
                    brand=contract_item.brand or item_data.brand,
                    unit=contract_item.unit,
                    quantity=item_data.quantity,
                    item_type=ItemType.MAIN_MATERIAL,
                    remaining_quantity=item_data.quantity,
                    remarks=item_data.remarks
                )
            else:
                # 辅材可以自由添加
                item = PurchaseRequestItem(
                    request_id=purchase_request.id,
                    contract_item_id=None,
                    system_category_id=item_data.system_category_id,
                    item_name=item_data.item_name,
                    specification=item_data.specification,
                    brand=item_data.brand,
                    unit=item_data.unit,
                    quantity=item_data.quantity,
                    item_type=ItemType.AUXILIARY_MATERIAL,
                    remaining_quantity=item_data.quantity,
                    remarks=item_data.remarks
                )
            
            self.db.add(item)
        
        self.db.commit()
        self.db.refresh(purchase_request)
        
        return purchase_request
    
    def validate_main_material_quantities(self, purchase_request: PurchaseRequest):
        """
        验证主材申购数量是否超出合同限制
        用于提交申购单时的最终验证
        """
        for item in purchase_request.items:
            if item.item_type == ItemType.MAIN_MATERIAL:
                if not item.contract_item_id:
                    raise ValueError(f"主材 {item.item_name} 未关联合同清单项")
                
                contract_item = self.db.query(ContractItem).filter(
                    ContractItem.id == item.contract_item_id
                ).first()
                
                if not contract_item:
                    raise ValueError(f"合同清单项 {item.contract_item_id} 不存在")
                
                # 获取该合同项的所有已批准申购数量
                total_requested = self._get_total_requested_quantity(
                    contract_item.id,
                    exclude_request_id=purchase_request.id
                )
                
                if total_requested + item.quantity > contract_item.quantity:
                    raise ValueError(
                        f"主材 {item.item_name} 申购数量超出合同限制。"
                        f"合同数量: {contract_item.quantity}, "
                        f"已申购: {total_requested}, "
                        f"本次申购: {item.quantity}"
                    )
    
    def recommend_auxiliary_materials(
        self, 
        main_material_id: int
    ) -> List[Dict[str, Any]]:
        """
        根据主材推荐相关辅材
        基于：
        1. 历史申购记录
        2. 辅材模板库
        3. 同类项目经验
        """
        recommendations = []
        
        # 1. 从历史申购记录中查找
        # 查找包含该主材的历史申购单
        historical_requests = self.db.query(PurchaseRequest).join(
            PurchaseRequestItem
        ).filter(
            and_(
                PurchaseRequestItem.contract_item_id == main_material_id,
                PurchaseRequest.status.in_([
                    PurchaseStatus.FINAL_APPROVED, 
                    PurchaseStatus.COMPLETED
                ])
            )
        ).distinct().all()
        
        auxiliary_items = {}
        for request in historical_requests:
            # 找出同一申购单中的辅材
            for item in request.items:
                if item.item_type == ItemType.AUXILIARY_MATERIAL:
                    key = f"{item.item_name}_{item.specification}"
                    if key not in auxiliary_items:
                        auxiliary_items[key] = {
                            "item_name": item.item_name,
                            "specification": item.specification,
                            "unit": item.unit,
                            "brand": item.brand,
                            "count": 0,
                            "avg_quantity": 0,
                            "source": "历史记录"
                        }
                    auxiliary_items[key]["count"] += 1
                    auxiliary_items[key]["avg_quantity"] += float(item.quantity)
        
        # 计算平均数量
        for item in auxiliary_items.values():
            item["avg_quantity"] = item["avg_quantity"] / item["count"]
            item["confidence"] = min(item["count"] / 10.0, 1.0)  # 置信度
            recommendations.append(item)
        
        # 2. 从辅材模板库中查找
        # 根据主材类型匹配模板
        contract_item = self.db.query(ContractItem).filter(
            ContractItem.id == main_material_id
        ).first()
        
        if contract_item:
            # 查找相关模板（根据项目类型或系统分类）
            templates = self.db.query(AuxiliaryTemplate).filter(
                or_(
                    AuxiliaryTemplate.project_type == contract_item.category.category_name,
                    AuxiliaryTemplate.project_type == "通用"
                )
            ).all()
            
            for template in templates:
                for template_item in template.items:
                    rec = {
                        "item_name": template_item.item_name,
                        "specification": template_item.specification,
                        "unit": template_item.unit,
                        "ratio": float(template_item.ratio) if template_item.ratio else None,
                        "is_required": template_item.is_required,
                        "reference_price": float(template_item.reference_price) if template_item.reference_price else None,
                        "source": f"模板: {template.template_name}",
                        "confidence": 0.8
                    }
                    recommendations.append(rec)
        
        # 3. 按置信度排序
        recommendations.sort(key=lambda x: x.get("confidence", 0), reverse=True)
        
        return recommendations[:20]  # 返回前20个推荐
    
    def create_auxiliary_template(
        self,
        template_data: AuxiliaryTemplateCreate,
        created_by: int
    ) -> AuxiliaryTemplate:
        """创建辅材模板"""
        # 检查模板名称是否已存在
        existing = self.db.query(AuxiliaryTemplate).filter(
            AuxiliaryTemplate.template_name == template_data.template_name
        ).first()
        
        if existing:
            raise ValueError(f"模板名称 {template_data.template_name} 已存在")
        
        # 创建模板
        template = AuxiliaryTemplate(
            template_name=template_data.template_name,
            project_type=template_data.project_type,
            description=template_data.description,
            created_by=created_by
        )
        self.db.add(template)
        self.db.flush()
        
        # 创建模板明细
        for idx, item_data in enumerate(template_data.items):
            item = AuxiliaryTemplateItem(
                template_id=template.id,
                item_name=item_data.item_name,
                specification=item_data.specification,
                unit=item_data.unit,
                ratio=item_data.ratio,
                is_required=item_data.is_required,
                reference_price=item_data.reference_price,
                remarks=item_data.remarks,
                sort_order=item_data.sort_order or idx
            )
            self.db.add(item)
        
        self.db.commit()
        self.db.refresh(template)
        
        return template
    
    def _generate_request_code(self) -> str:
        """生成申购单号"""
        today = datetime.now()
        prefix = f"PR{today.strftime('%Y%m%d')}"
        
        # 查找今天的最大序号
        last_request = self.db.query(PurchaseRequest).filter(
            PurchaseRequest.request_code.like(f"{prefix}%")
        ).order_by(PurchaseRequest.request_code.desc()).first()
        
        if last_request:
            # 提取序号并加1
            last_seq = int(last_request.request_code[-4:])
            seq = str(last_seq + 1).zfill(4)
        else:
            seq = "0001"
        
        return f"{prefix}{seq}"
    
    def _get_total_requested_quantity(
        self, 
        contract_item_id: int,
        exclude_request_id: Optional[int] = None
    ) -> Decimal:
        """
        获取某个合同清单项的累计已申购数量
        只统计已批准和已完成的申购单
        """
        query = self.db.query(
            func.sum(PurchaseRequestItem.quantity)
        ).join(
            PurchaseRequest
        ).filter(
            and_(
                PurchaseRequestItem.contract_item_id == contract_item_id,
                PurchaseRequest.status.in_([
                    PurchaseStatus.DEPT_APPROVED,
                    PurchaseStatus.FINAL_APPROVED,
                    PurchaseStatus.COMPLETED
                ])
            )
        )
        
        if exclude_request_id:
            query = query.filter(PurchaseRequest.id != exclude_request_id)
        
        total = query.scalar()
        
        return Decimal(total or 0)
    
    def get_purchase_statistics(self, project_id: int) -> Dict[str, Any]:
        """获取项目采购统计信息"""
        stats = {
            "total_requests": 0,
            "pending_approval": 0,
            "approved": 0,
            "total_amount": Decimal(0),
            "main_material_amount": Decimal(0),
            "auxiliary_material_amount": Decimal(0)
        }
        
        # 统计申购单数量
        requests = self.db.query(PurchaseRequest).filter(
            PurchaseRequest.project_id == project_id
        ).all()
        
        stats["total_requests"] = len(requests)
        
        for request in requests:
            if request.status in [PurchaseStatus.SUBMITTED, PurchaseStatus.PRICE_QUOTED]:
                stats["pending_approval"] += 1
            elif request.status in [PurchaseStatus.FINAL_APPROVED, PurchaseStatus.COMPLETED]:
                stats["approved"] += 1
                
                if request.total_amount:
                    stats["total_amount"] += request.total_amount
                    
                    # 分类统计金额
                    for item in request.items:
                        if item.total_price:
                            if item.item_type == ItemType.MAIN_MATERIAL:
                                stats["main_material_amount"] += item.total_price
                            else:
                                stats["auxiliary_material_amount"] += item.total_price
        
        return stats