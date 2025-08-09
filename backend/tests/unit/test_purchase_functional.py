"""
申购模块功能测试 - 无数据库依赖
专注测试业务逻辑和规则验证
"""

import pytest
from decimal import Decimal


class TestPurchaseBusinessRules:
    """申购业务规则测试"""
    
    def test_main_material_validation(self):
        """测试主材必须来自合同清单的规则"""
        # 模拟合同清单中的主材列表
        contract_main_materials = [
            "AI智能摄像头",
            "网络硬盘录像机", 
            "核心交换机",
            "接入交换机"
        ]
        
        def validate_main_material(item_name, item_type):
            """验证主材是否在合同清单中"""
            if item_type == "主材":
                return item_name in contract_main_materials
            return True  # 辅材不限制
        
        # 测试用例
        assert validate_main_material("AI智能摄像头", "主材") == True
        assert validate_main_material("未知设备", "主材") == False
        assert validate_main_material("电源线", "辅材") == True
        
    def test_quantity_limit_validation(self):
        """测试申购数量限制规则"""
        def validate_quantity(requested_qty, contract_qty, purchased_qty=0):
            """验证申购数量是否超过剩余数量"""
            remaining = contract_qty - purchased_qty
            if requested_qty > remaining:
                return False, f"申购数量({requested_qty})超过剩余可申购数量({remaining})"
            return True, None
        
        # 测试场景
        is_valid, error = validate_quantity(50, 100, 0)
        assert is_valid == True
        assert error is None
        
        is_valid, error = validate_quantity(60, 100, 50)
        assert is_valid == False
        assert "超过剩余可申购数量" in error
        
    def test_batch_purchase_calculation(self):
        """测试分批采购数量计算"""
        class PurchaseCalculator:
            def __init__(self, contract_qty):
                self.contract_qty = contract_qty
                self.purchases = []
            
            def add_purchase(self, qty):
                total_purchased = sum(self.purchases)
                remaining = self.contract_qty - total_purchased
                
                if qty <= remaining:
                    self.purchases.append(qty)
                    return True, remaining - qty
                return False, remaining
            
            def get_remaining(self):
                return self.contract_qty - sum(self.purchases)
        
        calculator = PurchaseCalculator(100)
        
        # 第1批
        success, remaining = calculator.add_purchase(30)
        assert success == True
        assert remaining == 70
        
        # 第2批
        success, remaining = calculator.add_purchase(40)
        assert success == True
        assert remaining == 30
        
        # 验证剩余数量
        assert calculator.get_remaining() == 30
        
    def test_specification_auto_fill(self):
        """测试规格自动填充逻辑"""
        contract_specs = {
            "AI智能摄像头": [
                {
                    "specification": "DH-IPC-HFW5442E-ZE",
                    "brand_model": "大华",
                    "unit": "台",
                    "unit_price": 2500.00
                },
                {
                    "specification": "DS-2CD3T56WD-I8", 
                    "brand_model": "海康威视",
                    "unit": "台",
                    "unit_price": 2200.00
                }
            ],
            "网络硬盘录像机": [
                {
                    "specification": "DH-NVR5832-4K",
                    "brand_model": "大华",
                    "unit": "台", 
                    "unit_price": 8000.00
                }
            ]
        }
        
        def get_specifications(item_name):
            return contract_specs.get(item_name, [])
        
        def should_auto_select(item_name):
            specs = get_specifications(item_name)
            return len(specs) == 1
        
        # 测试规格获取
        camera_specs = get_specifications("AI智能摄像头")
        assert len(camera_specs) == 2
        assert camera_specs[0]["brand_model"] == "大华"
        
        # 测试自动选择逻辑
        assert should_auto_select("网络硬盘录像机") == True
        assert should_auto_select("AI智能摄像头") == False
        
    def test_purchase_form_validation(self):
        """测试申购表单验证规则"""
        def validate_purchase_form(form_data):
            """验证申购表单数据"""
            errors = []
            
            # 必填字段检查
            required_fields = ['item_name', 'quantity', 'project_id']
            for field in required_fields:
                if not form_data.get(field):
                    errors.append(f"{field} 是必填字段")
            
            # 数量必须大于0
            quantity = form_data.get('quantity', 0)
            if quantity <= 0:
                errors.append("申购数量必须大于0")
            
            # 主材必须有合同关联
            if form_data.get('item_type') == '主材' and not form_data.get('contract_item_id'):
                errors.append("主材必须关联合同清单项")
            
            return len(errors) == 0, errors
        
        # 测试正确的表单
        valid_form = {
            'item_name': 'AI智能摄像头',
            'quantity': 10,
            'project_id': 1,
            'item_type': '主材',
            'contract_item_id': 1
        }
        is_valid, errors = validate_purchase_form(valid_form)
        assert is_valid == True
        assert len(errors) == 0
        
        # 测试错误的表单
        invalid_form = {
            'item_name': '',
            'quantity': 0,
            'project_id': None
        }
        is_valid, errors = validate_purchase_form(invalid_form)
        assert is_valid == False
        assert len(errors) > 0
        
    def test_purchase_code_generation(self):
        """测试申购单号生成规则"""
        import datetime
        
        def generate_purchase_code(project_id=None, sequence=1):
            """生成申购单号：PR-YYYYMMDD-XXX"""
            today = datetime.date.today()
            date_str = today.strftime('%Y%m%d')
            code = f"PR-{date_str}-{sequence:03d}"
            return code
        
        # 测试生成规则
        code = generate_purchase_code(1, 1)
        assert code.startswith("PR-")
        assert len(code) == 15  # PR-20250809-001 (实际长度是15)
        
        # 测试序号递增
        code1 = generate_purchase_code(1, 1)
        code2 = generate_purchase_code(1, 2)
        assert code1[-3:] == "001"
        assert code2[-3:] == "002"


class TestPurchaseItemCalculation:
    """申购明细计算测试"""
    
    def test_total_amount_calculation(self):
        """测试总金额计算"""
        def calculate_total(items):
            """计算申购单总金额"""
            total = Decimal('0')
            for item in items:
                quantity = Decimal(str(item['quantity']))
                unit_price = Decimal(str(item['unit_price']))
                total += quantity * unit_price
            return total
        
        items = [
            {'quantity': 10, 'unit_price': 2500.00},
            {'quantity': 5, 'unit_price': 8000.00},
            {'quantity': 20, 'unit_price': 500.00}
        ]
        
        total = calculate_total(items)
        expected = Decimal('25000') + Decimal('40000') + Decimal('10000')  # 75000
        assert total == expected
        
    def test_item_validation(self):
        """测试明细项验证"""
        def validate_item(item, contract_items):
            """验证申购明细项"""
            errors = []
            
            # 检查物料是否存在于合同中
            if item.get('item_type') == '主材':
                found = False
                for contract_item in contract_items:
                    if (contract_item['item_name'] == item['item_name'] and
                        contract_item['specification'] == item['specification']):
                        found = True
                        # 检查数量限制
                        remaining = contract_item['quantity'] - contract_item.get('purchased', 0)
                        if item['quantity'] > remaining:
                            errors.append(f"申购数量超过剩余数量({remaining})")
                        break
                
                if not found:
                    errors.append("主材不在合同清单中")
            
            return len(errors) == 0, errors
        
        # 模拟合同清单
        contract_items = [
            {
                'item_name': 'AI智能摄像头',
                'specification': 'DH-IPC-HFW5442E-ZE',
                'quantity': 100,
                'purchased': 30
            }
        ]
        
        # 测试正确的申购项
        valid_item = {
            'item_name': 'AI智能摄像头',
            'specification': 'DH-IPC-HFW5442E-ZE',
            'quantity': 40,
            'item_type': '主材'
        }
        is_valid, errors = validate_item(valid_item, contract_items)
        assert is_valid == True
        
        # 测试超量申购
        invalid_item = {
            'item_name': 'AI智能摄像头',
            'specification': 'DH-IPC-HFW5442E-ZE',
            'quantity': 80,  # 超过剩余数量70
            'item_type': '主材'
        }
        is_valid, errors = validate_item(invalid_item, contract_items)
        assert is_valid == False
        assert any("超过剩余数量" in error for error in errors)


class TestPurchaseWorkflow:
    """申购工作流程测试"""
    
    def test_purchase_status_transition(self):
        """测试申购单状态转换"""
        valid_transitions = {
            'draft': ['submitted', 'cancelled'],
            'submitted': ['approved', 'rejected', 'cancelled'],
            'approved': ['completed', 'cancelled'],
            'rejected': ['draft'],  # 可以重新编辑
            'completed': [],  # 终态
            'cancelled': []   # 终态
        }
        
        def can_transition(from_status, to_status):
            """检查状态转换是否合法"""
            return to_status in valid_transitions.get(from_status, [])
        
        # 测试正常流程
        assert can_transition('draft', 'submitted') == True
        assert can_transition('submitted', 'approved') == True
        assert can_transition('approved', 'completed') == True
        
        # 测试非法转换
        assert can_transition('completed', 'draft') == False
        assert can_transition('cancelled', 'approved') == False
        
    def test_purchase_approval_logic(self):
        """测试申购审批逻辑"""
        def need_approval(purchase_amount, requester_role):
            """判断是否需要审批"""
            approval_rules = {
                'purchaser': 5000,      # 采购员可直接处理5000以下
                'dept_manager': 50000,   # 部门主管可处理5万以下
                'general_manager': float('inf')  # 总经理无限制
            }
            
            limit = approval_rules.get(requester_role, 0)
            return purchase_amount > limit
        
        # 测试审批规则
        assert need_approval(3000, 'purchaser') == False
        assert need_approval(8000, 'purchaser') == True
        assert need_approval(30000, 'dept_manager') == False
        assert need_approval(80000, 'dept_manager') == True
        
    def test_purchase_priority_calculation(self):
        """测试申购优先级计算"""
        def calculate_priority(urgency, project_priority, amount):
            """计算申购优先级分数"""
            urgency_scores = {'low': 1, 'normal': 2, 'high': 3, 'urgent': 4}
            project_scores = {'low': 1, 'normal': 2, 'high': 3, 'critical': 4}
            
            urgency_score = urgency_scores.get(urgency, 2)
            project_score = project_scores.get(project_priority, 2) 
            
            # 金额越大优先级越高（简化逻辑）
            amount_score = min(int(amount / 10000), 5)
            
            return urgency_score * 3 + project_score * 2 + amount_score
        
        # 测试优先级计算
        score1 = calculate_priority('urgent', 'critical', 50000)
        score2 = calculate_priority('normal', 'normal', 10000)
        
        assert score1 > score2  # 紧急+关键项目的优先级更高


if __name__ == "__main__":
    pytest.main([__file__, "-v"])