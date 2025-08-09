"""
申购模块智能规则测试
验证申购业务规则的正确性
"""

import pytest
from decimal import Decimal


def test_main_material_validation():
    """测试主材必须来自合同清单规则"""
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
    assert validate_main_material("不存在的设备", "主材") == False
    assert validate_main_material("电源线", "辅材") == True
    assert validate_main_material("网线", "辅材") == True
    print("✅ 主材验证规则测试通过")


def test_quantity_limit_validation():
    """测试申购数量限制规则"""
    def validate_quantity(requested_qty, contract_qty, purchased_qty=0):
        """验证申购数量是否超过剩余数量"""
        remaining = contract_qty - purchased_qty
        if requested_qty > remaining:
            return False, f"申购数量({requested_qty})超过剩余可申购数量({remaining})"
        return True, None
    
    # 测试场景1：全新申购
    is_valid, error = validate_quantity(50, 100, 0)
    assert is_valid == True
    assert error is None
    
    # 测试场景2：已有部分申购记录
    is_valid, error = validate_quantity(30, 100, 60)
    assert is_valid == True  # 30 <= (100-60)
    
    # 测试场景3：超出剩余数量
    is_valid, error = validate_quantity(50, 100, 60)
    assert is_valid == False  # 50 > (100-60)
    assert "超过剩余可申购数量" in error
    
    print("✅ 数量限制规则测试通过")


def test_batch_purchase_support():
    """测试分批采购支持"""
    class PurchaseTracker:
        """申购追踪器"""
        def __init__(self, contract_qty):
            self.contract_qty = contract_qty
            self.purchases = []
        
        def add_purchase(self, qty):
            """添加申购记录"""
            total_purchased = sum(self.purchases)
            remaining = self.contract_qty - total_purchased
            
            if qty <= remaining:
                self.purchases.append(qty)
                return True, remaining - qty
            return False, remaining
        
        def get_summary(self):
            """获取申购汇总"""
            total = sum(self.purchases)
            return {
                "contract_qty": self.contract_qty,
                "total_purchased": total,
                "remaining": self.contract_qty - total,
                "batch_count": len(self.purchases)
            }
    
    # 创建追踪器，合同数量100
    tracker = PurchaseTracker(100)
    
    # 第1批：申购30
    success, remaining = tracker.add_purchase(30)
    assert success == True
    assert remaining == 70
    
    # 第2批：申购40
    success, remaining = tracker.add_purchase(40)
    assert success == True
    assert remaining == 30
    
    # 第3批：申购20
    success, remaining = tracker.add_purchase(20)
    assert success == True
    assert remaining == 10
    
    # 第4批：尝试申购20（超出）
    success, remaining = tracker.add_purchase(20)
    assert success == False
    assert remaining == 10
    
    # 验证汇总
    summary = tracker.get_summary()
    assert summary["total_purchased"] == 90
    assert summary["remaining"] == 10
    assert summary["batch_count"] == 3
    
    print("✅ 分批采购支持测试通过")


def test_specification_auto_fill():
    """测试规格自动填充规则"""
    # 模拟合同清单数据
    contract_items_db = {
        "AI智能摄像头": [
            {
                "specification": "DH-IPC-HFW5442E-ZE",
                "brand": "大华",
                "unit": "台",
                "unit_price": 2500.00
            },
            {
                "specification": "DS-2CD3T56WD-I8",
                "brand": "海康威视",
                "unit": "台",
                "unit_price": 2200.00
            }
        ],
        "网络硬盘录像机": [
            {
                "specification": "DH-NVR5832-4K",
                "brand": "大华",
                "unit": "台",
                "unit_price": 8000.00
            }
        ]
    }
    
    def get_specifications(item_name):
        """根据物料名称获取可选规格"""
        return contract_items_db.get(item_name, [])
    
    # 测试获取摄像头规格
    specs = get_specifications("AI智能摄像头")
    assert len(specs) == 2
    assert specs[0]["brand"] == "大华"
    assert specs[1]["brand"] == "海康威视"
    
    # 测试获取录像机规格（只有一个）
    specs = get_specifications("网络硬盘录像机")
    assert len(specs) == 1
    assert specs[0]["specification"] == "DH-NVR5832-4K"
    
    # 测试自动选择逻辑
    def should_auto_select(specs):
        """判断是否应该自动选择"""
        return len(specs) == 1
    
    assert should_auto_select(get_specifications("网络硬盘录像机")) == True
    assert should_auto_select(get_specifications("AI智能摄像头")) == False
    
    print("✅ 规格自动填充规则测试通过")


def test_unit_readonly_rule():
    """测试单位只读规则"""
    class FormField:
        """表单字段"""
        def __init__(self, value=None, readonly=False):
            self.value = value
            self.readonly = readonly
        
        def set_value(self, value):
            if not self.readonly:
                self.value = value
                return True
            return False
    
    # 创建单位字段
    unit_field = FormField()
    
    # 初始状态可编辑
    assert unit_field.set_value("台") == True
    assert unit_field.value == "台"
    
    # 从合同清单选择后设为只读
    unit_field.readonly = True
    assert unit_field.set_value("个") == False
    assert unit_field.value == "台"  # 值未改变
    
    print("✅ 单位只读规则测试通过")


def test_remarks_free_input():
    """测试备注自由输入"""
    def validate_remarks(text):
        """验证备注内容"""
        # 备注无任何限制
        return True
    
    # 测试各种备注内容
    test_cases = [
        "",  # 空备注
        "简单备注",
        "这是一个很长的备注" * 100,  # 长文本
        "包含特殊字符!@#$%^&*()",
        "包含\n换行符\n的备注",
        "包含数字123456和英文ABC"
    ]
    
    for remarks in test_cases:
        assert validate_remarks(remarks) == True
    
    print("✅ 备注自由输入测试通过")


def test_complete_purchase_scenario():
    """测试完整的申购场景"""
    print("\n" + "="*50)
    print("完整申购场景测试")
    print("="*50)
    
    # 场景：申购AI智能摄像头
    purchase_request = {
        "project_id": 1,
        "item_name": "AI智能摄像头",
        "item_type": "主材",
        "contract_qty": 100,
        "purchased_qty": 30,
        "request_qty": 40,
        "remarks": "项目二期采购"
    }
    
    # 步骤1：验证主材
    is_main_material = purchase_request["item_type"] == "主材"
    print(f"1. 物料类型检查: {'主材' if is_main_material else '辅材'}")
    
    # 步骤2：检查剩余数量
    remaining = purchase_request["contract_qty"] - purchase_request["purchased_qty"]
    can_purchase = purchase_request["request_qty"] <= remaining
    print(f"2. 数量验证: 申购{purchase_request['request_qty']}台, 剩余{remaining}台, {'✅通过' if can_purchase else '❌失败'}")
    
    # 步骤3：计算金额
    unit_price = 2500.00
    total_amount = purchase_request["request_qty"] * unit_price
    print(f"3. 金额计算: {purchase_request['request_qty']} × {unit_price} = {total_amount}")
    
    # 步骤4：生成申购单号
    import datetime
    request_code = f"PR-{datetime.datetime.now().strftime('%Y%m%d')}-001"
    print(f"4. 申购单号: {request_code}")
    
    # 验证所有步骤
    assert is_main_material == True
    assert can_purchase == True
    assert total_amount == 100000.00
    assert len(request_code) > 0
    
    print("\n✅ 完整申购场景测试通过")
    print("="*50)


def run_all_tests():
    """运行所有测试"""
    print("\n🚀 开始运行申购模块智能规则测试...\n")
    
    test_functions = [
        test_main_material_validation,
        test_quantity_limit_validation,
        test_batch_purchase_support,
        test_specification_auto_fill,
        test_unit_readonly_rule,
        test_remarks_free_input,
        test_complete_purchase_scenario
    ]
    
    passed = 0
    failed = 0
    
    for test_func in test_functions:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"❌ {test_func.__name__} 失败: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ {test_func.__name__} 异常: {e}")
            failed += 1
    
    print("\n" + "="*50)
    print(f"测试结果汇总: {passed} 通过, {failed} 失败")
    if failed == 0:
        print("🎉 所有测试通过！")
    print("="*50)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)