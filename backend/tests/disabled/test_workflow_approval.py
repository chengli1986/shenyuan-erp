"""
申购单工作流审批功能单元测试
测试完整的审批流程：提交→询价→部门审批→总经理审批→完成
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from decimal import Decimal


class TestWorkflowApproval:
    """工作流审批功能测试类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        # 模拟用户角色
        self.users = {
            "pm_sunyun": {"id": 3, "name": "孙赟", "role": "project_manager"},
            "purchaser": {"id": 2, "name": "赵采购员", "role": "purchaser"},
            "dept_manager": {"id": 4, "name": "李工程部主管", "role": "dept_manager"},
            "general_manager": {"id": 1, "name": "张总经理", "role": "general_manager"},
            "admin": {"id": 5, "name": "系统管理员", "role": "admin"}
        }
        
        # 模拟项目数据
        self.projects = [
            {"id": 2, "project_name": "娄山关路445弄综合弱电智能化", "project_manager": "孙赟"}
        ]
        
        # 申购单状态枚举
        self.purchase_statuses = {
            'DRAFT': 'draft',
            'SUBMITTED': 'submitted', 
            'PRICE_QUOTED': 'price_quoted',
            'DEPT_APPROVED': 'dept_approved',
            'FINAL_APPROVED': 'final_approved',
            'COMPLETED': 'completed',
            'REJECTED': 'rejected',
            'CANCELLED': 'cancelled'
        }
        
        # 模拟申购单数据
        self.sample_purchase_request = {
            "id": 1,
            "request_code": "PR202508200001",
            "project_id": 2,
            "requester_id": 3,
            "status": "draft",
            "current_step": "project_manager",
            "current_approver_id": 3,
            "total_amount": None,
            "created_at": datetime.now(),
            "items": [
                {
                    "id": 1,
                    "item_name": "网络摄像机",
                    "specification": "DS-2CD3T56WD-I8",
                    "brand_model": "海康威视",
                    "quantity": 10,
                    "unit": "台",
                    "item_type": "main"
                }
            ]
        }
    
    def test_submit_workflow_step(self):
        """测试申购单提交步骤"""
        print("\n📤 测试申购单提交步骤...")
        
        def submit_purchase_request(purchase_request, current_user):
            """申购单提交业务逻辑"""
            # 权限检查
            if current_user['role'] not in ['project_manager', 'purchaser', 'admin']:
                return {
                    'success': False,
                    'error': 'permission_denied',
                    'message': f"{current_user['role']}角色无权提交申购单"
                }
            
            # 状态检查
            if purchase_request['status'] != 'draft':
                return {
                    'success': False,
                    'error': 'invalid_status',
                    'message': f"只有草稿状态的申购单可以提交，当前状态：{purchase_request['status']}"
                }
            
            # 项目权限检查（针对项目经理）
            if current_user['role'] == 'project_manager':
                project = next((p for p in self.projects if p['id'] == purchase_request['project_id']), None)
                if not project or project['project_manager'] != current_user['name']:
                    return {
                        'success': False,
                        'error': 'project_permission_denied',
                        'message': "只能提交负责项目的申购单"
                    }
            
            # 内容验证
            if not purchase_request.get('items') or len(purchase_request['items']) == 0:
                return {
                    'success': False,
                    'error': 'validation_failed',
                    'message': "申购单必须包含至少一个明细项"
                }
            
            # 执行提交
            updated_request = purchase_request.copy()
            updated_request.update({
                'status': 'submitted',
                'current_step': 'purchaser',
                'current_approver_id': self.users['purchaser']['id'],
                'submitted_at': datetime.now(),
                'submitted_by': current_user['id']
            })
            
            return {
                'success': True,
                'updated_request': updated_request,
                'message': "申购单提交成功，等待采购员询价",
                'next_step': {
                    'step_name': 'purchaser',
                    'approver': self.users['purchaser']['name'],
                    'action_required': '询价'
                }
            }
        
        # 测试场景1：项目经理成功提交
        result = submit_purchase_request(self.sample_purchase_request, self.users['pm_sunyun'])
        
        assert result['success'] == True
        assert result['updated_request']['status'] == 'submitted'
        assert result['updated_request']['current_step'] == 'purchaser'
        assert result['next_step']['step_name'] == 'purchaser'
        assert result['next_step']['action_required'] == '询价'
        print("   ✅ 项目经理成功提交申购单")
        
        # 测试场景2：非草稿状态提交失败
        submitted_request = self.sample_purchase_request.copy()
        submitted_request['status'] = 'submitted'
        
        result = submit_purchase_request(submitted_request, self.users['pm_sunyun'])
        
        assert result['success'] == False
        assert result['error'] == 'invalid_status'
        assert "只有草稿状态" in result['message']
        print("   ✅ 非草稿状态正确阻止提交")
        
        # 测试场景3：无权限用户提交失败
        result = submit_purchase_request(self.sample_purchase_request, {'role': 'worker', 'name': '施工队长'})
        
        assert result['success'] == False
        assert result['error'] == 'permission_denied'
        print("   ✅ 无权限用户被正确拒绝")
    
    def test_quote_workflow_step(self):
        """测试采购员询价步骤"""
        print("\n💰 测试采购员询价步骤...")
        
        def quote_purchase_request(purchase_request, quote_data, current_user):
            """采购员询价业务逻辑"""
            # 权限检查
            if current_user['role'] not in ['purchaser', 'admin']:
                return {
                    'success': False,
                    'error': 'permission_denied',
                    'message': f"{current_user['role']}角色无权询价"
                }
            
            # 状态检查
            if purchase_request['status'] != 'submitted':
                return {
                    'success': False,
                    'error': 'invalid_status',
                    'message': f"只有已提交状态的申购单可以询价，当前状态：{purchase_request['status']}"
                }
            
            # 询价数据验证
            required_quote_fields = ['payment_method', 'estimated_delivery_date']
            for field in required_quote_fields:
                if not quote_data.get(field):
                    return {
                        'success': False,
                        'error': 'validation_failed',
                        'message': f"询价信息不完整，缺少：{field}"
                    }
            
            # 明细项询价信息验证
            if not quote_data.get('items') or len(quote_data['items']) == 0:
                return {
                    'success': False,
                    'error': 'validation_failed',
                    'message': "必须为申购明细项提供询价信息"
                }
            
            # 价格信息验证
            total_amount = Decimal('0.0')
            updated_items = []
            
            for item_quote in quote_data['items']:
                if not item_quote.get('unit_price') or Decimal(str(item_quote['unit_price'])) <= 0:
                    return {
                        'success': False,
                        'error': 'validation_failed',
                        'message': f"明细项{item_quote.get('item_id', 'Unknown')}单价无效"
                    }
                
                quantity = Decimal(str(item_quote.get('quantity', 0)))
                unit_price = Decimal(str(item_quote['unit_price']))
                item_total = quantity * unit_price
                total_amount += item_total
                
                updated_items.append({
                    'item_id': item_quote['item_id'],
                    'unit_price': unit_price,
                    'total_price': item_total,
                    'supplier_name': item_quote.get('supplier_name', ''),
                    'supplier_contact': item_quote.get('supplier_contact', ''),
                    'estimated_delivery': item_quote.get('estimated_delivery')
                })
            
            # 执行询价
            updated_request = purchase_request.copy()
            updated_request.update({
                'status': 'price_quoted',
                'current_step': 'dept_manager',
                'current_approver_id': self.users['dept_manager']['id'],
                'total_amount': total_amount,
                'payment_method': quote_data['payment_method'],
                'estimated_delivery_date': quote_data['estimated_delivery_date'],
                'quote_notes': quote_data.get('quote_notes', ''),
                'quoted_at': datetime.now(),
                'quoted_by': current_user['id'],
                'quoted_items': updated_items
            })
            
            return {
                'success': True,
                'updated_request': updated_request,
                'message': f"询价完成，总金额：¥{total_amount}，等待部门主管审批",
                'total_amount': total_amount,
                'next_step': {
                    'step_name': 'dept_manager',
                    'approver': self.users['dept_manager']['name'],
                    'action_required': '审批'
                }
            }
        
        # 准备测试数据
        submitted_request = self.sample_purchase_request.copy()
        submitted_request['status'] = 'submitted'
        
        quote_data = {
            'payment_method': 'PREPAYMENT',
            'estimated_delivery_date': datetime.now() + timedelta(days=15),
            'quote_notes': '供应商报价优惠，交期可保证',
            'items': [
                {
                    'item_id': 1,
                    'unit_price': 2800.00,
                    'quantity': 10,
                    'supplier_name': '海康威视科技有限公司',
                    'supplier_contact': '张经理 13800138000',
                    'estimated_delivery': datetime.now() + timedelta(days=15)
                }
            ]
        }
        
        # 测试场景1：采购员成功询价
        result = quote_purchase_request(submitted_request, quote_data, self.users['purchaser'])
        
        assert result['success'] == True
        assert result['updated_request']['status'] == 'price_quoted'
        assert result['updated_request']['current_step'] == 'dept_manager'
        assert result['total_amount'] == Decimal('28000.00')  # 10 * 2800
        assert result['next_step']['step_name'] == 'dept_manager'
        print("   ✅ 采购员成功完成询价")
        print(f"   💰 总金额: ¥{result['total_amount']}")
        
        # 测试场景2：缺少必要询价信息
        incomplete_quote = quote_data.copy()
        del incomplete_quote['payment_method']
        
        result = quote_purchase_request(submitted_request, incomplete_quote, self.users['purchaser'])
        
        assert result['success'] == False
        assert result['error'] == 'validation_failed'
        assert 'payment_method' in result['message']
        print("   ✅ 缺少必要信息时正确拒绝")
        
        # 测试场景3：非已提交状态询价失败
        draft_request = self.sample_purchase_request.copy()
        
        result = quote_purchase_request(draft_request, quote_data, self.users['purchaser'])
        
        assert result['success'] == False
        assert result['error'] == 'invalid_status'
        print("   ✅ 非已提交状态正确阻止询价")
    
    def test_department_approval_step(self):
        """测试部门主管审批步骤"""
        print("\n👔 测试部门主管审批步骤...")
        
        def department_approve(purchase_request, approval_data, current_user):
            """部门主管审批业务逻辑"""
            # 权限检查
            if current_user['role'] not in ['dept_manager', 'admin']:
                return {
                    'success': False,
                    'error': 'permission_denied',
                    'message': f"{current_user['role']}角色无部门审批权限"
                }
            
            # 状态检查
            if purchase_request['status'] != 'price_quoted':
                return {
                    'success': False,
                    'error': 'invalid_status',
                    'message': f"只有已询价状态的申购单可以审批，当前状态：{purchase_request['status']}"
                }
            
            # 审批数据验证
            approval_status = approval_data.get('approval_status')
            if approval_status not in ['approved', 'rejected']:
                return {
                    'success': False,
                    'error': 'validation_failed',
                    'message': "审批状态必须是approved或rejected"
                }
            
            # 拒绝时必须有理由
            if approval_status == 'rejected' and not approval_data.get('approval_notes'):
                return {
                    'success': False,
                    'error': 'validation_failed',
                    'message': "拒绝审批时必须填写拒绝理由"
                }
            
            # 执行审批
            updated_request = purchase_request.copy()
            
            if approval_status == 'approved':
                updated_request.update({
                    'status': 'dept_approved',
                    'current_step': 'general_manager',
                    'current_approver_id': self.users['general_manager']['id'],
                    'dept_approved_at': datetime.now(),
                    'dept_approved_by': current_user['id'],
                    'dept_approval_notes': approval_data.get('approval_notes', '')
                })
                
                next_step = {
                    'step_name': 'general_manager',
                    'approver': self.users['general_manager']['name'],
                    'action_required': '最终审批'
                }
                message = "部门主管审批通过，等待总经理最终审批"
                
            else:  # rejected
                updated_request.update({
                    'status': 'rejected',
                    'current_step': None,
                    'current_approver_id': None,
                    'rejected_at': datetime.now(),
                    'rejected_by': current_user['id'],
                    'rejection_reason': approval_data['approval_notes']
                })
                
                next_step = None
                message = "部门主管拒绝审批，申购流程终止"
            
            return {
                'success': True,
                'updated_request': updated_request,
                'message': message,
                'approval_status': approval_status,
                'next_step': next_step
            }
        
        # 准备测试数据
        quoted_request = self.sample_purchase_request.copy()
        quoted_request.update({
            'status': 'price_quoted',
            'total_amount': Decimal('28000.00'),
            'payment_method': 'PREPAYMENT'
        })
        
        # 测试场景1：部门主管批准
        approval_data = {
            'approval_status': 'approved',
            'approval_notes': '技术规格符合要求，预算合理，同意采购'
        }
        
        result = department_approve(quoted_request, approval_data, self.users['dept_manager'])
        
        assert result['success'] == True
        assert result['updated_request']['status'] == 'dept_approved'
        assert result['updated_request']['current_step'] == 'general_manager'
        assert result['approval_status'] == 'approved'
        assert result['next_step']['step_name'] == 'general_manager'
        print("   ✅ 部门主管成功批准申购单")
        
        # 测试场景2：部门主管拒绝（有理由）
        rejection_data = {
            'approval_status': 'rejected',
            'approval_notes': '预算超标，需要重新询价或选择更经济的方案'
        }
        
        result = department_approve(quoted_request, rejection_data, self.users['dept_manager'])
        
        assert result['success'] == True
        assert result['updated_request']['status'] == 'rejected'
        assert result['updated_request']['current_step'] is None
        assert result['approval_status'] == 'rejected'
        assert result['next_step'] is None
        print("   ✅ 部门主管成功拒绝申购单")
        
        # 测试场景3：拒绝时缺少理由
        invalid_rejection = {
            'approval_status': 'rejected',
            'approval_notes': ''  # 空理由
        }
        
        result = department_approve(quoted_request, invalid_rejection, self.users['dept_manager'])
        
        assert result['success'] == False
        assert result['error'] == 'validation_failed'
        assert "必须填写拒绝理由" in result['message']
        print("   ✅ 拒绝时缺少理由被正确阻止")
    
    def test_final_approval_step(self):
        """测试总经理最终审批步骤"""
        print("\n👑 测试总经理最终审批步骤...")
        
        def final_approve(purchase_request, approval_data, current_user):
            """总经理最终审批业务逻辑"""
            # 权限检查
            if current_user['role'] not in ['general_manager', 'admin']:
                return {
                    'success': False,
                    'error': 'permission_denied',
                    'message': f"{current_user['role']}角色无最终审批权限"
                }
            
            # 状态检查
            if purchase_request['status'] != 'dept_approved':
                return {
                    'success': False,
                    'error': 'invalid_status',
                    'message': f"只有部门审批通过的申购单可以最终审批，当前状态：{purchase_request['status']}"
                }
            
            # 审批数据验证
            approval_status = approval_data.get('approval_status')
            if approval_status not in ['approved', 'rejected']:
                return {
                    'success': False,
                    'error': 'validation_failed',
                    'message': "最终审批状态必须是approved或rejected"
                }
            
            # 执行最终审批
            updated_request = purchase_request.copy()
            
            if approval_status == 'approved':
                updated_request.update({
                    'status': 'final_approved',
                    'current_step': 'completed',  # 流程基本完成
                    'current_approver_id': None,
                    'final_approved_at': datetime.now(),
                    'final_approved_by': current_user['id'],
                    'final_approval_notes': approval_data.get('approval_notes', '')
                })
                
                message = "总经理最终批准，申购单已通过所有审批流程"
                next_step = {
                    'step_name': 'completed',
                    'action_required': '可以开始采购执行'
                }
                
            else:  # rejected
                updated_request.update({
                    'status': 'rejected',
                    'current_step': None,
                    'current_approver_id': None,
                    'final_rejected_at': datetime.now(),
                    'final_rejected_by': current_user['id'],
                    'final_rejection_reason': approval_data.get('approval_notes', '')
                })
                
                message = "总经理拒绝最终审批，申购流程终止"
                next_step = None
            
            return {
                'success': True,
                'updated_request': updated_request,
                'message': message,
                'approval_status': approval_status,
                'next_step': next_step
            }
        
        # 准备测试数据
        dept_approved_request = self.sample_purchase_request.copy()
        dept_approved_request.update({
            'status': 'dept_approved',
            'total_amount': Decimal('28000.00')
        })
        
        # 测试场景1：总经理最终批准
        final_approval_data = {
            'approval_status': 'approved',
            'approval_notes': '同意采购，请按时完成交付'
        }
        
        result = final_approve(dept_approved_request, final_approval_data, self.users['general_manager'])
        
        assert result['success'] == True
        assert result['updated_request']['status'] == 'final_approved'
        assert result['updated_request']['current_step'] == 'completed'
        assert result['approval_status'] == 'approved'
        assert result['next_step']['step_name'] == 'completed'
        print("   ✅ 总经理成功最终批准申购单")
        
        # 测试场景2：总经理最终拒绝
        final_rejection_data = {
            'approval_status': 'rejected',
            'approval_notes': '当前资金紧张，暂缓此采购项目'
        }
        
        result = final_approve(dept_approved_request, final_rejection_data, self.users['general_manager'])
        
        assert result['success'] == True
        assert result['updated_request']['status'] == 'rejected'
        assert result['updated_request']['current_step'] is None
        assert result['approval_status'] == 'rejected'
        assert result['next_step'] is None
        print("   ✅ 总经理成功拒绝申购单")
    
    def test_complete_workflow_integration(self):
        """测试完整工作流集成"""
        print("\n🔄 测试完整工作流集成...")
        
        def execute_complete_workflow(initial_request):
            """执行完整的申购工作流"""
            workflow_log = []
            current_request = initial_request.copy()
            
            # 步骤1：项目经理提交
            def submit_step(request, user):
                request_copy = request.copy()
                request_copy.update({
                    'status': 'submitted',
                    'current_step': 'purchaser',
                    'submitted_at': datetime.now(),
                    'submitted_by': user['id']
                })
                return request_copy
            
            current_request = submit_step(current_request, self.users['pm_sunyun'])
            workflow_log.append({
                'step': 'submit',
                'status': current_request['status'],
                'operator': self.users['pm_sunyun']['name'],
                'timestamp': datetime.now()
            })
            
            # 步骤2：采购员询价
            def quote_step(request, user):
                request_copy = request.copy()
                request_copy.update({
                    'status': 'price_quoted',
                    'current_step': 'dept_manager',
                    'total_amount': Decimal('28000.00'),
                    'payment_method': 'PREPAYMENT',
                    'quoted_at': datetime.now(),
                    'quoted_by': user['id']
                })
                return request_copy
            
            current_request = quote_step(current_request, self.users['purchaser'])
            workflow_log.append({
                'step': 'quote',
                'status': current_request['status'],
                'operator': self.users['purchaser']['name'],
                'amount': current_request['total_amount'],
                'timestamp': datetime.now()
            })
            
            # 步骤3：部门主管审批
            def dept_approve_step(request, user):
                request_copy = request.copy()
                request_copy.update({
                    'status': 'dept_approved',
                    'current_step': 'general_manager',
                    'dept_approved_at': datetime.now(),
                    'dept_approved_by': user['id']
                })
                return request_copy
            
            current_request = dept_approve_step(current_request, self.users['dept_manager'])
            workflow_log.append({
                'step': 'dept_approve',
                'status': current_request['status'],
                'operator': self.users['dept_manager']['name'],
                'timestamp': datetime.now()
            })
            
            # 步骤4：总经理最终审批
            def final_approve_step(request, user):
                request_copy = request.copy()
                request_copy.update({
                    'status': 'final_approved',
                    'current_step': 'completed',
                    'final_approved_at': datetime.now(),
                    'final_approved_by': user['id']
                })
                return request_copy
            
            current_request = final_approve_step(current_request, self.users['general_manager'])
            workflow_log.append({
                'step': 'final_approve',
                'status': current_request['status'],
                'operator': self.users['general_manager']['name'],
                'timestamp': datetime.now()
            })
            
            return {
                'final_request': current_request,
                'workflow_log': workflow_log,
                'total_steps': len(workflow_log),
                'final_status': current_request['status']
            }
        
        # 执行完整工作流
        result = execute_complete_workflow(self.sample_purchase_request)
        
        assert result['total_steps'] == 4
        assert result['final_status'] == 'final_approved'
        assert result['final_request']['status'] == 'final_approved'
        
        # 验证工作流步骤顺序
        expected_steps = ['submit', 'quote', 'dept_approve', 'final_approve']
        actual_steps = [log['step'] for log in result['workflow_log']]
        assert actual_steps == expected_steps
        
        # 验证每个步骤的操作员正确
        expected_operators = ['孙赟', '赵采购员', '李工程部主管', '张总经理']
        actual_operators = [log['operator'] for log in result['workflow_log']]
        assert actual_operators == expected_operators
        
        print("   ✅ 完整工作流执行成功")
        print(f"   📊 总步骤数: {result['total_steps']}")
        print(f"   🎯 最终状态: {result['final_status']}")
        
        # 打印工作流日志
        for i, log in enumerate(result['workflow_log'], 1):
            step_amount = f", 金额: ¥{log['amount']}" if log.get('amount') else ""
            print(f"   {i}. {log['step']} - {log['operator']}{step_amount}")
    
    def test_workflow_return_functionality(self):
        """测试工作流退回功能"""
        print("\n⬅️ 测试工作流退回功能...")
        
        def return_purchase_request(purchase_request, return_data, current_user):
            """工作流退回业务逻辑"""
            # 权限检查 - 不同角色可以在不同阶段退回
            return_permissions = {
                'purchaser': ['submitted'],  # 采购员可以退回已提交的给项目经理
                'dept_manager': ['price_quoted'],  # 部门主管可以退回已询价的给采购员
                'general_manager': ['dept_approved'],  # 总经理可以退回部门批准的
                'admin': ['submitted', 'price_quoted', 'dept_approved']  # 管理员可以在任何阶段退回
            }
            
            current_status = purchase_request['status']
            allowed_statuses = return_permissions.get(current_user['role'], [])
            
            if current_status not in allowed_statuses:
                return {
                    'success': False,
                    'error': 'permission_denied',
                    'message': f"{current_user['role']}角色无权在{current_status}状态下退回"
                }
            
            # 退回理由检查
            if not return_data.get('return_reason'):
                return {
                    'success': False,
                    'error': 'validation_failed',
                    'message': "退回时必须填写退回理由"
                }
            
            # 确定退回目标状态和负责人
            return_mappings = {
                'submitted': {'target_status': 'draft', 'target_step': 'project_manager'},
                'price_quoted': {'target_status': 'submitted', 'target_step': 'purchaser'},
                'dept_approved': {'target_status': 'price_quoted', 'target_step': 'dept_manager'}
            }
            
            mapping = return_mappings.get(current_status)
            if not mapping:
                return {
                    'success': False,
                    'error': 'invalid_operation',
                    'message': f"状态{current_status}不支持退回操作"
                }
            
            # 执行退回
            updated_request = purchase_request.copy()
            updated_request.update({
                'status': mapping['target_status'],
                'current_step': mapping['target_step'],
                'returned_at': datetime.now(),
                'returned_by': current_user['id'],
                'return_reason': return_data['return_reason'],
                'return_from_status': current_status
            })
            
            return {
                'success': True,
                'updated_request': updated_request,
                'message': f"申购单已退回至{mapping['target_status']}状态",
                'return_info': {
                    'from_status': current_status,
                    'to_status': mapping['target_status'],
                    'reason': return_data['return_reason']
                }
            }
        
        # 测试场景1：部门主管退回已询价的申购单给采购员
        quoted_request = self.sample_purchase_request.copy()
        quoted_request['status'] = 'price_quoted'
        
        return_data = {
            'return_reason': '价格偏高，建议重新询价或寻找更优供应商'
        }
        
        result = return_purchase_request(quoted_request, return_data, self.users['dept_manager'])
        
        assert result['success'] == True
        assert result['updated_request']['status'] == 'submitted'
        assert result['updated_request']['current_step'] == 'purchaser'
        assert result['return_info']['from_status'] == 'price_quoted'
        assert result['return_info']['to_status'] == 'submitted'
        print("   ✅ 部门主管成功退回申购单给采购员")
        
        # 测试场景2：采购员退回已提交的申购单给项目经理
        submitted_request = self.sample_purchase_request.copy()
        submitted_request['status'] = 'submitted'
        
        return_data = {
            'return_reason': '申购明细信息不完整，需要补充详细规格参数'
        }
        
        result = return_purchase_request(submitted_request, return_data, self.users['purchaser'])
        
        assert result['success'] == True
        assert result['updated_request']['status'] == 'draft'
        assert result['updated_request']['current_step'] == 'project_manager'
        print("   ✅ 采购员成功退回申购单给项目经理")
        
        # 测试场景3：无权限退回
        result = return_purchase_request(quoted_request, return_data, self.users['pm_sunyun'])
        
        assert result['success'] == False
        assert result['error'] == 'permission_denied'
        print("   ✅ 无权限退回被正确阻止")
        
        # 测试场景4：缺少退回理由
        empty_reason_data = {'return_reason': ''}
        result = return_purchase_request(quoted_request, empty_reason_data, self.users['dept_manager'])
        
        assert result['success'] == False
        assert result['error'] == 'validation_failed'
        assert "必须填写退回理由" in result['message']
        print("   ✅ 缺少退回理由被正确阻止")


def run_workflow_approval_tests():
    """运行所有工作流审批测试"""
    print("🔄 开始运行工作流审批功能测试...")
    print("=" * 60)
    
    test_instance = TestWorkflowApproval()
    
    test_methods = [
        test_instance.test_submit_workflow_step,
        test_instance.test_quote_workflow_step,
        test_instance.test_department_approval_step,
        test_instance.test_final_approval_step,
        test_instance.test_complete_workflow_integration,
        test_instance.test_workflow_return_functionality
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
    print(f"📊 工作流审批功能测试结果: {passed} 通过, {failed} 失败")
    
    return failed == 0


if __name__ == "__main__":
    success = run_workflow_approval_tests()
    exit(0 if success else 1)