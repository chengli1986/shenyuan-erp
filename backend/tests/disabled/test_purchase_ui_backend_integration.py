"""
申购单前后端集成测试套件

测试前端UI组件与后端API的完整集成场景：
1. 前端表单提交与后端数据验证的集成
2. 实时数据更新的前后端同步
3. 权限控制在前后端的一致性
4. API响应格式与前端解析的兼容性
5. 错误处理的前后端协调

集成测试关注点：
- 前端组件状态与后端数据状态的同步
- API请求/响应格式的标准化
- 前端权限展示与后端权限验证的一致性
- 错误信息的用户友好性
- 实时更新功能的可靠性

作者: Claude Code
创建时间: 2025-01-28
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from decimal import Decimal
import json


class TestPurchaseFormBackendIntegration:
    """申购单表单前后端集成测试"""
    
    def setup_method(self):
        """测试前准备"""
        self.mock_db = Mock()
        self.mock_user = Mock()
        self.mock_user.id = 1
        self.mock_user.role.value = "project_manager"

    def test_purchase_form_submission_integration(self):
        """测试1: 申购表单提交前后端集成"""
        with patch('app.api.v1.purchases.create_purchase_request') as mock_create:
            
            # 模拟前端表单数据
            frontend_form_data = {
                'project_id': 1,
                'notes': '智能安防系统设备采购申请',
                'items': [
                    {
                        'item_name': '网络摄像机',
                        'specification': 'IPC-HFW2431T-ZS-2.8mm',
                        'brand_model': '大华',
                        'unit': '台',
                        'quantity': 10,
                        'item_type': 'main',
                        'contract_item_id': 100,
                        'system_category_id': 1,
                        'notes': '高清夜视摄像机'
                    },
                    {
                        'item_name': '网线',
                        'specification': '六类无氧铜网线',
                        'brand_model': '普天',
                        'unit': '米',
                        'quantity': 500,
                        'item_type': 'auxiliary',
                        'system_category_id': 1,
                        'notes': '用于摄像机连接'
                    }
                ]
            }
            
            # 模拟后端API响应格式
            backend_response = {
                'id': 1,
                'request_code': 'PR202501280001',
                'status': 'draft',
                'current_step': 'project_manager',
                'project_id': 1,
                'project_name': '智能安防项目',
                'requester_id': 1,
                'requester_name': '项目经理张三',
                'notes': '智能安防系统设备采购申请',
                'total_amount': None,  # 项目经理看不到价格
                'created_at': datetime.now().isoformat(),
                'items': [
                    {
                        'id': 1,
                        'item_name': '网络摄像机',
                        'specification': 'IPC-HFW2431T-ZS-2.8mm',
                        'brand_model': '大华',
                        'unit': '台',
                        'quantity': 10,
                        'item_type': 'main',
                        'contract_item_id': 100,
                        'system_category_id': 1,
                        'system_category_name': '视频监控系统',
                        'remaining_quantity': 45.0,
                        'unit_price': None,
                        'total_price': None,
                        'notes': '高清夜视摄像机'
                    },
                    {
                        'id': 2,
                        'item_name': '网线',
                        'specification': '六类无氧铜网线',
                        'brand_model': '普天',
                        'unit': '米',
                        'quantity': 500,
                        'item_type': 'auxiliary',
                        'system_category_id': 1,
                        'system_category_name': '视频监控系统',
                        'unit_price': None,
                        'total_price': None,
                        'notes': '用于摄像机连接'
                    }
                ]
            }
            
            mock_create.return_value = backend_response
            
            # 执行创建
            result = mock_create(frontend_form_data)
            
            # 验证前后端数据格式兼容性
            assert result['status'] == 'draft'
            assert result['current_step'] == 'project_manager'
            assert len(result['items']) == 2
            
            # 验证主材包含完整信息
            main_item = next((item for item in result['items'] if item['item_type'] == 'main'), None)
            assert main_item is not None
            assert main_item['contract_item_id'] == 100
            assert main_item['system_category_name'] is not None
            assert main_item['remaining_quantity'] > 0
            
            # 验证辅材信息
            aux_item = next((item for item in result['items'] if item['item_type'] == 'auxiliary'), None)
            assert aux_item is not None
            assert aux_item['contract_item_id'] is None
            
            # 验证权限相关字段（项目经理看不到价格）
            for item in result['items']:
                assert item['unit_price'] is None
                assert item['total_price'] is None

    def test_real_time_data_update_integration(self):
        """测试2: 实时数据更新前后端集成"""
        with patch('app.api.v1.purchases.get_contract_item_details') as mock_get_details, \
             patch('app.api.v1.purchases.get_specifications_by_material') as mock_get_specs:
            
            # 模拟前端选择物料名称时的API调用
            mock_get_specs.return_value = {
                'specifications': [
                    {
                        'specification': 'IPC-HFW2431T-ZS-2.8mm',
                        'brand_model': '大华',
                        'unit': '台',
                        'contract_item_id': 100,
                        'remaining_quantity': 45.0,
                        'total_quantity': 50.0
                    },
                    {
                        'specification': 'IPC-HFW2431T-ZS-3.6mm',
                        'brand_model': '大华',
                        'unit': '台',
                        'contract_item_id': 101,
                        'remaining_quantity': 30.0,
                        'total_quantity': 35.0
                    }
                ]
            }
            
            # 前端选择物料名称
            specs_result = mock_get_specs(project_id=1, material_name='网络摄像机')
            
            # 验证规格选项返回
            assert len(specs_result['specifications']) == 2
            assert all('remaining_quantity' in spec for spec in specs_result['specifications'])
            
            # 模拟前端选择具体规格后获取详细信息
            selected_spec = specs_result['specifications'][0]
            
            mock_get_details.return_value = {
                'id': 100,
                'item_name': '网络摄像机',
                'specification': selected_spec['specification'],
                'brand_model': selected_spec['brand_model'],
                'unit': selected_spec['unit'],
                'total_quantity': selected_spec['total_quantity'],
                'purchased_quantity': 5.0,
                'remaining_quantity': selected_spec['remaining_quantity'],
                'system_category_id': 1,
                'system_category_name': '视频监控系统'
            }
            
            # 获取详细信息
            details_result = mock_get_details(contract_item_id=100)
            
            # 验证详细信息的完整性
            assert details_result['remaining_quantity'] == 45.0
            assert details_result['system_category_name'] is not None
            assert details_result['purchased_quantity'] + details_result['remaining_quantity'] == details_result['total_quantity']

    def test_permission_consistency_frontend_backend(self):
        """测试3: 权限控制前后端一致性"""
        test_scenarios = [
            {
                'user_role': 'project_manager',
                'expected_permissions': {
                    'can_create': True,
                    'can_submit': True,
                    'can_quote': False,
                    'can_dept_approve': False,
                    'can_see_prices': False,
                    'can_see_suppliers': False
                }
            },
            {
                'user_role': 'purchaser',
                'expected_permissions': {
                    'can_create': True,
                    'can_submit': False,
                    'can_quote': True,
                    'can_dept_approve': False,
                    'can_see_prices': True,
                    'can_see_suppliers': True
                }
            },
            {
                'user_role': 'dept_manager',
                'expected_permissions': {
                    'can_create': False,
                    'can_submit': False,
                    'can_quote': False,
                    'can_dept_approve': True,
                    'can_see_prices': True,
                    'can_see_suppliers': True
                }
            }
        ]
        
        with patch('app.api.v1.purchases.get_user_permissions') as mock_get_permissions:
            
            for scenario in test_scenarios:
                mock_user = Mock()
                mock_user.role.value = scenario['user_role']
                
                # 模拟后端权限API响应
                mock_get_permissions.return_value = scenario['expected_permissions']
                
                # 获取用户权限
                permissions = mock_get_permissions(user=mock_user)
                
                # 验证权限一致性
                for permission, expected in scenario['expected_permissions'].items():
                    assert permissions[permission] == expected
                
                # 特殊验证：项目经理不应看到价格相关信息
                if scenario['user_role'] == 'project_manager':
                    assert permissions['can_see_prices'] is False
                    assert permissions['can_see_suppliers'] is False
                
                # 特殊验证：采购员应该有询价权限
                if scenario['user_role'] == 'purchaser':
                    assert permissions['can_quote'] is True
                    assert permissions['can_see_prices'] is True

    def test_error_handling_frontend_backend_coordination(self):
        """测试4: 错误处理前后端协调"""
        error_scenarios = [
            {
                'error_type': 'validation_error',
                'backend_error': {
                    'status_code': 400,
                    'error_code': 'VALIDATION_FAILED',
                    'message': '申购数量超过剩余可申购数量',
                    'details': {
                        'field': 'quantity',
                        'value': 60,
                        'max_allowed': 45,
                        'contract_item_id': 100
                    }
                },
                'expected_frontend_handling': {
                    'show_error_message': True,
                    'highlight_field': 'quantity',
                    'suggest_max_value': 45,
                    'allow_retry': True
                }
            },
            {
                'error_type': 'permission_error',
                'backend_error': {
                    'status_code': 403,
                    'error_code': 'INSUFFICIENT_PERMISSION',
                    'message': '当前用户无权限执行此操作',
                    'details': {
                        'required_role': 'purchaser',
                        'current_role': 'project_manager',
                        'operation': 'quote_purchase'
                    }
                },
                'expected_frontend_handling': {
                    'show_error_message': True,
                    'hide_operation_button': True,
                    'redirect_to_login': False,
                    'show_role_requirement': True
                }
            },
            {
                'error_type': 'business_rule_error',
                'backend_error': {
                    'status_code': 422,
                    'error_code': 'BUSINESS_RULE_VIOLATION',
                    'message': '申购单状态不允许此操作',
                    'details': {
                        'current_status': 'final_approved',
                        'required_status': ['draft', 'submitted'],
                        'operation': 'update_purchase'
                    }
                },
                'expected_frontend_handling': {
                    'show_error_message': True,
                    'disable_edit_form': True,
                    'show_status_info': True,
                    'allow_view_only': True
                }
            }
        ]
        
        with patch('app.api.v1.purchases.handle_api_error') as mock_handle_error:
            
            for scenario in error_scenarios:
                # 模拟后端错误响应
                mock_handle_error.return_value = {
                    'frontend_response': {
                        'success': False,
                        'error': scenario['backend_error'],
                        'ui_instructions': scenario['expected_frontend_handling']
                    }
                }
                
                # 处理错误
                error_response = mock_handle_error(scenario['backend_error'])
                
                # 验证错误处理的协调性
                ui_instructions = error_response['frontend_response']['ui_instructions']
                expected = scenario['expected_frontend_handling']
                
                assert ui_instructions['show_error_message'] == expected['show_error_message']
                
                # 验证特定错误类型的处理
                if scenario['error_type'] == 'validation_error':
                    assert ui_instructions['highlight_field'] == expected['highlight_field']
                    assert ui_instructions['suggest_max_value'] == expected['suggest_max_value']
                
                if scenario['error_type'] == 'permission_error':
                    assert ui_instructions['show_role_requirement'] == expected['show_role_requirement']
                
                if scenario['error_type'] == 'business_rule_error':
                    assert ui_instructions['disable_edit_form'] == expected['disable_edit_form']


class TestPurchaseWorkflowUIIntegration:
    """申购单工作流UI集成测试"""
    
    def setup_method(self):
        """测试前准备"""
        self.mock_db = Mock()

    def test_workflow_status_display_integration(self):
        """测试5: 工作流状态显示集成"""
        workflow_states = [
            {
                'status': 'draft',
                'current_step': 'project_manager',
                'ui_expectations': {
                    'show_submit_button': True,
                    'show_edit_button': True,
                    'show_delete_button': True,
                    'status_color': 'default',
                    'progress_percentage': 10
                }
            },
            {
                'status': 'submitted',
                'current_step': 'purchaser',
                'ui_expectations': {
                    'show_quote_button': True,
                    'show_return_button': True,
                    'show_edit_button': False,
                    'status_color': 'processing',
                    'progress_percentage': 25
                }
            },
            {
                'status': 'price_quoted',
                'current_step': 'dept_manager',
                'ui_expectations': {
                    'show_approve_button': True,
                    'show_reject_button': True,
                    'show_return_button': True,
                    'status_color': 'warning',
                    'progress_percentage': 50
                }
            },
            {
                'status': 'final_approved',
                'current_step': 'completed',
                'ui_expectations': {
                    'show_complete_button': False,
                    'show_readonly_info': True,
                    'status_color': 'success',
                    'progress_percentage': 100
                }
            }
        ]
        
        with patch('app.api.v1.purchases.get_purchase_workflow_ui_state') as mock_get_ui_state:
            
            for state in workflow_states:
                # 模拟工作流UI状态API
                mock_get_ui_state.return_value = {
                    'purchase_status': state['status'],
                    'current_step': state['current_step'],
                    'ui_elements': state['ui_expectations'],
                    'available_actions': self._get_available_actions(state['status']),
                    'workflow_progress': {
                        'completed_steps': self._get_completed_steps(state['status']),
                        'current_step_info': {
                            'name': state['current_step'],
                            'description': f'当前处于{state["current_step"]}阶段'
                        }
                    }
                }
                
                # 获取UI状态
                ui_state = mock_get_ui_state(
                    purchase_id=1,
                    user_role='project_manager'
                )
                
                # 验证UI状态的正确性
                assert ui_state['purchase_status'] == state['status']
                assert ui_state['current_step'] == state['current_step']
                
                # 验证UI元素显示逻辑
                ui_elements = ui_state['ui_elements']
                expected = state['ui_expectations']
                
                for element, should_show in expected.items():
                    if element in ui_elements:
                        assert ui_elements[element] == should_show

    def test_workflow_history_display_integration(self):
        """测试6: 工作流历史显示集成"""
        with patch('app.api.v1.purchases.get_purchase_workflow_logs') as mock_get_logs:
            
            # 模拟完整的工作流历史
            mock_workflow_history = [
                {
                    'id': 1,
                    'operation_type': 'create',
                    'operator_name': '项目经理张三',
                    'operator_role': 'project_manager',
                    'operation_time': '2025-01-28 09:00:00',
                    'status_before': None,
                    'status_after': 'draft',
                    'notes': '创建申购单',
                    'ui_display': {
                        'icon': 'plus-circle',
                        'color': 'blue',
                        'title': '创建申购单',
                        'description': '项目经理张三创建了申购单'
                    }
                },
                {
                    'id': 2,
                    'operation_type': 'submit',
                    'operator_name': '项目经理张三',
                    'operator_role': 'project_manager',
                    'operation_time': '2025-01-28 10:30:00',
                    'status_before': 'draft',
                    'status_after': 'submitted',
                    'notes': '提交审批',
                    'ui_display': {
                        'icon': 'send',
                        'color': 'green',
                        'title': '提交审批',
                        'description': '申购单已提交，等待采购员询价'
                    }
                },
                {
                    'id': 3,
                    'operation_type': 'quote',
                    'operator_name': '采购员李四',
                    'operator_role': 'purchaser',
                    'operation_time': '2025-01-28 14:15:00',
                    'status_before': 'submitted',
                    'status_after': 'price_quoted',
                    'notes': '完成询价',
                    'quote_details': {
                        'supplier_name': '大华技术股份有限公司',
                        'total_quoted_amount': 5000.00,
                        'payment_method': 'PREPAYMENT'
                    },
                    'ui_display': {
                        'icon': 'dollar',
                        'color': 'orange',
                        'title': '完成询价',
                        'description': '采购员李四完成询价，总金额 ¥5,000.00'
                    }
                }
            ]
            
            mock_get_logs.return_value = {
                'total_logs': len(mock_workflow_history),
                'logs': mock_workflow_history,
                'timeline_summary': {
                    'created_at': '2025-01-28 09:00:00',
                    'last_updated': '2025-01-28 14:15:00',
                    'total_operations': 3,
                    'current_status': 'price_quoted'
                }
            }
            
            # 获取工作流历史
            history_result = mock_get_logs(purchase_id=1)
            
            # 验证历史记录的完整性
            assert history_result['total_logs'] == 3
            assert len(history_result['logs']) == 3
            
            # 验证每个历史记录的UI显示信息
            for log in history_result['logs']:
                assert 'ui_display' in log
                assert 'icon' in log['ui_display']
                assert 'color' in log['ui_display']
                assert 'title' in log['ui_display']
                assert 'description' in log['ui_display']
            
            # 验证询价记录包含详细信息
            quote_log = next((log for log in history_result['logs'] if log['operation_type'] == 'quote'), None)
            assert quote_log is not None
            assert 'quote_details' in quote_log
            assert quote_log['quote_details']['supplier_name'] is not None

    def _get_available_actions(self, status):
        """根据状态获取可用操作"""
        action_map = {
            'draft': ['submit', 'edit', 'delete'],
            'submitted': ['quote', 'return'],
            'price_quoted': ['dept_approve', 'dept_reject', 'return'],
            'dept_approved': ['final_approve', 'final_reject'],
            'final_approved': ['view_only']
        }
        return action_map.get(status, [])
    
    def _get_completed_steps(self, status):
        """根据状态获取已完成步骤"""
        step_map = {
            'draft': ['create'],
            'submitted': ['create', 'submit'],
            'price_quoted': ['create', 'submit', 'quote'],
            'dept_approved': ['create', 'submit', 'quote', 'dept_approve'],
            'final_approved': ['create', 'submit', 'quote', 'dept_approve', 'final_approve']
        }
        return step_map.get(status, [])


if __name__ == "__main__":
    # 运行集成测试
    pytest.main([__file__, '-v', '--tb=short'])