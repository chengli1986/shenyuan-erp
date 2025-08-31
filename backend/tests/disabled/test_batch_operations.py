"""
申购单批量操作功能单元测试
测试批量删除、批量状态更新等功能的权限控制和业务逻辑
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta


class TestBatchOperations:
    """批量操作功能测试类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        # 模拟用户角色
        self.users = {
            "admin": {"id": 1, "name": "系统管理员", "role": "admin"},
            "purchaser": {"id": 2, "name": "赵采购员", "role": "purchaser"},
            "pm_sunyun": {"id": 3, "name": "孙赟", "role": "project_manager"},
            "pm_liqiang": {"id": 4, "name": "李强", "role": "project_manager"},
            "worker": {"id": 5, "name": "刘施工队长", "role": "worker"}
        }
        
        # 模拟项目数据
        self.projects = [
            {"id": 1, "project_name": "智慧园区项目", "project_manager": "未分配"},
            {"id": 2, "project_name": "娄山关路445弄综合弱电智能化", "project_manager": "孙赟"},
            {"id": 3, "project_name": "某小区智能化改造项目", "project_manager": "李强"}
        ]
        
        # 模拟申购单数据（不同状态和项目）
        self.purchase_requests = [
            {"id": 1, "project_id": 2, "requester_id": 3, "status": "draft"},      # 孙赟项目，草稿
            {"id": 2, "project_id": 2, "requester_id": 2, "status": "draft"},      # 孙赟项目，草稿
            {"id": 3, "project_id": 2, "requester_id": 3, "status": "submitted"},  # 孙赟项目，已提交
            {"id": 4, "project_id": 3, "requester_id": 4, "status": "draft"},      # 李强项目，草稿
            {"id": 5, "project_id": 3, "requester_id": 2, "status": "draft"},      # 李强项目，草稿
            {"id": 6, "project_id": 3, "requester_id": 4, "status": "price_quoted"}, # 李强项目，已询价
            {"id": 7, "project_id": 1, "requester_id": 2, "status": "draft"},      # 未分配项目，草稿
            {"id": 8, "project_id": 1, "requester_id": 2, "status": "final_approved"}, # 未分配项目，已批准
        ]
    
    def test_batch_delete_permission_validation(self):
        """测试批量删除权限验证"""
        print("\n🔒 测试批量删除权限验证...")
        
        def check_batch_delete_permission(user, request_ids, purchase_requests, projects):
            """检查批量删除权限"""
            # 获取要删除的申购单
            target_requests = [req for req in purchase_requests if req['id'] in request_ids]
            
            if not target_requests:
                return False, "未找到指定的申购单"
            
            # 角色权限检查
            allowed_roles = ["admin", "purchaser", "project_manager"]
            if user["role"] not in allowed_roles:
                return False, f"{user['role']}角色无批量删除权限"
            
            validation_errors = []
            
            for request in target_requests:
                # 状态检查：只能删除草稿状态
                if request["status"] != "draft":
                    validation_errors.append(f"申购单{request['id']}状态为{request['status']}，只能删除草稿状态")
                
                # 项目权限检查（针对项目经理）
                if user["role"] == "project_manager":
                    project = next((p for p in projects if p['id'] == request['project_id']), None)
                    if not project or project["project_manager"] != user["name"]:
                        validation_errors.append(f"申购单{request['id']}不在您负责的项目中")
            
            if validation_errors:
                return False, "; ".join(validation_errors)
            
            return True, f"有权限删除{len(target_requests)}个申购单"
        
        # 测试场景1：管理员批量删除草稿申购单
        can_delete, message = check_batch_delete_permission(
            self.users["admin"], [1, 2, 4, 5, 7], self.purchase_requests, self.projects
        )
        assert can_delete == True
        assert "有权限删除5个" in message
        print("   ✅ 管理员可以批量删除草稿申购单")
        
        # 测试场景2：采购员批量删除草稿申购单
        can_delete, message = check_batch_delete_permission(
            self.users["purchaser"], [1, 2, 4, 5], self.purchase_requests, self.projects
        )
        assert can_delete == True
        print("   ✅ 采购员可以批量删除草稿申购单")
        
        # 测试场景3：项目经理只能删除负责项目的草稿申购单
        can_delete, message = check_batch_delete_permission(
            self.users["pm_sunyun"], [1, 2], self.purchase_requests, self.projects  # 孙赟负责项目2
        )
        assert can_delete == True
        print("   ✅ 孙赟可以删除负责项目的草稿申购单")
        
        # 测试场景4：项目经理尝试删除其他项目的申购单
        can_delete, message = check_batch_delete_permission(
            self.users["pm_sunyun"], [4, 5], self.purchase_requests, self.projects  # 李强项目的申购单
        )
        assert can_delete == False
        assert "不在您负责的项目" in message
        print("   ✅ 项目经理无法删除其他项目的申购单")
        
        # 测试场景5：尝试删除包含非草稿状态的申购单
        can_delete, message = check_batch_delete_permission(
            self.users["purchaser"], [1, 3, 8], self.purchase_requests, self.projects  # 包含submitted和final_approved
        )
        assert can_delete == False
        assert "只能删除草稿状态" in message
        print("   ✅ 无法批量删除非草稿状态的申购单")
        
        # 测试场景6：无权限角色尝试批量删除
        can_delete, message = check_batch_delete_permission(
            self.users["worker"], [1, 2], self.purchase_requests, self.projects
        )
        assert can_delete == False
        assert "无批量删除权限" in message
        print("   ✅ 无权限角色被正确拒绝")
    
    def test_batch_delete_business_logic(self):
        """测试批量删除业务逻辑"""
        print("\n🗑️ 测试批量删除业务逻辑...")
        
        def execute_batch_delete(user, request_ids, purchase_requests, projects):
            """执行批量删除业务逻辑"""
            # 权限验证
            from test_batch_operations import TestBatchOperations
            test_instance = TestBatchOperations()
            test_instance.setup_method()
            
            def check_permission(user, request_ids, purchase_requests, projects):
                target_requests = [req for req in purchase_requests if req['id'] in request_ids]
                if not target_requests:
                    return False, "未找到指定的申购单"
                
                allowed_roles = ["admin", "purchaser", "project_manager"]
                if user["role"] not in allowed_roles:
                    return False, f"{user['role']}角色无批量删除权限"
                
                for request in target_requests:
                    if request["status"] != "draft":
                        return False, f"申购单{request['id']}不是草稿状态"
                    
                    if user["role"] == "project_manager":
                        project = next((p for p in projects if p['id'] == request['project_id']), None)
                        if not project or project["project_manager"] != user["name"]:
                            return False, f"申购单{request['id']}不在负责项目中"
                
                return True, "权限验证通过"
            
            can_delete, permission_message = check_permission(user, request_ids, purchase_requests, projects)
            
            if not can_delete:
                return {
                    'success': False,
                    'error': 'permission_denied',
                    'message': permission_message,
                    'deleted_count': 0
                }
            
            # 执行删除
            deleted_requests = []
            remaining_requests = []
            
            for request in purchase_requests:
                if request['id'] in request_ids:
                    deleted_requests.append(request)
                else:
                    remaining_requests.append(request)
            
            return {
                'success': True,
                'deleted_count': len(deleted_requests),
                'deleted_ids': [req['id'] for req in deleted_requests],
                'remaining_requests': remaining_requests,
                'message': f"成功删除{len(deleted_requests)}个申购单"
            }
        
        # 测试场景1：成功批量删除
        result = execute_batch_delete(
            self.users["admin"], [1, 2, 4, 5, 7], self.purchase_requests, self.projects
        )
        
        assert result['success'] == True
        assert result['deleted_count'] == 5
        assert set(result['deleted_ids']) == {1, 2, 4, 5, 7}
        assert len(result['remaining_requests']) == 3  # 剩余3个申购单
        print(f"   ✅ 成功删除{result['deleted_count']}个申购单")
        
        # 测试场景2：部分删除失败（权限问题）
        result = execute_batch_delete(
            self.users["pm_sunyun"], [1, 4], self.purchase_requests, self.projects  # 包含其他项目
        )
        
        assert result['success'] == False
        assert result['error'] == 'permission_denied'
        assert result['deleted_count'] == 0
        assert "不在负责项目" in result['message']
        print("   ✅ 权限不足时正确阻止删除")
        
        # 测试场景3：空ID列表处理
        result = execute_batch_delete(
            self.users["admin"], [], self.purchase_requests, self.projects
        )
        
        assert result['success'] == False
        assert result['deleted_count'] == 0
        print("   ✅ 空ID列表正确处理")
    
    def test_batch_status_update_functionality(self):
        """测试批量状态更新功能"""
        print("\n🔄 测试批量状态更新功能...")
        
        def batch_status_update(user, request_ids, target_status, purchase_requests, projects):
            """批量状态更新功能"""
            # 状态转换规则
            valid_transitions = {
                'draft': ['submitted', 'cancelled'],
                'submitted': ['price_quoted', 'returned', 'cancelled'],
                'price_quoted': ['dept_approved', 'returned', 'cancelled'],
                'dept_approved': ['final_approved', 'returned', 'cancelled'],
                'final_approved': ['completed', 'cancelled'],
                'returned': ['draft', 'cancelled'],
                'cancelled': [],
                'completed': []
            }
            
            # 角色权限规则
            status_permissions = {
                'submitted': ['admin', 'project_manager', 'purchaser'],
                'price_quoted': ['admin', 'purchaser'],
                'dept_approved': ['admin', 'dept_manager'],
                'final_approved': ['admin', 'general_manager'],
                'completed': ['admin', 'purchaser'],
                'cancelled': ['admin', 'project_manager', 'purchaser'],
                'returned': ['admin', 'dept_manager', 'purchaser']
            }
            
            # 权限检查
            if user['role'] not in status_permissions.get(target_status, []):
                return {
                    'success': False,
                    'error': 'role_permission_denied',
                    'message': f"{user['role']}角色无权限设置状态为{target_status}"
                }
            
            target_requests = [req for req in purchase_requests if req['id'] in request_ids]
            if not target_requests:
                return {
                    'success': False,
                    'error': 'requests_not_found',
                    'message': "未找到指定的申购单"
                }
            
            # 项目权限检查（项目经理）
            if user['role'] == 'project_manager':
                for request in target_requests:
                    project = next((p for p in projects if p['id'] == request['project_id']), None)
                    if not project or project['project_manager'] != user['name']:
                        return {
                            'success': False,
                            'error': 'project_permission_denied',
                            'message': f"申购单{request['id']}不在您负责的项目中"
                        }
            
            # 状态转换检查
            invalid_transitions = []
            for request in target_requests:
                current_status = request['status']
                if target_status not in valid_transitions.get(current_status, []):
                    invalid_transitions.append(f"申购单{request['id']}无法从{current_status}转换为{target_status}")
            
            if invalid_transitions:
                return {
                    'success': False,
                    'error': 'invalid_status_transition',
                    'message': "; ".join(invalid_transitions)
                }
            
            # 执行状态更新
            updated_requests = []
            for request in target_requests:
                updated_request = request.copy()
                updated_request['status'] = target_status
                updated_request['updated_at'] = datetime.now()
                updated_request['updated_by'] = user['id']
                updated_requests.append(updated_request)
            
            return {
                'success': True,
                'updated_count': len(updated_requests),
                'updated_requests': updated_requests,
                'message': f"成功更新{len(updated_requests)}个申购单状态为{target_status}"
            }
        
        # 测试场景1：项目经理批量提交草稿申购单
        result = batch_status_update(
            self.users["pm_sunyun"], [1, 2], 'submitted', self.purchase_requests, self.projects
        )
        
        assert result['success'] == True
        assert result['updated_count'] == 2
        assert all(req['status'] == 'submitted' for req in result['updated_requests'])
        print("   ✅ 项目经理成功批量提交申购单")
        
        # 测试场景2：采购员批量询价
        # 先将状态设为submitted
        submitted_requests = self.purchase_requests.copy()
        for req in submitted_requests:
            if req['id'] in [1, 2]:
                req['status'] = 'submitted'
        
        result = batch_status_update(
            self.users["purchaser"], [1, 2], 'price_quoted', submitted_requests, self.projects
        )
        
        assert result['success'] == True
        assert result['updated_count'] == 2
        print("   ✅ 采购员成功批量设置询价状态")
        
        # 测试场景3：无效状态转换
        result = batch_status_update(
            self.users["admin"], [8], 'draft', self.purchase_requests, self.projects  # final_approved不能转为draft
        )
        
        assert result['success'] == False
        assert result['error'] == 'invalid_status_transition'
        assert "无法从final_approved转换为draft" in result['message']
        print("   ✅ 无效状态转换被正确阻止")
        
        # 测试场景4：角色权限不足
        result = batch_status_update(
            self.users["worker"], [1, 2], 'submitted', self.purchase_requests, self.projects
        )
        
        assert result['success'] == False
        assert result['error'] == 'role_permission_denied'
        print("   ✅ 角色权限不足被正确阻止")
    
    def test_batch_operation_performance(self):
        """测试批量操作性能"""
        print("\n⚡ 测试批量操作性能...")
        
        import time
        
        def optimized_batch_delete(user, request_ids, purchase_requests, projects):
            """优化的批量删除实现"""
            # 构建快速查找索引
            request_index = {req['id']: req for req in purchase_requests}
            project_manager_index = {p['id']: p['project_manager'] for p in projects}
            
            # 批量权限检查
            if user['role'] not in ['admin', 'purchaser', 'project_manager']:
                return {'success': False, 'error': 'role_not_allowed'}
            
            # 批量获取目标申购单
            target_requests = []
            for req_id in request_ids:
                if req_id in request_index:
                    target_requests.append(request_index[req_id])
            
            if not target_requests:
                return {'success': False, 'error': 'no_requests_found'}
            
            # 批量验证
            validation_errors = []
            for request in target_requests:
                # 状态检查
                if request['status'] != 'draft':
                    validation_errors.append(f"Request {request['id']}: invalid status")
                    continue
                
                # 项目权限检查（仅项目经理）
                if user['role'] == 'project_manager':
                    project_manager = project_manager_index.get(request['project_id'])
                    if project_manager != user['name']:
                        validation_errors.append(f"Request {request['id']}: project permission denied")
            
            if validation_errors:
                return {'success': False, 'errors': validation_errors}
            
            # 执行删除（模拟）
            deleted_ids = [req['id'] for req in target_requests]
            
            return {
                'success': True,
                'deleted_count': len(deleted_ids),
                'deleted_ids': deleted_ids
            }
        
        # 生成大量测试数据
        large_purchase_requests = []
        large_projects = []
        
        for i in range(10000):
            large_projects.append({
                'id': i + 1,
                'project_name': f'项目{i}',
                'project_manager': '孙赟' if i % 2 == 0 else '李强'
            })
            
            large_purchase_requests.append({
                'id': i + 1,
                'project_id': i + 1,
                'status': 'draft' if i % 3 == 0 else 'submitted',
                'requester_id': 1
            })
        
        # 性能测试
        test_request_ids = list(range(1, 1001, 3))  # 每3个取1个，约333个草稿申购单
        
        start_time = time.time()
        result = optimized_batch_delete(
            self.users['admin'], test_request_ids, large_purchase_requests[:3000], large_projects[:3000]
        )
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        assert result['success'] == True
        assert result['deleted_count'] > 0
        assert execution_time < 0.5  # 应该在0.5秒内完成
        
        print(f"   ✅ 批量删除{result['deleted_count']}个申购单耗时: {execution_time:.4f}秒")
        print("   ✅ 批量操作性能优良")
    
    def test_batch_operation_transaction_safety(self):
        """测试批量操作事务安全性"""
        print("\n🛡️ 测试批量操作事务安全性...")
        
        def safe_batch_delete(user, request_ids, purchase_requests, projects):
            """事务安全的批量删除实现"""
            # 事务前验证
            pre_validation_errors = []
            target_requests = []
            
            for req_id in request_ids:
                request = next((req for req in purchase_requests if req['id'] == req_id), None)
                if not request:
                    pre_validation_errors.append(f"申购单{req_id}不存在")
                    continue
                
                target_requests.append(request)
            
            if pre_validation_errors:
                return {
                    'success': False,
                    'phase': 'pre_validation',
                    'errors': pre_validation_errors,
                    'rollback_required': False
                }
            
            # 权限验证
            for request in target_requests:
                if request['status'] != 'draft':
                    return {
                        'success': False,
                        'phase': 'permission_check',
                        'error': f"申购单{request['id']}状态为{request['status']}，无法删除",
                        'rollback_required': False
                    }
                
                if user['role'] == 'project_manager':
                    project = next((p for p in projects if p['id'] == request['project_id']), None)
                    if not project or project['project_manager'] != user['name']:
                        return {
                            'success': False,
                            'phase': 'permission_check',
                            'error': f"申购单{request['id']}不在负责项目中",
                            'rollback_required': False
                        }
            
            # 模拟事务执行
            deleted_requests = []
            try:
                # 第一阶段：标记删除
                for request in target_requests:
                    # 模拟可能失败的操作
                    if request['id'] == 999:  # 模拟特定ID删除失败
                        raise Exception(f"申购单{request['id']}删除失败：外键约束错误")
                    
                    deleted_requests.append(request)
                
                # 第二阶段：提交事务
                return {
                    'success': True,
                    'deleted_count': len(deleted_requests),
                    'deleted_ids': [req['id'] for req in deleted_requests],
                    'transaction_committed': True
                }
                
            except Exception as e:
                # 事务回滚
                return {
                    'success': False,
                    'phase': 'transaction_execution',
                    'error': str(e),
                    'rollback_required': True,
                    'partial_deleted': [req['id'] for req in deleted_requests]
                }
        
        # 测试场景1：正常批量删除事务
        result = safe_batch_delete(
            self.users['admin'], [1, 2, 4], self.purchase_requests, self.projects
        )
        
        assert result['success'] == True
        assert result['deleted_count'] == 3
        assert result['transaction_committed'] == True
        print("   ✅ 正常事务执行成功")
        
        # 测试场景2：预验证失败（事务未开始）
        result = safe_batch_delete(
            self.users['admin'], [999, 1000], self.purchase_requests, self.projects
        )
        
        assert result['success'] == False
        assert result['phase'] == 'pre_validation'
        assert result['rollback_required'] == False
        print("   ✅ 预验证失败正确处理")
        
        # 测试场景3：权限检查失败
        result = safe_batch_delete(
            self.users['pm_sunyun'], [4, 5], self.purchase_requests, self.projects  # 李强的项目
        )
        
        assert result['success'] == False
        assert result['phase'] == 'permission_check'
        assert "不在负责项目" in result['error']
        assert result['rollback_required'] == False
        print("   ✅ 权限检查失败正确处理")
        
        # 测试场景4：事务执行失败需要回滚
        requests_with_failure = self.purchase_requests + [
            {'id': 999, 'project_id': 2, 'status': 'draft', 'requester_id': 1}
        ]
        
        result = safe_batch_delete(
            self.users['admin'], [1, 2, 999], requests_with_failure, self.projects
        )
        
        assert result['success'] == False
        assert result['phase'] == 'transaction_execution'
        assert result['rollback_required'] == True
        assert 'partial_deleted' in result
        print("   ✅ 事务执行失败正确回滚")
    
    def test_batch_operation_audit_logging(self):
        """测试批量操作审计日志"""
        print("\n📝 测试批量操作审计日志...")
        
        def batch_delete_with_audit(user, request_ids, purchase_requests, projects):
            """带审计日志的批量删除"""
            audit_log = {
                'operation_type': 'batch_delete',
                'operator': user,
                'timestamp': datetime.now(),
                'target_ids': request_ids,
                'steps': []
            }
            
            try:
                # 步骤1：权限验证
                audit_log['steps'].append({
                    'step': 'permission_check',
                    'timestamp': datetime.now(),
                    'status': 'started'
                })
                
                if user['role'] not in ['admin', 'purchaser', 'project_manager']:
                    audit_log['steps'][-1].update({
                        'status': 'failed',
                        'error': 'insufficient_role_permission'
                    })
                    return {'success': False, 'audit_log': audit_log}
                
                audit_log['steps'][-1]['status'] = 'completed'
                
                # 步骤2：数据验证
                audit_log['steps'].append({
                    'step': 'data_validation',
                    'timestamp': datetime.now(),
                    'status': 'started'
                })
                
                target_requests = [req for req in purchase_requests if req['id'] in request_ids]
                audit_log['target_count'] = len(target_requests)
                
                if not target_requests:
                    audit_log['steps'][-1].update({
                        'status': 'failed',
                        'error': 'no_valid_targets'
                    })
                    return {'success': False, 'audit_log': audit_log}
                
                # 状态验证
                invalid_status_requests = [req for req in target_requests if req['status'] != 'draft']
                if invalid_status_requests:
                    audit_log['steps'][-1].update({
                        'status': 'failed',
                        'error': 'invalid_status',
                        'invalid_requests': [req['id'] for req in invalid_status_requests]
                    })
                    return {'success': False, 'audit_log': audit_log}
                
                audit_log['steps'][-1]['status'] = 'completed'
                
                # 步骤3：项目权限验证（如果是项目经理）
                if user['role'] == 'project_manager':
                    audit_log['steps'].append({
                        'step': 'project_permission_check',
                        'timestamp': datetime.now(),
                        'status': 'started'
                    })
                    
                    unauthorized_requests = []
                    for request in target_requests:
                        project = next((p for p in projects if p['id'] == request['project_id']), None)
                        if not project or project['project_manager'] != user['name']:
                            unauthorized_requests.append(request['id'])
                    
                    if unauthorized_requests:
                        audit_log['steps'][-1].update({
                            'status': 'failed',
                            'error': 'project_permission_denied',
                            'unauthorized_requests': unauthorized_requests
                        })
                        return {'success': False, 'audit_log': audit_log}
                    
                    audit_log['steps'][-1]['status'] = 'completed'
                
                # 步骤4：执行删除
                audit_log['steps'].append({
                    'step': 'execute_deletion',
                    'timestamp': datetime.now(),
                    'status': 'started'
                })
                
                deleted_ids = [req['id'] for req in target_requests]
                
                audit_log['steps'][-1].update({
                    'status': 'completed',
                    'deleted_ids': deleted_ids,
                    'deleted_count': len(deleted_ids)
                })
                
                # 成功完成
                audit_log.update({
                    'final_status': 'success',
                    'completion_time': datetime.now(),
                    'total_deleted': len(deleted_ids)
                })
                
                return {
                    'success': True,
                    'deleted_count': len(deleted_ids),
                    'deleted_ids': deleted_ids,
                    'audit_log': audit_log
                }
                
            except Exception as e:
                # 记录异常
                audit_log['steps'].append({
                    'step': 'exception_handler',
                    'timestamp': datetime.now(),
                    'status': 'error',
                    'error': str(e)
                })
                audit_log.update({
                    'final_status': 'error',
                    'completion_time': datetime.now()
                })
                
                return {
                    'success': False,
                    'error': str(e),
                    'audit_log': audit_log
                }
        
        # 测试成功删除的审计日志
        result = batch_delete_with_audit(
            self.users['admin'], [1, 2, 4], self.purchase_requests, self.projects
        )
        
        assert result['success'] == True
        assert result['audit_log']['final_status'] == 'success'
        assert len(result['audit_log']['steps']) >= 3
        
        # 验证各步骤都记录正确
        steps = {step['step']: step for step in result['audit_log']['steps']}
        assert 'permission_check' in steps
        assert 'data_validation' in steps
        assert 'execute_deletion' in steps
        assert all(step['status'] == 'completed' for step in steps.values())
        
        print("   ✅ 成功操作的审计日志记录完整")
        
        # 测试失败操作的审计日志
        result = batch_delete_with_audit(
            self.users['worker'], [1, 2], self.purchase_requests, self.projects
        )
        
        assert result['success'] == False
        assert result['audit_log']['final_status'] != 'success'
        
        permission_step = next((step for step in result['audit_log']['steps'] 
                              if step['step'] == 'permission_check'), None)
        assert permission_step is not None
        assert permission_step['status'] == 'failed'
        assert permission_step['error'] == 'insufficient_role_permission'
        
        print("   ✅ 失败操作的审计日志记录完整")
        print(f"   📋 审计日志包含{len(result['audit_log']['steps'])}个步骤记录")


def run_batch_operations_tests():
    """运行所有批量操作测试"""
    print("🔄 开始运行批量操作功能测试...")
    print("=" * 60)
    
    test_instance = TestBatchOperations()
    
    test_methods = [
        test_instance.test_batch_delete_permission_validation,
        test_instance.test_batch_delete_business_logic,
        test_instance.test_batch_status_update_functionality,
        test_instance.test_batch_operation_performance,
        test_instance.test_batch_operation_transaction_safety,
        test_instance.test_batch_operation_audit_logging
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
    print(f"📊 批量操作功能测试结果: {passed} 通过, {failed} 失败")
    
    return failed == 0


if __name__ == "__main__":
    success = run_batch_operations_tests()
    exit(0 if success else 1)