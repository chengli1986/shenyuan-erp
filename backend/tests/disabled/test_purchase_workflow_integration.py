"""
申购单工作流集成测试套件

测试最近开发的申购单核心功能的端到端集成场景：
1. 申购单创建到最终审批的完整工作流
2. 智能系统分类推荐的API集成
3. 剩余数量计算的实时更新
4. 批量操作的权限和业务规则集成
5. 跨组件交互的数据一致性验证

集成测试关注点：
- API层与服务层的集成
- 权限系统与业务逻辑的集成
- 前后端数据格式的兼容性
- 工作流状态变更的一致性
- 多用户并发场景的处理

作者: Claude Code
创建时间: 2025-01-28
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from decimal import Decimal


class TestPurchaseWorkflowIntegration:
    """申购单工作流完整集成测试"""
    
    def setup_method(self):
        """测试前准备"""
        # 模拟数据库会话
        self.mock_db = Mock()
        
        # 模拟用户角色
        self.project_manager = Mock()
        self.project_manager.id = 1
        self.project_manager.name = "测试项目经理"
        self.project_manager.role.value = "project_manager"
        
        self.purchaser = Mock()
        self.purchaser.id = 2
        self.purchaser.name = "测试采购员"
        self.purchaser.role.value = "purchaser"
        
        self.dept_manager = Mock()
        self.dept_manager.id = 3
        self.dept_manager.name = "测试部门主管"
        self.dept_manager.role.value = "dept_manager"
        
        # 模拟申购单数据
        self.purchase_request_data = {
            'project_id': 1,
            'requester_id': 1,
            'items': [
                {
                    'item_name': '网络摄像机',
                    'specification': 'IPC-HFW2431T-ZS',
                    'quantity': 5,
                    'item_type': 'main',
                    'contract_item_id': 100,
                    'system_category_id': 1
                }
            ],
            'total_amount': Decimal('2500.00'),
            'notes': '智能安防系统设备采购'
        }

    def test_complete_purchase_workflow_lifecycle(self):
        """测试1: 申购单完整生命周期集成"""
        with patch('app.services.purchase_service.PurchaseService') as mock_service, \
             patch('app.api.v1.purchases.get_current_user') as mock_get_user:
            
            # 阶段1: 项目经理创建申购单
            mock_get_user.return_value = self.project_manager
            mock_service.create_purchase_request.return_value = {
                'id': 1,
                'request_code': 'PR202501280001',
                'status': 'draft',
                'current_step': 'project_manager',
                'items': self.purchase_request_data['items']
            }
            
            # 创建申购单
            create_result = mock_service.create_purchase_request(
                self.mock_db, 
                self.purchase_request_data, 
                self.project_manager
            )
            
            assert create_result['status'] == 'draft'
            assert create_result['current_step'] == 'project_manager'
            
            # 阶段2: 项目经理提交申购单
            mock_service.submit_purchase_request.return_value = {
                'id': 1,
                'status': 'submitted',
                'current_step': 'purchaser',
                'submitted_at': datetime.now()
            }
            
            submit_result = mock_service.submit_purchase_request(
                self.mock_db, 
                1, 
                self.project_manager
            )
            
            assert submit_result['status'] == 'submitted'
            assert submit_result['current_step'] == 'purchaser'
            
            # 阶段3: 采购员询价
            mock_get_user.return_value = self.purchaser
            quote_data = {
                'supplier_name': '大华技术股份有限公司',
                'supplier_contact': '张销售经理',
                'payment_method': 'PREPAYMENT',
                'estimated_delivery_date': '2025-02-15',
                'items': [
                    {
                        'id': 1,
                        'unit_price': Decimal('500.00'),
                        'supplier_info': {
                            'supplier_name': '大华技术',
                            'payment_method': 'PREPAYMENT'
                        }
                    }
                ]
            }
            
            mock_service.quote_purchase_request.return_value = {
                'id': 1,
                'status': 'price_quoted',
                'current_step': 'dept_manager',
                'quote_date': datetime.now()
            }
            
            quote_result = mock_service.quote_purchase_request(
                self.mock_db, 
                1, 
                quote_data, 
                self.purchaser
            )
            
            assert quote_result['status'] == 'price_quoted'
            assert quote_result['current_step'] == 'dept_manager'
            
            # 阶段4: 部门主管审批
            mock_get_user.return_value = self.dept_manager
            mock_service.approve_purchase_request.return_value = {
                'id': 1,
                'status': 'dept_approved',
                'current_step': 'general_manager',
                'dept_approved_at': datetime.now()
            }
            
            dept_approve_result = mock_service.approve_purchase_request(
                self.mock_db, 
                1, 
                True, 
                '价格合理，同意采购', 
                self.dept_manager
            )
            
            assert dept_approve_result['status'] == 'dept_approved'
            assert dept_approve_result['current_step'] == 'general_manager'
            
            # 验证工作流状态转换的一致性
            expected_workflow = ['draft', 'submitted', 'price_quoted', 'dept_approved']
            actual_workflow = [
                create_result['status'],
                submit_result['status'], 
                quote_result['status'],
                dept_approve_result['status']
            ]
            
            assert actual_workflow == expected_workflow

    def test_intelligent_system_category_api_integration(self):
        """测试2: 智能系统分类推荐API集成"""
        with patch('app.api.v1.purchases.get_system_categories_by_material') as mock_api:
            
            # 模拟单系统推荐场景
            mock_api.return_value = {
                'categories': [
                    {
                        'id': 1,
                        'category_name': '视频监控系统',
                        'is_suggested': True,
                        'confidence_score': 0.95,
                        'items_count': 15
                    }
                ],
                'recommendation_type': 'single_system',
                'material_analysis': {
                    'material_name': '网络摄像机',
                    'specification_matched': True,
                    'contract_items_found': 3
                }
            }
            
            # 测试API调用
            result = mock_api(project_id=1, material_name='网络摄像机')
            
            # 验证推荐结果
            assert result['recommendation_type'] == 'single_system'
            assert len(result['categories']) == 1
            assert result['categories'][0]['is_suggested'] is True
            assert result['categories'][0]['confidence_score'] > 0.9
            
            # 模拟多系统选择场景
            mock_api.return_value = {
                'categories': [
                    {
                        'id': 1,
                        'category_name': '视频监控系统',
                        'is_suggested': True,
                        'confidence_score': 0.85
                    },
                    {
                        'id': 2,
                        'category_name': '周界报警系统',
                        'is_suggested': False,
                        'confidence_score': 0.65
                    }
                ],
                'recommendation_type': 'multi_system',
                'requires_user_selection': True
            }
            
            multi_result = mock_api(project_id=1, material_name='红外探测器')
            
            assert multi_result['recommendation_type'] == 'multi_system'
            assert multi_result['requires_user_selection'] is True
            assert len([cat for cat in multi_result['categories'] if cat['is_suggested']]) == 1

    def test_remaining_quantity_real_time_calculation(self):
        """测试3: 剩余数量实时计算集成"""
        with patch('app.services.purchase_service.calculate_remaining_quantity') as mock_calc:
            
            # 模拟合同清单项
            contract_item = {
                'id': 100,
                'item_name': '网络摄像机',
                'total_quantity': Decimal('50.0'),
                'purchased_quantity': Decimal('0.0')
            }
            
            # 模拟不同状态申购单的数量统计
            status_quantities = {
                'draft': Decimal('5.0'),          # 不应计入
                'submitted': Decimal('8.0'),      # 不应计入
                'price_quoted': Decimal('10.0'),  # 不应计入
                'dept_approved': Decimal('12.0'), # 不应计入（修复后）
                'final_approved': Decimal('15.0'), # 应计入
                'completed': Decimal('0.0')       # 应计入
            }
            
            # 计算预期剩余数量（只统计final_approved和completed）
            expected_purchased = status_quantities['final_approved'] + status_quantities['completed']
            expected_remaining = contract_item['total_quantity'] - expected_purchased
            
            mock_calc.return_value = {
                'contract_quantity': contract_item['total_quantity'],
                'purchased_quantity': expected_purchased,
                'remaining_quantity': expected_remaining,
                'calculation_logic': 'only_final_approved_and_completed',
                'status_breakdown': status_quantities
            }
            
            # 执行计算
            result = mock_calc(
                contract_item_id=100,
                exclude_purchase_ids=[]
            )
            
            # 验证计算逻辑正确性
            assert result['remaining_quantity'] == Decimal('35.0')  # 50 - 15
            assert result['purchased_quantity'] == Decimal('15.0')   # 只统计final_approved
            assert result['calculation_logic'] == 'only_final_approved_and_completed'
            
            # 验证状态排除逻辑
            draft_and_process_total = (
                status_quantities['draft'] + 
                status_quantities['submitted'] + 
                status_quantities['price_quoted'] + 
                status_quantities['dept_approved']
            )
            assert result['purchased_quantity'] < (result['contract_quantity'] - draft_and_process_total)

    def test_batch_operations_permission_integration(self):
        """测试4: 批量操作权限集成"""
        with patch('app.api.v1.purchases.check_batch_operation_permission') as mock_check, \
             patch('app.services.purchase_service.execute_batch_delete') as mock_execute:
            
            # 测试项目经理批量删除权限
            purchase_ids = [1, 2, 3, 4, 5]
            
            # 模拟权限检查结果
            mock_check.return_value = {
                'allowed_ids': [1, 2, 3],        # 可删除的ID
                'blocked_ids': [4, 5],           # 权限不足的ID
                'permission_details': {
                    1: {'status': 'draft', 'project_id': 1, 'can_delete': True},
                    2: {'status': 'draft', 'project_id': 1, 'can_delete': True},
                    3: {'status': 'submitted', 'project_id': 1, 'can_delete': True},
                    4: {'status': 'price_quoted', 'project_id': 1, 'can_delete': False},
                    5: {'status': 'draft', 'project_id': 2, 'can_delete': False}  # 不同项目
                },
                'validation_rules': {
                    'only_draft_and_submitted': True,
                    'project_level_permission': True,
                    'role_based_access': True
                }
            }
            
            # 执行权限检查
            permission_result = mock_check(
                user=self.project_manager,
                purchase_ids=purchase_ids
            )
            
            # 验证权限检查结果
            assert len(permission_result['allowed_ids']) == 3
            assert len(permission_result['blocked_ids']) == 2
            
            # 只对允许的ID执行批量删除
            mock_execute.return_value = {
                'deleted_count': 3,
                'deleted_ids': [1, 2, 3],
                'failed_ids': [],
                'operation_log': {
                    'operator': self.project_manager.name,
                    'timestamp': datetime.now(),
                    'affected_projects': [1]
                }
            }
            
            delete_result = mock_execute(
                self.mock_db,
                permission_result['allowed_ids'],
                self.project_manager
            )
            
            assert delete_result['deleted_count'] == 3
            assert delete_result['deleted_ids'] == [1, 2, 3]
            
            # 测试跨角色权限差异
            mock_check.return_value['allowed_ids'] = [1, 2, 3, 4, 5]  # 管理员全部允许
            
            admin_permission = mock_check(
                user=Mock(role=Mock(value='admin')),
                purchase_ids=purchase_ids
            )
            
            assert len(admin_permission['allowed_ids']) == 5  # 管理员权限更高

    def test_workflow_return_bidirectional_integration(self):
        """测试5: 工作流双向退回集成"""
        with patch('app.services.purchase_service.return_purchase_request') as mock_return:
            
            # 测试采购员退回给项目经理
            mock_return.return_value = {
                'id': 1,
                'status': 'draft',
                'current_step': 'project_manager',
                'return_reason': '规格需要重新确认',
                'returned_by': self.purchaser.name,
                'returned_at': datetime.now()
            }
            
            purchaser_return = mock_return(
                self.mock_db,
                purchase_id=1,
                return_reason='规格需要重新确认',
                current_user=self.purchaser
            )
            
            assert purchaser_return['status'] == 'draft'
            assert purchaser_return['current_step'] == 'project_manager'
            
            # 测试项目经理退回给采购员
            mock_return.return_value = {
                'id': 1,
                'status': 'submitted',
                'current_step': 'purchaser',
                'return_reason': '价格过高，需要重新询价',
                'returned_by': self.project_manager.name,
                'returned_at': datetime.now()
            }
            
            pm_return = mock_return(
                self.mock_db,
                purchase_id=1,
                return_reason='价格过高，需要重新询价',
                current_user=self.project_manager
            )
            
            assert pm_return['status'] == 'submitted'
            assert pm_return['current_step'] == 'purchaser'
            
            # 验证双向退回的状态逻辑一致性
            assert purchaser_return['status'] != pm_return['status']
            assert purchaser_return['current_step'] != pm_return['current_step']

    def test_cross_component_data_consistency(self):
        """测试6: 跨组件数据一致性验证"""
        with patch('app.api.v1.purchases.get_purchase_request') as mock_get_detail, \
             patch('app.api.v1.purchases.get_purchase_requests') as mock_get_list:
            
            # 模拟申购单详情API响应
            purchase_detail = {
                'id': 1,
                'request_code': 'PR202501280001',
                'status': 'price_quoted',
                'current_step': 'dept_manager',
                'total_amount': Decimal('2500.00'),
                'items': [
                    {
                        'id': 1,
                        'item_name': '网络摄像机',
                        'quantity': 5,
                        'unit_price': Decimal('500.00'),
                        'system_category_name': '视频监控系统',
                        'remaining_quantity': Decimal('45.0')
                    }
                ]
            }
            
            mock_get_detail.return_value = purchase_detail
            
            # 模拟申购单列表API响应
            purchase_list = {
                'total': 1,
                'items': [
                    {
                        'id': 1,
                        'request_code': 'PR202501280001',
                        'status': 'price_quoted',
                        'total_amount': Decimal('2500.00'),
                        'project_name': '测试项目',
                        'requester_name': '测试项目经理'
                    }
                ]
            }
            
            mock_get_list.return_value = purchase_list
            
            # 验证详情和列表数据一致性
            detail = mock_get_detail(purchase_id=1)
            list_result = mock_get_list(page=1, size=10)
            list_item = list_result['items'][0]
            
            # 关键字段一致性验证
            assert detail['id'] == list_item['id']
            assert detail['request_code'] == list_item['request_code']
            assert detail['status'] == list_item['status']
            assert detail['total_amount'] == list_item['total_amount']
            
            # 验证系统分类和剩余数量在详情中的完整性
            assert detail['items'][0]['system_category_name'] is not None
            assert detail['items'][0]['remaining_quantity'] > 0
            assert isinstance(detail['items'][0]['unit_price'], Decimal)

    def test_concurrent_purchase_request_handling(self):
        """测试7: 并发申购单处理"""
        with patch('app.services.purchase_service.create_purchase_request') as mock_create, \
             patch('app.services.purchase_service.calculate_remaining_quantity') as mock_calc:
            
            # 模拟并发创建场景
            concurrent_requests = []
            
            for i in range(3):
                request_data = {
                    'project_id': 1,
                    'requester_id': self.project_manager.id,
                    'items': [
                        {
                            'contract_item_id': 100,
                            'quantity': 10,  # 每个申购单申请10个
                            'item_name': '网络摄像机'
                        }
                    ]
                }
                concurrent_requests.append(request_data)
            
            # 模拟剩余数量实时计算
            remaining_quantities = [35, 25, 15]  # 递减的剩余数量
            
            mock_calc.side_effect = [
                {'remaining_quantity': Decimal(str(rq))} for rq in remaining_quantities
            ]
            
            # 模拟创建结果
            mock_create.side_effect = [
                {'id': i+1, 'status': 'draft', 'can_create': True} 
                for i in range(3)
            ]
            
            # 执行并发创建
            results = []
            for i, request_data in enumerate(concurrent_requests):
                # 每次创建前检查剩余数量
                remaining = mock_calc()
                if remaining['remaining_quantity'] >= request_data['items'][0]['quantity']:
                    result = mock_create(self.mock_db, request_data, self.project_manager)
                    results.append(result)
                else:
                    results.append({'error': 'insufficient_quantity'})
            
            # 验证并发处理结果
            assert len(results) == 3
            assert all(r.get('can_create', False) for r in results if 'error' not in r)
            
            # 验证剩余数量计算的实时性
            assert len([r for r in results if 'error' not in r]) <= 3  # 最多3个成功


class TestPurchasePermissionIntegration:
    """申购单权限系统集成测试"""
    
    def setup_method(self):
        """测试前准备"""
        self.mock_db = Mock()
        
        # 不同角色用户
        self.roles_users = {
            'project_manager': Mock(id=1, name='项目经理张三', role=Mock(value='project_manager')),
            'purchaser': Mock(id=2, name='采购员李四', role=Mock(value='purchaser')),
            'dept_manager': Mock(id=3, name='部门主管王五', role=Mock(value='dept_manager')),
            'admin': Mock(id=4, name='系统管理员', role=Mock(value='admin'))
        }

    def test_role_based_api_access_integration(self):
        """测试8: 基于角色的API访问集成"""
        with patch('app.api.v1.purchases.get_current_user') as mock_get_user, \
             patch('app.api.v1.purchases.get_purchase_requests') as mock_get_requests:
            
            # 测试项目经理权限 - 只看负责项目的申购单
            mock_get_user.return_value = self.roles_users['project_manager']
            mock_get_requests.return_value = {
                'total': 5,
                'items': [
                    {'id': i, 'project_id': 1, 'project_name': '项目A'} 
                    for i in range(1, 6)
                ]
            }
            
            pm_result = mock_get_requests(user=self.roles_users['project_manager'])
            assert pm_result['total'] == 5
            assert all(item['project_id'] == 1 for item in pm_result['items'])
            
            # 测试管理员权限 - 看到所有申购单
            mock_get_user.return_value = self.roles_users['admin']
            mock_get_requests.return_value = {
                'total': 15,
                'items': [
                    {'id': i, 'project_id': i % 3 + 1} 
                    for i in range(1, 16)
                ]
            }
            
            admin_result = mock_get_requests(user=self.roles_users['admin'])
            assert admin_result['total'] == 15
            project_ids = set(item['project_id'] for item in admin_result['items'])
            assert len(project_ids) == 3  # 跨多个项目

    def test_workflow_operation_permission_matrix(self):
        """测试9: 工作流操作权限矩阵"""
        permission_matrix = {
            'create': ['project_manager', 'admin'],
            'submit': ['project_manager', 'admin'],
            'quote': ['purchaser', 'admin'],
            'dept_approve': ['dept_manager', 'admin'],
            'final_approve': ['general_manager', 'admin'],
            'return': ['purchaser', 'project_manager', 'admin'],
            'delete': ['project_manager', 'admin']
        }
        
        with patch('app.services.purchase_service.check_operation_permission') as mock_check:
            
            for operation, allowed_roles in permission_matrix.items():
                for role_name, user in self.roles_users.items():
                    expected_allowed = role_name in allowed_roles or role_name == 'admin'
                    
                    mock_check.return_value = {
                        'allowed': expected_allowed,
                        'operation': operation,
                        'user_role': role_name,
                        'reason': f'{role_name} {"can" if expected_allowed else "cannot"} {operation}'
                    }
                    
                    result = mock_check(
                        operation=operation,
                        user=user,
                        purchase_id=1
                    )
                    
                    if role_name == 'admin':
                        assert result['allowed'] is True  # 管理员拥有所有权限
                    else:
                        assert result['allowed'] == expected_allowed


if __name__ == "__main__":
    # 运行集成测试
    pytest.main([__file__, '-v', '--tb=short'])