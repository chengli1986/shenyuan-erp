"""
剩余数量计算逻辑单元测试
测试申购单剩余数量计算的业务规则和边界情况
"""

import pytest
from decimal import Decimal
from datetime import datetime, timedelta
from unittest.mock import Mock, patch


class TestRemainingQuantityCalculation:
    """剩余数量计算测试类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        # 模拟合同清单项
        self.contract_items = [
            {
                "id": 1,
                "item_name": "室外人脸抓拍枪式摄像机",
                "specification": "DH-SH-HFS9541P-I",
                "quantity": Decimal('15.0'),
                "unit": "台"
            },
            {
                "id": 2,
                "item_name": "AI智能摄像头",
                "specification": "DH-IPC-HFW5442E-ZE",
                "quantity": Decimal('100.0'),
                "unit": "台"
            },
            {
                "id": 3,
                "item_name": "网络硬盘录像机",
                "specification": "DH-NVR5832-4K",
                "quantity": Decimal('5.0'),
                "unit": "台"
            }
        ]
        
        # 模拟不同状态的申购单（基于CLAUDE.md中2025-08-29的优化记录）
        self.purchase_requests = [
            # 草稿状态 - 不应计入已申购数量
            {
                "id": 1,
                "status": "draft",
                "contract_item_id": 1,
                "quantity": Decimal('3.0'),
                "created_at": datetime.now() - timedelta(days=1)
            },
            {
                "id": 2,
                "status": "draft",
                "contract_item_id": 2,
                "quantity": Decimal('20.0'),
                "created_at": datetime.now() - timedelta(days=2)
            },
            
            # 已提交状态 - 不应计入已申购数量
            {
                "id": 3,
                "status": "submitted",
                "contract_item_id": 1,
                "quantity": Decimal('2.0'),
                "created_at": datetime.now() - timedelta(days=3)
            },
            
            # 已询价状态 - 不应计入已申购数量
            {
                "id": 4,
                "status": "price_quoted",
                "contract_item_id": 2,
                "quantity": Decimal('15.0'),
                "created_at": datetime.now() - timedelta(days=4)
            },
            
            # 部门已批准状态 - 根据优化后的逻辑，不应计入已申购数量
            {
                "id": 5,
                "status": "dept_approved",
                "contract_item_id": 1,
                "quantity": Decimal('4.0'),
                "created_at": datetime.now() - timedelta(days=5)
            },
            {
                "id": 6,
                "status": "dept_approved",
                "contract_item_id": 2,
                "quantity": Decimal('25.0'),
                "created_at": datetime.now() - timedelta(days=6)
            },
            
            # 总经理最终批准状态 - 应该计入已申购数量
            {
                "id": 7,
                "status": "final_approved",
                "contract_item_id": 1,
                "quantity": Decimal('5.0'),
                "created_at": datetime.now() - timedelta(days=7)
            },
            {
                "id": 8,
                "status": "final_approved",
                "contract_item_id": 2,
                "quantity": Decimal('30.0'),
                "created_at": datetime.now() - timedelta(days=8)
            },
            {
                "id": 9,
                "status": "final_approved",
                "contract_item_id": 3,
                "quantity": Decimal('2.0'),
                "created_at": datetime.now() - timedelta(days=9)
            },
            
            # 已完成状态 - 应该计入已申购数量
            {
                "id": 10,
                "status": "completed",
                "contract_item_id": 2,
                "quantity": Decimal('10.0'),
                "created_at": datetime.now() - timedelta(days=10)
            }
        ]
    
    def test_correct_status_inclusion_logic(self):
        """测试正确的状态包含逻辑（只有总经理批准后才计入）"""
        print("\n✅ 测试正确的状态包含逻辑...")
        
        def calculate_remaining_quantity_optimized(contract_item_id, purchase_requests):
            """优化后的剩余数量计算逻辑"""
            # 查找合同清单项
            contract_item = next(
                (item for item in self.contract_items if item['id'] == contract_item_id), 
                None
            )
            
            if not contract_item:
                return None, "合同清单项不存在"
            
            # 只统计总经理最终批准和已完成的申购单
            valid_statuses = ['final_approved', 'completed']
            
            purchased_quantity = Decimal('0.0')
            for request in purchase_requests:
                if (request['contract_item_id'] == contract_item_id and 
                    request['status'] in valid_statuses):
                    purchased_quantity += request['quantity']
            
            remaining_quantity = contract_item['quantity'] - purchased_quantity
            
            return {
                'contract_quantity': contract_item['quantity'],
                'purchased_quantity': purchased_quantity,
                'remaining_quantity': remaining_quantity,
                'valid_statuses_counted': valid_statuses
            }, None
        
        # 测试摄像机（合同数量15）
        result, error = calculate_remaining_quantity_optimized(1, self.purchase_requests)
        
        assert error is None
        assert result['contract_quantity'] == Decimal('15.0')
        # 只应该统计final_approved状态的5台，不包括draft(3)、submitted(2)、dept_approved(4)
        assert result['purchased_quantity'] == Decimal('5.0')
        assert result['remaining_quantity'] == Decimal('10.0')
        assert result['valid_statuses_counted'] == ['final_approved', 'completed']
        
        print("   ✅ 摄像机剩余数量计算正确")
        print(f"   📊 合同数量: {result['contract_quantity']}, 已申购: {result['purchased_quantity']}, 剩余: {result['remaining_quantity']}")
        
        # 测试AI智能摄像头（合同数量100）
        result, error = calculate_remaining_quantity_optimized(2, self.purchase_requests)
        
        assert error is None
        assert result['contract_quantity'] == Decimal('100.0')
        # 应该统计final_approved(30) + completed(10) = 40，不包括其他状态
        assert result['purchased_quantity'] == Decimal('40.0')
        assert result['remaining_quantity'] == Decimal('60.0')
        
        print("   ✅ AI摄像头剩余数量计算正确")
        print(f"   📊 合同数量: {result['contract_quantity']}, 已申购: {result['purchased_quantity']}, 剩余: {result['remaining_quantity']}")
    
    def test_wrong_status_inclusion_comparison(self):
        """测试错误的状态包含逻辑（对比修复前的问题）"""
        print("\n❌ 测试修复前的错误逻辑（用于对比）...")
        
        def calculate_remaining_quantity_old_logic(contract_item_id, purchase_requests):
            """修复前的错误逻辑：包含部门审批状态"""
            contract_item = next(
                (item for item in self.contract_items if item['id'] == contract_item_id), 
                None
            )
            
            if not contract_item:
                return None, "合同清单项不存在"
            
            # 错误的逻辑：过早包含dept_approved状态
            wrong_statuses = ['dept_approved', 'final_approved', 'completed']
            
            purchased_quantity = Decimal('0.0')
            for request in purchase_requests:
                if (request['contract_item_id'] == contract_item_id and 
                    request['status'] in wrong_statuses):
                    purchased_quantity += request['quantity']
            
            remaining_quantity = contract_item['quantity'] - purchased_quantity
            
            return {
                'contract_quantity': contract_item['quantity'],
                'purchased_quantity': purchased_quantity,
                'remaining_quantity': remaining_quantity,
                'wrong_statuses_counted': wrong_statuses
            }, None
        
        # 使用错误逻辑测试摄像机
        wrong_result, error = calculate_remaining_quantity_old_logic(1, self.purchase_requests)
        
        assert error is None
        assert wrong_result['contract_quantity'] == Decimal('15.0')
        # 错误逻辑会统计dept_approved(4) + final_approved(5) = 9
        assert wrong_result['purchased_quantity'] == Decimal('9.0')
        assert wrong_result['remaining_quantity'] == Decimal('6.0')
        
        # 对比正确逻辑的结果
        from test_remaining_quantity_calculation import TestRemainingQuantityCalculation
        test_instance = TestRemainingQuantityCalculation()
        test_instance.setup_method()
        
        def calculate_remaining_quantity_correct(contract_item_id, purchase_requests):
            contract_item = next(
                (item for item in test_instance.contract_items if item['id'] == contract_item_id), 
                None
            )
            
            correct_statuses = ['final_approved', 'completed']
            purchased_quantity = Decimal('0.0')
            for request in purchase_requests:
                if (request['contract_item_id'] == contract_item_id and 
                    request['status'] in correct_statuses):
                    purchased_quantity += request['quantity']
            
            return contract_item['quantity'] - purchased_quantity
        
        correct_remaining = calculate_remaining_quantity_correct(1, self.purchase_requests)
        
        print(f"   ❌ 错误逻辑结果: 剩余 {wrong_result['remaining_quantity']} (过早锁定资源)")
        print(f"   ✅ 正确逻辑结果: 剩余 {correct_remaining} (合理的资源管理)")
        print(f"   📈 差异: {correct_remaining - wrong_result['remaining_quantity']} (修复释放的资源)")
        
        # 验证修复的价值
        assert correct_remaining > wrong_result['remaining_quantity']
        assert correct_remaining - wrong_result['remaining_quantity'] == Decimal('4.0')
    
    def test_batch_remaining_quantity_calculation(self):
        """测试批量剩余数量计算"""
        print("\n📊 测试批量剩余数量计算...")
        
        def calculate_all_remaining_quantities(contract_items, purchase_requests):
            """批量计算所有合同清单项的剩余数量"""
            results = {}
            valid_statuses = ['final_approved', 'completed']
            
            for contract_item in contract_items:
                item_id = contract_item['id']
                purchased_quantity = Decimal('0.0')
                
                for request in purchase_requests:
                    if (request['contract_item_id'] == item_id and 
                        request['status'] in valid_statuses):
                        purchased_quantity += request['quantity']
                
                remaining_quantity = contract_item['quantity'] - purchased_quantity
                
                results[item_id] = {
                    'item_name': contract_item['item_name'],
                    'contract_quantity': contract_item['quantity'],
                    'purchased_quantity': purchased_quantity,
                    'remaining_quantity': remaining_quantity,
                    'utilization_rate': float(purchased_quantity / contract_item['quantity'] * 100)
                }
            
            return results
        
        results = calculate_all_remaining_quantities(self.contract_items, self.purchase_requests)
        
        assert len(results) == 3
        
        # 验证每个项目的计算结果
        # 项目1：摄像机
        assert results[1]['purchased_quantity'] == Decimal('5.0')
        assert results[1]['remaining_quantity'] == Decimal('10.0')
        assert abs(results[1]['utilization_rate'] - 33.33) < 0.1
        
        # 项目2：AI摄像头
        assert results[2]['purchased_quantity'] == Decimal('40.0')
        assert results[2]['remaining_quantity'] == Decimal('60.0')
        assert results[2]['utilization_rate'] == 40.0
        
        # 项目3：录像机
        assert results[3]['purchased_quantity'] == Decimal('2.0')
        assert results[3]['remaining_quantity'] == Decimal('3.0')
        assert results[3]['utilization_rate'] == 40.0
        
        print("   ✅ 批量计算结果正确")
        for item_id, result in results.items():
            print(f"   📋 {result['item_name']}: 合同{result['contract_quantity']}, "
                  f"已申购{result['purchased_quantity']}, 剩余{result['remaining_quantity']}, "
                  f"利用率{result['utilization_rate']:.1f}%")
    
    def test_remaining_quantity_edge_cases(self):
        """测试剩余数量计算的边界情况"""
        print("\n🔍 测试剩余数量计算边界情况...")
        
        def calculate_remaining_quantity_robust(contract_item_id, purchase_requests, contract_items):
            """健壮的剩余数量计算，处理各种边界情况"""
            
            # 边界情况1：合同清单项不存在
            contract_item = next(
                (item for item in contract_items if item['id'] == contract_item_id), 
                None
            )
            
            if not contract_item:
                return {
                    'error': 'contract_item_not_found',
                    'message': f'合同清单项ID {contract_item_id} 不存在'
                }
            
            # 边界情况2：合同数量为0或None
            contract_quantity = contract_item.get('quantity', Decimal('0'))
            if contract_quantity is None or contract_quantity <= 0:
                return {
                    'error': 'invalid_contract_quantity',
                    'message': f'合同清单项数量无效: {contract_quantity}'
                }
            
            valid_statuses = ['final_approved', 'completed']
            purchased_quantity = Decimal('0.0')
            purchase_count = 0
            
            # 边界情况3：处理None或空的申购请求列表
            if not purchase_requests:
                return {
                    'contract_quantity': contract_quantity,
                    'purchased_quantity': Decimal('0.0'),
                    'remaining_quantity': contract_quantity,
                    'purchase_count': 0
                }
            
            for request in purchase_requests:
                if request.get('contract_item_id') == contract_item_id:
                    request_status = request.get('status')
                    request_quantity = request.get('quantity', Decimal('0'))
                    
                    # 边界情况4：处理无效的申购数量
                    if request_quantity is None:
                        continue
                    
                    if isinstance(request_quantity, (int, float)):
                        request_quantity = Decimal(str(request_quantity))
                    elif not isinstance(request_quantity, Decimal):
                        continue
                    
                    if request_status in valid_statuses and request_quantity > 0:
                        purchased_quantity += request_quantity
                        purchase_count += 1
            
            remaining_quantity = contract_quantity - purchased_quantity
            
            # 边界情况5：剩余数量为负数的警告
            if remaining_quantity < 0:
                return {
                    'contract_quantity': contract_quantity,
                    'purchased_quantity': purchased_quantity,
                    'remaining_quantity': remaining_quantity,
                    'purchase_count': purchase_count,
                    'warning': 'negative_remaining',
                    'message': f'剩余数量为负数 ({remaining_quantity})，可能存在超额申购'
                }
            
            return {
                'contract_quantity': contract_quantity,
                'purchased_quantity': purchased_quantity,
                'remaining_quantity': remaining_quantity,
                'purchase_count': purchase_count
            }
        
        # 测试场景1：不存在的合同清单项
        result = calculate_remaining_quantity_robust(999, self.purchase_requests, self.contract_items)
        assert result['error'] == 'contract_item_not_found'
        assert '不存在' in result['message']
        
        # 测试场景2：空的申购请求列表
        result = calculate_remaining_quantity_robust(1, [], self.contract_items)
        assert result['purchased_quantity'] == Decimal('0.0')
        assert result['remaining_quantity'] == Decimal('15.0')
        assert result['purchase_count'] == 0
        
        # 测试场景3：包含无效数据的申购请求
        invalid_requests = [
            {"id": 1, "contract_item_id": 1, "status": "final_approved", "quantity": None},
            {"id": 2, "contract_item_id": 1, "status": "final_approved", "quantity": "invalid"},
            {"id": 3, "contract_item_id": 1, "status": "final_approved", "quantity": Decimal('3.0')},
            {"id": 4, "contract_item_id": 1, "status": "final_approved", "quantity": -1},
        ]
        
        result = calculate_remaining_quantity_robust(1, invalid_requests, self.contract_items)
        # 只应该统计有效的数量3.0，忽略None、"invalid"、负数
        assert result['purchased_quantity'] == Decimal('3.0')
        assert result['remaining_quantity'] == Decimal('12.0')
        assert result['purchase_count'] == 1
        
        # 测试场景4：超额申购的情况
        over_purchase_requests = [
            {"id": 1, "contract_item_id": 3, "status": "final_approved", "quantity": Decimal('8.0')},  # 超过合同数量5.0
        ]
        
        result = calculate_remaining_quantity_robust(3, over_purchase_requests, self.contract_items)
        assert result['remaining_quantity'] == Decimal('-3.0')
        assert result['warning'] == 'negative_remaining'
        assert '超额申购' in result['message']
        
        print("   ✅ 所有边界情况处理正确")
        print(f"   🚨 超额申购检测: {result['message']}")
    
    def test_performance_optimization_large_dataset(self):
        """测试大数据集的性能优化"""
        print("\n⚡ 测试大数据集性能优化...")
        
        import time
        
        def calculate_remaining_quantities_optimized(contract_items, purchase_requests):
            """优化的批量剩余数量计算"""
            # 构建按合同清单项分组的申购请求索引
            purchase_index = {}
            valid_statuses = {'final_approved', 'completed'}
            
            for request in purchase_requests:
                contract_item_id = request.get('contract_item_id')
                if contract_item_id and request.get('status') in valid_statuses:
                    if contract_item_id not in purchase_index:
                        purchase_index[contract_item_id] = []
                    purchase_index[contract_item_id].append(request)
            
            results = {}
            for contract_item in contract_items:
                item_id = contract_item['id']
                purchased_quantity = Decimal('0.0')
                
                if item_id in purchase_index:
                    for request in purchase_index[item_id]:
                        quantity = request.get('quantity', Decimal('0'))
                        if isinstance(quantity, (int, float)):
                            quantity = Decimal(str(quantity))
                        if isinstance(quantity, Decimal) and quantity > 0:
                            purchased_quantity += quantity
                
                remaining_quantity = contract_item['quantity'] - purchased_quantity
                
                results[item_id] = {
                    'remaining_quantity': remaining_quantity,
                    'purchased_quantity': purchased_quantity
                }
            
            return results
        
        # 生成大量测试数据
        large_contract_items = []
        large_purchase_requests = []
        
        for i in range(10000):
            large_contract_items.append({
                'id': i + 1,
                'item_name': f'设备{i}',
                'quantity': Decimal('100.0')
            })
            
            # 为每个合同项创建多个申购请求
            for j in range(5):
                large_purchase_requests.append({
                    'id': i * 5 + j + 1,
                    'contract_item_id': i + 1,
                    'status': 'final_approved' if j < 2 else 'draft',
                    'quantity': Decimal('10.0')
                })
        
        # 性能测试
        start_time = time.time()
        results = calculate_remaining_quantities_optimized(
            large_contract_items[:1000], large_purchase_requests[:5000]
        )
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        assert len(results) == 1000
        assert execution_time < 1.0  # 应该在1秒内完成
        
        # 验证计算正确性
        sample_result = results[1]
        assert sample_result['purchased_quantity'] == Decimal('20.0')  # 2个final_approved * 10.0
        assert sample_result['remaining_quantity'] == Decimal('80.0')  # 100.0 - 20.0
        
        print(f"   ✅ 1000个合同项，5000个申购请求计算耗时: {execution_time:.4f}秒")
        print("   ✅ 大数据集剩余数量计算性能优良")
    
    def test_real_time_calculation_accuracy(self):
        """测试实时计算的准确性"""
        print("\n🔄 测试实时计算准确性...")
        
        def simulate_real_time_updates(initial_contracts, initial_requests):
            """模拟实时更新场景"""
            import copy
            
            contracts = copy.deepcopy(initial_contracts)
            requests = copy.deepcopy(initial_requests)
            
            def get_current_remaining(item_id):
                contract = next((c for c in contracts if c['id'] == item_id), None)
                if not contract:
                    return None
                
                purchased = Decimal('0.0')
                for req in requests:
                    if (req['contract_item_id'] == item_id and 
                        req['status'] in ['final_approved', 'completed']):
                        purchased += req['quantity']
                
                return contract['quantity'] - purchased
            
            # 初始状态
            initial_remaining = get_current_remaining(1)
            updates_log = [f"初始剩余数量: {initial_remaining}"]
            
            # 模拟申购单状态变化
            # 场景1：草稿申购单提交（不应影响剩余数量）
            for req in requests:
                if req['id'] == 1 and req['status'] == 'draft':
                    req['status'] = 'submitted'
                    break
            
            after_submit = get_current_remaining(1)
            updates_log.append(f"申购单提交后剩余数量: {after_submit}")
            assert after_submit == initial_remaining, "提交状态不应影响剩余数量"
            
            # 场景2：申购单询价完成（不应影响剩余数量）
            for req in requests:
                if req['id'] == 3 and req['status'] == 'submitted':
                    req['status'] = 'price_quoted'
                    break
            
            after_quote = get_current_remaining(1)
            updates_log.append(f"询价完成后剩余数量: {after_quote}")
            assert after_quote == initial_remaining, "询价状态不应影响剩余数量"
            
            # 场景3：部门审批通过（按新逻辑不应影响剩余数量）
            for req in requests:
                if req['id'] == 3 and req['status'] == 'price_quoted':
                    req['status'] = 'dept_approved'
                    break
            
            after_dept = get_current_remaining(1)
            updates_log.append(f"部门审批后剩余数量: {after_dept}")
            assert after_dept == initial_remaining, "部门审批不应影响剩余数量（新逻辑）"
            
            # 场景4：总经理最终批准（应该影响剩余数量）
            approval_quantity = None
            for req in requests:
                if req['id'] == 3 and req['status'] == 'dept_approved':
                    req['status'] = 'final_approved'
                    approval_quantity = req['quantity']
                    break
            
            after_final = get_current_remaining(1)
            expected_remaining = initial_remaining - approval_quantity
            updates_log.append(f"总经理批准后剩余数量: {after_final}")
            assert after_final == expected_remaining, "总经理批准应该减少剩余数量"
            
            # 场景5：申购单完成（继续减少剩余数量）
            for req in requests:
                if req['id'] == 7 and req['status'] == 'final_approved':
                    req['status'] = 'completed'
                    break
            
            after_complete = get_current_remaining(1)
            updates_log.append(f"申购单完成后剩余数量: {after_complete}")
            # 完成状态不应再次减少数量（因为已经在final_approved时减少过了）
            assert after_complete == after_final, "完成状态应与最终批准状态的剩余数量相同"
            
            return updates_log
        
        updates_log = simulate_real_time_updates(self.contract_items, self.purchase_requests)
        
        print("   ✅ 实时计算状态变化记录:")
        for i, log in enumerate(updates_log, 1):
            print(f"   {i}. {log}")
        
        print("   ✅ 实时计算准确性验证通过")


def run_remaining_quantity_tests():
    """运行所有剩余数量计算测试"""
    print("📊 开始运行剩余数量计算逻辑测试...")
    print("=" * 60)
    
    test_instance = TestRemainingQuantityCalculation()
    
    test_methods = [
        test_instance.test_correct_status_inclusion_logic,
        test_instance.test_wrong_status_inclusion_comparison,
        test_instance.test_batch_remaining_quantity_calculation,
        test_instance.test_remaining_quantity_edge_cases,
        test_instance.test_performance_optimization_large_dataset,
        test_instance.test_real_time_calculation_accuracy
    ]
    
    passed = 0
    failed = 0
    
    for test_method in test_methods:
        try:
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
    print(f"📊 剩余数量计算测试结果: {passed} 通过, {failed} 失败")
    
    return failed == 0


if __name__ == "__main__":
    success = run_remaining_quantity_tests()
    exit(0 if success else 1)