"""
申购单验证功能单元测试
测试申购单保存前的剩余数量验证逻辑
"""

import pytest
from decimal import Decimal
from unittest.mock import Mock, patch


class TestPurchaseValidation:
    """申购单验证功能测试类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        # 模拟合同清单项数据
        self.contract_items = [
            {
                "id": 1,
                "item_name": "室外人脸抓拍枪式摄像机",
                "specification": "DH-SH-HFS9541P-I",
                "brand_model": "大华",
                "unit": "台",
                "quantity": 15,
                "purchased_quantity": 5,  # 已申购5台
                "remaining_quantity": 10  # 剩余10台
            },
            {
                "id": 2,
                "item_name": "AI智能摄像头",
                "specification": "DH-IPC-HFW5442E-ZE",
                "brand_model": "大华",
                "unit": "台", 
                "quantity": 100,
                "purchased_quantity": 30,
                "remaining_quantity": 70
            },
            {
                "id": 3,
                "item_name": "网络硬盘录像机",
                "specification": "DH-NVR5832-4K",
                "brand_model": "大华",
                "unit": "台",
                "quantity": 5,
                "purchased_quantity": 5,  # 已全部申购完
                "remaining_quantity": 0
            }
        ]
    
    def test_validation_logic_sufficient_quantity(self):
        """测试剩余数量充足时的验证逻辑"""
        print("\n✅ 测试剩余数量充足时的验证...")
        
        def validate_purchase_items(items, contract_items):
            """验证申购明细项的剩余数量"""
            problematic_items = []
            
            for item in items:
                if item.get('item_type') == 'main':
                    # 查找对应的合同清单项
                    contract_item = None
                    for ci in contract_items:
                        if (ci['item_name'] == item['item_name'] and 
                            ci['specification'] == item['specification']):
                            contract_item = ci
                            break
                    
                    if contract_item:
                        remaining = contract_item['remaining_quantity']
                        requested = item['quantity']
                        
                        if remaining <= 0 or requested > remaining:
                            problematic_items.append({
                                'item_name': item['item_name'],
                                'requested': requested,
                                'remaining': remaining,
                                'error': f'申购数量({requested})超过剩余数量({remaining})'
                            })
            
            return len(problematic_items) == 0, problematic_items
        
        # 测试数据：申购数量在剩余范围内
        valid_items = [
            {
                'item_name': 'AI智能摄像头',
                'specification': 'DH-IPC-HFW5442E-ZE',
                'quantity': 30,  # 小于剩余数量70
                'item_type': 'main'
            },
            {
                'item_name': '电源适配器',  # 辅材，不需要验证
                'specification': '12V 2A',
                'quantity': 50,
                'item_type': 'auxiliary'
            }
        ]
        
        is_valid, errors = validate_purchase_items(valid_items, self.contract_items)
        
        assert is_valid == True
        assert len(errors) == 0
        print("   ✅ 剩余数量充足时验证通过")
    
    def test_validation_logic_insufficient_quantity(self):
        """测试剩余数量不足时的验证逻辑"""
        print("\n❌ 测试剩余数量不足时的验证...")
        
        def validate_purchase_items(items, contract_items):
            """验证申购明细项的剩余数量"""
            problematic_items = []
            
            for item in items:
                if item.get('item_type') == 'main':
                    contract_item = None
                    for ci in contract_items:
                        if (ci['item_name'] == item['item_name'] and 
                            ci['specification'] == item['specification']):
                            contract_item = ci
                            break
                    
                    if contract_item:
                        remaining = contract_item['remaining_quantity']
                        requested = item['quantity']
                        
                        if remaining <= 0 or requested > remaining:
                            problematic_items.append({
                                'item_name': item['item_name'],
                                'requested': requested,
                                'remaining': remaining,
                                'error': f'申购数量({requested})超过剩余数量({remaining})'
                            })
            
            return len(problematic_items) == 0, problematic_items
        
        # 测试数据：申购数量超过剩余数量
        invalid_items = [
            {
                'item_name': '室外人脸抓拍枪式摄像机',
                'specification': 'DH-SH-HFS9541P-I',
                'quantity': 15,  # 超过剩余数量10
                'item_type': 'main'
            },
            {
                'item_name': '网络硬盘录像机',
                'specification': 'DH-NVR5832-4K', 
                'quantity': 1,  # 剩余数量为0
                'item_type': 'main'
            }
        ]
        
        is_valid, errors = validate_purchase_items(invalid_items, self.contract_items)
        
        assert is_valid == False
        assert len(errors) == 2
        assert errors[0]['item_name'] == '室外人脸抓拍枪式摄像机'
        assert errors[0]['requested'] == 15
        assert errors[0]['remaining'] == 10
        assert errors[1]['item_name'] == '网络硬盘录像机'
        assert errors[1]['remaining'] == 0
        print("   ✅ 剩余数量不足时正确识别问题")
    
    def test_validation_error_message_formatting(self):
        """测试验证错误信息格式化"""
        print("\n📝 测试验证错误信息格式化...")
        
        def format_validation_error_message(errors):
            """格式化验证错误信息"""
            if not errors:
                return ""
            
            item_list = []
            for i, error in enumerate(errors, 1):
                item_list.append(
                    f"{i}. {error['item_name']} - "
                    f"申购: {error['requested']}, "
                    f"剩余: {error['remaining']}"
                )
            
            message = (
                "申购数量验证失败！\n\n"
                "以下物料的剩余可申购数量不足：\n\n" +
                '\n'.join(item_list) +
                "\n\n请调整申购数量后再保存。"
            )
            
            return message
        
        # 模拟验证错误
        test_errors = [
            {
                'item_name': '室外人脸抓拍枪式摄像机',
                'requested': 15,
                'remaining': 10
            },
            {
                'item_name': '网络硬盘录像机',
                'requested': 1,
                'remaining': 0
            }
        ]
        
        message = format_validation_error_message(test_errors)
        
        assert "申购数量验证失败" in message
        assert "室外人脸抓拍枪式摄像机" in message
        assert "申购: 15, 剩余: 10" in message
        assert "网络硬盘录像机" in message
        assert "申购: 1, 剩余: 0" in message
        assert "请调整申购数量后再保存" in message
        print("   ✅ 错误信息格式化正确")
    
    def test_validation_auxiliary_materials_skip(self):
        """测试辅材不参与验证的逻辑"""
        print("\n🔄 测试辅材跳过验证逻辑...")
        
        def validate_purchase_items(items, contract_items):
            """验证申购明细项，辅材跳过验证"""
            problematic_items = []
            
            for item in items:
                # 只验证主材
                if item.get('item_type') == 'main':
                    contract_item = None
                    for ci in contract_items:
                        if (ci['item_name'] == item['item_name'] and 
                            ci['specification'] == item['specification']):
                            contract_item = ci
                            break
                    
                    if contract_item:
                        remaining = contract_item['remaining_quantity']
                        requested = item['quantity']
                        
                        if remaining <= 0 or requested > remaining:
                            problematic_items.append({
                                'item_name': item['item_name'],
                                'requested': requested,
                                'remaining': remaining
                            })
                # 辅材直接跳过验证
                elif item.get('item_type') == 'auxiliary':
                    continue
            
            return len(problematic_items) == 0, problematic_items
        
        # 测试数据：包含主材和辅材
        mixed_items = [
            {
                'item_name': '网络硬盘录像机',  # 主材，剩余数量为0
                'specification': 'DH-NVR5832-4K',
                'quantity': 1,
                'item_type': 'main'
            },
            {
                'item_name': '电源线',  # 辅材，数量很大但应该跳过验证
                'specification': '3米',
                'quantity': 1000,
                'item_type': 'auxiliary'
            },
            {
                'item_name': '安装支架',  # 辅材
                'specification': '通用型',
                'quantity': 500,
                'item_type': 'auxiliary'
            }
        ]
        
        is_valid, errors = validate_purchase_items(mixed_items, self.contract_items)
        
        # 只有主材的数量问题被检测出来
        assert is_valid == False
        assert len(errors) == 1
        assert errors[0]['item_name'] == '网络硬盘录像机'
        
        # 确认辅材没有出现在错误列表中
        error_item_names = [e['item_name'] for e in errors]
        assert '电源线' not in error_item_names
        assert '安装支架' not in error_item_names
        print("   ✅ 辅材正确跳过验证，只检查主材")
    
    def test_validation_performance_large_dataset(self):
        """测试大数据量时的验证性能"""
        print("\n⚡ 测试大数据量验证性能...")
        
        import time
        
        def validate_purchase_items_optimized(items, contract_items):
            """优化的验证函数：使用字典索引提高查找性能"""
            # 构建合同清单项的快速查找索引
            contract_index = {}
            for ci in contract_items:
                key = f"{ci['item_name']}||{ci['specification']}"
                contract_index[key] = ci
            
            problematic_items = []
            
            for item in items:
                if item.get('item_type') == 'main':
                    key = f"{item['item_name']}||{item['specification']}"
                    contract_item = contract_index.get(key)
                    
                    if contract_item:
                        remaining = contract_item['remaining_quantity']
                        requested = item['quantity']
                        
                        if remaining <= 0 or requested > remaining:
                            problematic_items.append({
                                'item_name': item['item_name'],
                                'requested': requested,
                                'remaining': remaining
                            })
            
            return len(problematic_items) == 0, problematic_items
        
        # 生成大量测试数据
        large_contract_items = []
        large_purchase_items = []
        
        for i in range(1000):
            # 合同清单项
            large_contract_items.append({
                "id": i + 1,
                "item_name": f"设备{i}",
                "specification": f"规格{i}",
                "brand_model": "测试品牌",
                "unit": "台",
                "quantity": 100,
                "purchased_quantity": 50,
                "remaining_quantity": 50
            })
            
            # 申购明细项
            large_purchase_items.append({
                'item_name': f"设备{i}",
                'specification': f"规格{i}",
                'quantity': 30,  # 在剩余范围内
                'item_type': 'main'
            })
        
        # 添加一个超量申购的项目
        large_purchase_items[500]['quantity'] = 60  # 超过剩余数量50
        
        start_time = time.time()
        is_valid, errors = validate_purchase_items_optimized(
            large_purchase_items, large_contract_items
        )
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        assert is_valid == False
        assert len(errors) == 1
        assert errors[0]['item_name'] == "设备500"
        assert execution_time < 1.0  # 应该在1秒内完成验证
        
        print(f"   ✅ 1000个项目验证耗时: {execution_time:.4f}秒")
        print("   ✅ 大数据量验证性能良好")
    
    def test_validation_edge_cases(self):
        """测试验证边界情况"""
        print("\n🔍 测试验证边界情况...")
        
        def validate_purchase_items_robust(items, contract_items):
            """健壮的验证函数，处理各种边界情况"""
            if not items:
                return True, []
            
            if not contract_items:
                # 如果没有合同清单，主材都应该被拒绝
                main_items = [item for item in items if item.get('item_type') == 'main']
                if main_items:
                    return False, [{'error': '没有合同清单数据，无法验证主材'}]
                return True, []
            
            problematic_items = []
            
            for item in items:
                if item.get('item_type') == 'main':
                    # 处理 None 值和缺失字段
                    item_name = item.get('item_name', '').strip()
                    specification = item.get('specification', '').strip()
                    quantity = item.get('quantity', 0)
                    
                    if not item_name or not specification:
                        problematic_items.append({
                            'error': f'主材信息不完整: 名称="{item_name}", 规格="{specification}"'
                        })
                        continue
                    
                    if quantity <= 0:
                        problematic_items.append({
                            'item_name': item_name,
                            'error': '申购数量必须大于0'
                        })
                        continue
                    
                    # 查找合同清单项
                    contract_item = None
                    for ci in contract_items:
                        if (ci.get('item_name', '').strip() == item_name and 
                            ci.get('specification', '').strip() == specification):
                            contract_item = ci
                            break
                    
                    if not contract_item:
                        problematic_items.append({
                            'item_name': item_name,
                            'error': '主材不在合同清单中'
                        })
                        continue
                    
                    remaining = contract_item.get('remaining_quantity', 0)
                    if remaining is None:
                        remaining = 0
                    
                    if remaining <= 0 or quantity > remaining:
                        problematic_items.append({
                            'item_name': item_name,
                            'requested': quantity,
                            'remaining': remaining,
                            'error': f'申购数量({quantity})超过剩余数量({remaining})'
                        })
            
            return len(problematic_items) == 0, problematic_items
        
        # 测试场景1：空列表
        is_valid, errors = validate_purchase_items_robust([], self.contract_items)
        assert is_valid == True
        assert len(errors) == 0
        
        # 测试场景2：缺失字段的项目
        incomplete_items = [
            {
                'item_name': '',  # 空名称
                'specification': 'DH-IPC-HFW5442E-ZE',
                'quantity': 10,
                'item_type': 'main'
            },
            {
                'item_name': 'AI智能摄像头',
                'specification': '',  # 空规格
                'quantity': 5,
                'item_type': 'main'
            }
        ]
        
        is_valid, errors = validate_purchase_items_robust(incomplete_items, self.contract_items)
        assert is_valid == False
        assert len(errors) == 2
        assert any('信息不完整' in e.get('error', '') for e in errors)
        
        # 测试场景3：数量为0或负数
        zero_quantity_items = [
            {
                'item_name': 'AI智能摄像头',
                'specification': 'DH-IPC-HFW5442E-ZE',
                'quantity': 0,
                'item_type': 'main'
            },
            {
                'item_name': '室外人脸抓拍枪式摄像机',
                'specification': 'DH-SH-HFS9541P-I',
                'quantity': -5,
                'item_type': 'main'
            }
        ]
        
        is_valid, errors = validate_purchase_items_robust(zero_quantity_items, self.contract_items)
        assert is_valid == False
        assert len(errors) == 2
        assert all('必须大于0' in e.get('error', '') for e in errors)
        
        print("   ✅ 所有边界情况处理正确")


class TestPurchaseValidationIntegration:
    """申购单验证集成测试"""
    
    def test_frontend_backend_validation_sync(self):
        """测试前后端验证逻辑同步"""
        print("\n🔄 测试前后端验证逻辑同步...")
        
        def frontend_validation(items):
            """模拟前端验证逻辑"""
            problematic_items = []
            
            for item in items:
                if item.get('item_type') == 'main':
                    remaining = item.get('remaining_quantity', 0)
                    requested = item.get('quantity', 0)
                    
                    if remaining is not None and (remaining <= 0 or requested > remaining):
                        problematic_items.append({
                            'item_name': item['item_name'],
                            'requested': requested,
                            'remaining': remaining
                        })
            
            return len(problematic_items) == 0, problematic_items
        
        def backend_validation(items, contract_items):
            """模拟后端验证逻辑"""
            problematic_items = []
            
            for item in items:
                if item.get('item_type') == 'main':
                    # 查找合同清单项
                    contract_item = None
                    for ci in contract_items:
                        if (ci['item_name'] == item['item_name'] and 
                            ci['specification'] == item['specification']):
                            contract_item = ci
                            break
                    
                    if contract_item:
                        remaining = contract_item['remaining_quantity']
                        requested = item['quantity']
                        
                        if remaining <= 0 or requested > remaining:
                            problematic_items.append({
                                'item_name': item['item_name'],
                                'requested': requested,
                                'remaining': remaining
                            })
            
            return len(problematic_items) == 0, problematic_items
        
        # 测试数据：前端项目（包含剩余数量信息）
        frontend_items = [
            {
                'item_name': '室外人脸抓拍枪式摄像机',
                'specification': 'DH-SH-HFS9541P-I',
                'quantity': 15,
                'remaining_quantity': 10,  # 前端已知剩余数量
                'item_type': 'main'
            }
        ]
        
        # 后端数据：合同清单项
        backend_contract_items = [
            {
                "item_name": "室外人脸抓拍枪式摄像机",
                "specification": "DH-SH-HFS9541P-I",
                "remaining_quantity": 10
            }
        ]
        
        # 测试前后端验证结果一致性
        frontend_valid, frontend_errors = frontend_validation(frontend_items)
        backend_valid, backend_errors = backend_validation(frontend_items, backend_contract_items)
        
        assert frontend_valid == backend_valid
        assert len(frontend_errors) == len(backend_errors)
        
        if frontend_errors and backend_errors:
            assert frontend_errors[0]['item_name'] == backend_errors[0]['item_name']
            assert frontend_errors[0]['requested'] == backend_errors[0]['requested']
            assert frontend_errors[0]['remaining'] == backend_errors[0]['remaining']
        
        print("   ✅ 前后端验证逻辑保持一致")


def run_validation_tests():
    """运行所有验证测试"""
    print("🚀 开始运行申购单验证功能测试...")
    print("=" * 60)
    
    test_instance = TestPurchaseValidation()
    integration_instance = TestPurchaseValidationIntegration()
    
    test_methods = [
        test_instance.test_validation_logic_sufficient_quantity,
        test_instance.test_validation_logic_insufficient_quantity,
        test_instance.test_validation_error_message_formatting,
        test_instance.test_validation_auxiliary_materials_skip,
        test_instance.test_validation_performance_large_dataset,
        test_instance.test_validation_edge_cases,
        integration_instance.test_frontend_backend_validation_sync
    ]
    
    passed = 0
    failed = 0
    
    for test_method in test_methods:
        try:
            if hasattr(test_instance, 'setup_method'):
                test_instance.setup_method()
            test_method()
            passed += 1
        except AssertionError as e:
            print(f"❌ 测试失败: {test_method.__name__} - {e}")
            failed += 1
        except Exception as e:
            print(f"💥 测试错误: {test_method.__name__} - {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 验证功能测试结果: {passed} 通过, {failed} 失败")
    
    return failed == 0


if __name__ == "__main__":
    success = run_validation_tests()
    exit(0 if success else 1)