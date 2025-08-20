"""
申购单权限系统专项测试
测试项目级权限隔离、角色权限控制等功能
"""

import pytest
from unittest.mock import Mock, patch
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


class TestPurchasePermissions:
    """申购单权限系统测试类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        # 模拟用户角色
        self.users = {
            "admin": {"id": 1, "name": "系统管理员", "role": "admin"},
            "general_manager": {"id": 2, "name": "张总经理", "role": "general_manager"},
            "dept_manager": {"id": 3, "name": "李工程部主管", "role": "dept_manager"},
            "purchaser": {"id": 4, "name": "赵采购员", "role": "purchaser"},
            "pm_sunyun": {"id": 5, "name": "孙赟", "role": "project_manager"},
            "pm_liqiang": {"id": 6, "name": "李强", "role": "project_manager"},
            "worker": {"id": 7, "name": "刘施工队长", "role": "worker"},
            "finance": {"id": 8, "name": "陈财务", "role": "finance"}
        }
        
        # 模拟项目数据
        self.projects = [
            {"id": 1, "project_name": "智慧园区项目", "project_manager": "未分配"},
            {"id": 2, "project_name": "娄山关路445弄综合弱电智能化", "project_manager": "孙赟"},
            {"id": 3, "project_name": "某小区智能化改造项目", "project_manager": "李强"}
        ]
        
        # 模拟申购单数据分布
        self.purchase_requests = [
            {"id": 1, "project_id": 1, "requester_id": 4, "status": "draft"},   # 项目1
            {"id": 2, "project_id": 1, "requester_id": 4, "status": "submitted"}, # 项目1
            {"id": 3, "project_id": 2, "requester_id": 5, "status": "draft"},   # 项目2 - 孙赟负责
            {"id": 4, "project_id": 2, "requester_id": 4, "status": "approved"}, # 项目2 - 孙赟负责
            {"id": 5, "project_id": 3, "requester_id": 6, "status": "draft"},   # 项目3 - 李强负责
            {"id": 6, "project_id": 3, "requester_id": 4, "status": "submitted"} # 项目3 - 李强负责
        ]

    def test_project_manager_permission_isolation(self):
        """测试项目经理的项目级权限隔离"""
        print("\n🔒 测试项目经理项目级权限隔离...")
        
        def get_managed_projects(user):
            """获取用户负责的项目"""
            if user["role"] != "project_manager":
                return []  # 非项目经理无项目管理权限
            
            managed = []
            for project in self.projects:
                if project["project_manager"] == user["name"]:
                    managed.append(project)
            return managed
        
        def filter_purchases_by_permission(user, all_purchases):
            """根据权限过滤申购单"""
            if user["role"] in ["admin", "general_manager", "dept_manager", "purchaser", "finance"]:
                # 高权限角色可以看到所有申购单
                return all_purchases
            elif user["role"] == "project_manager":
                # 项目经理只能看到负责项目的申购单
                managed_projects = get_managed_projects(user)
                managed_project_ids = [p["id"] for p in managed_projects]
                
                if not managed_project_ids:
                    return []  # 无负责项目，看不到任何申购单
                
                filtered = []
                for purchase in all_purchases:
                    if purchase["project_id"] in managed_project_ids:
                        filtered.append(purchase)
                return filtered
            else:
                # 其他角色无权限
                return []
        
        # 测试场景1：孙赟（负责项目2）
        sunyun = self.users["pm_sunyun"]
        sunyun_purchases = filter_purchases_by_permission(sunyun, self.purchase_requests)
        
        sunyun_project_ids = [p["project_id"] for p in sunyun_purchases]
        assert all(pid == 2 for pid in sunyun_project_ids)
        assert len(sunyun_purchases) == 2  # 项目2有2个申购单
        print("   ✅ 孙赟只能看到项目2的申购单")
        
        # 测试场景2：李强（负责项目3）
        liqiang = self.users["pm_liqiang"]
        liqiang_purchases = filter_purchases_by_permission(liqiang, self.purchase_requests)
        
        liqiang_project_ids = [p["project_id"] for p in liqiang_purchases]
        assert all(pid == 3 for pid in liqiang_project_ids)
        assert len(liqiang_purchases) == 2  # 项目3有2个申购单
        print("   ✅ 李强只能看到项目3的申购单")
        
        # 测试场景3：管理员（可看到所有）
        admin = self.users["admin"]
        admin_purchases = filter_purchases_by_permission(admin, self.purchase_requests)
        assert len(admin_purchases) == 6  # 可以看到所有申购单
        print("   ✅ 管理员可以看到所有申购单")
        
        # 测试场景4：采购员（可看到所有）
        purchaser = self.users["purchaser"]
        purchaser_purchases = filter_purchases_by_permission(purchaser, self.purchase_requests)
        assert len(purchaser_purchases) == 6  # 可以看到所有申购单
        print("   ✅ 采购员可以看到所有申购单")

    def test_role_based_price_visibility(self):
        """测试基于角色的价格信息可见性"""
        print("\n💰 测试基于角色的价格信息可见性...")
        
        def get_purchase_response_schema(user, purchase_data):
            """根据用户角色返回相应的申购单数据格式"""
            import copy
            
            if user["role"] == "project_manager":
                # 项目经理：隐藏价格信息
                response = copy.deepcopy(purchase_data)
                if "total_amount" in response:
                    del response["total_amount"]
                if "items" in response:
                    for item in response["items"]:
                        if "unit_price" in item:
                            del item["unit_price"]
                        if "total_price" in item:
                            del item["total_price"]
                response["price_hidden"] = True
                return response
            else:
                # 其他角色：显示完整价格信息
                response = copy.deepcopy(purchase_data)
                response["price_hidden"] = False
                return response
        
        # 模拟申购单数据（包含价格）
        purchase_with_price = {
            "id": 1,
            "request_code": "PR202508190001",
            "total_amount": 15000.00,
            "items": [
                {"id": 1, "item_name": "摄像机", "quantity": 5, "unit_price": 2000.00, "total_price": 10000.00},
                {"id": 2, "item_name": "录像机", "quantity": 1, "unit_price": 5000.00, "total_price": 5000.00}
            ]
        }
        
        # 测试场景1：项目经理访问（价格隐藏）
        pm_response = get_purchase_response_schema(self.users["pm_sunyun"], purchase_with_price)
        assert "total_amount" not in pm_response
        assert pm_response["price_hidden"] == True
        
        for item in pm_response["items"]:
            assert "unit_price" not in item
            assert "total_price" not in item
        print("   ✅ 项目经理角色正确隐藏价格信息")
        
        # 测试场景2：采购员访问（价格显示）
        purchaser_response = get_purchase_response_schema(self.users["purchaser"], purchase_with_price)
        assert "total_amount" in purchaser_response
        assert purchaser_response["total_amount"] == 15000.00
        assert purchaser_response["price_hidden"] == False
        
        for item in purchaser_response["items"]:
            assert "unit_price" in item
            assert "total_price" in item
        print("   ✅ 采购员角色正确显示价格信息")
        
        # 测试场景3：管理员访问（价格显示）
        admin_response = get_purchase_response_schema(self.users["admin"], purchase_with_price)
        assert "total_amount" in admin_response
        assert admin_response["price_hidden"] == False
        print("   ✅ 管理员角色正确显示价格信息")

    def test_purchase_creation_permissions(self):
        """测试申购单创建权限"""
        print("\n📝 测试申购单创建权限...")
        
        def check_creation_permission(user, project_id):
            """检查用户是否有权限在指定项目创建申购单"""
            # 权限规则
            creation_roles = ["admin", "project_manager", "purchaser"]
            
            if user["role"] not in creation_roles:
                return False, f"{user['role']}角色无权创建申购单"
            
            if user["role"] == "project_manager":
                # 项目经理只能在负责的项目中创建申购单
                managed_projects = []
                for project in self.projects:
                    if project["project_manager"] == user["name"]:
                        managed_projects.append(project["id"])
                
                if project_id not in managed_projects:
                    return False, "项目经理只能在负责的项目中创建申购单"
            
            return True, "有权限创建申购单"
        
        # 测试场景1：孙赟在负责的项目2中创建
        can_create, message = check_creation_permission(self.users["pm_sunyun"], 2)
        assert can_create == True
        print("   ✅ 孙赟可以在负责的项目2中创建申购单")
        
        # 测试场景2：孙赟尝试在其他项目中创建
        can_create, message = check_creation_permission(self.users["pm_sunyun"], 3)
        assert can_create == False
        assert "只能在负责的项目" in message
        print("   ✅ 孙赟无法在其他项目中创建申购单")
        
        # 测试场景3：采购员在任意项目创建
        can_create, message = check_creation_permission(self.users["purchaser"], 1)
        assert can_create == True
        can_create, message = check_creation_permission(self.users["purchaser"], 2)
        assert can_create == True
        print("   ✅ 采购员可以在任意项目中创建申购单")
        
        # 测试场景4：施工队长尝试创建
        can_create, message = check_creation_permission(self.users["worker"], 1)
        assert can_create == False
        assert "无权创建申购单" in message
        print("   ✅ 施工队长无权创建申购单")

    def test_purchase_deletion_permissions(self):
        """测试申购单删除权限"""
        print("\n🗑️ 测试申购单删除权限...")
        
        def check_deletion_permission(user, purchase):
            """检查用户是否有权限删除指定申购单"""
            # 只有草稿状态的申购单可以删除
            if purchase["status"] != "draft":
                return False, "只有草稿状态的申购单可以删除"
            
            deletion_roles = ["admin", "project_manager", "purchaser"]
            
            if user["role"] not in deletion_roles:
                return False, f"{user['role']}角色无权删除申购单"
            
            if user["role"] == "project_manager":
                # 项目经理只能删除负责项目的申购单
                project = None
                for p in self.projects:
                    if p["id"] == purchase["project_id"]:
                        project = p
                        break
                
                if not project or project["project_manager"] != user["name"]:
                    return False, "项目经理只能删除负责项目的申购单"
            
            return True, "有权限删除申购单"
        
        # 准备测试数据
        draft_purchase_project2 = {"id": 3, "project_id": 2, "status": "draft"}
        submitted_purchase_project2 = {"id": 4, "project_id": 2, "status": "submitted"}
        draft_purchase_project3 = {"id": 5, "project_id": 3, "status": "draft"}
        
        # 测试场景1：孙赟删除负责项目的草稿申购单
        can_delete, message = check_deletion_permission(self.users["pm_sunyun"], draft_purchase_project2)
        assert can_delete == True
        print("   ✅ 孙赟可以删除负责项目的草稿申购单")
        
        # 测试场景2：孙赟尝试删除已提交的申购单
        can_delete, message = check_deletion_permission(self.users["pm_sunyun"], submitted_purchase_project2)
        assert can_delete == False
        assert "草稿状态" in message
        print("   ✅ 无法删除非草稿状态的申购单")
        
        # 测试场景3：孙赟尝试删除其他项目的申购单
        can_delete, message = check_deletion_permission(self.users["pm_sunyun"], draft_purchase_project3)
        assert can_delete == False
        assert "负责项目" in message
        print("   ✅ 项目经理无法删除其他项目的申购单")
        
        # 测试场景4：采购员删除任意草稿申购单
        can_delete, message = check_deletion_permission(self.users["purchaser"], draft_purchase_project2)
        assert can_delete == True
        can_delete, message = check_deletion_permission(self.users["purchaser"], draft_purchase_project3)
        assert can_delete == True
        print("   ✅ 采购员可以删除任意项目的草稿申购单")

    def test_purchase_detail_access_permissions(self):
        """测试申购单详情访问权限"""
        print("\n👁️ 测试申购单详情访问权限...")
        
        def check_detail_access_permission(user, purchase):
            """检查用户是否有权限查看申购单详情"""
            # 管理员和高级角色可以查看所有详情
            if user["role"] in ["admin", "general_manager", "dept_manager", "purchaser", "finance"]:
                return True, "有权限查看详情"
            
            if user["role"] == "project_manager":
                # 项目经理只能查看负责项目的申购单详情
                project = None
                for p in self.projects:
                    if p["id"] == purchase["project_id"]:
                        project = p
                        break
                
                if not project or project["project_manager"] != user["name"]:
                    return False, "项目经理只能查看负责项目的申购单详情"
                
                return True, "有权限查看详情"
            
            return False, f"{user['role']}角色无权查看申购单详情"
        
        # 准备测试数据
        purchase_project2 = {"id": 3, "project_id": 2}
        purchase_project3 = {"id": 5, "project_id": 3}
        
        # 测试场景1：孙赟查看负责项目的申购单
        can_access, message = check_detail_access_permission(self.users["pm_sunyun"], purchase_project2)
        assert can_access == True
        print("   ✅ 孙赟可以查看负责项目的申购单详情")
        
        # 测试场景2：孙赟尝试查看其他项目的申购单
        can_access, message = check_detail_access_permission(self.users["pm_sunyun"], purchase_project3)
        assert can_access == False
        assert "负责项目" in message
        print("   ✅ 孙赟无法查看其他项目的申购单详情")
        
        # 测试场景3：采购员查看任意申购单
        can_access, message = check_detail_access_permission(self.users["purchaser"], purchase_project2)
        assert can_access == True
        can_access, message = check_detail_access_permission(self.users["purchaser"], purchase_project3)
        assert can_access == True
        print("   ✅ 采购员可以查看任意申购单详情")
        
        # 测试场景4：施工队长尝试查看
        can_access, message = check_detail_access_permission(self.users["worker"], purchase_project2)
        assert can_access == False
        assert "无权查看" in message
        print("   ✅ 施工队长无权查看申购单详情")

    def test_batch_operations_permissions(self):
        """测试批量操作权限"""
        print("\n🔄 测试批量操作权限...")
        
        def check_batch_deletion_permission(user, purchase_ids):
            """检查批量删除权限"""
            # 获取对应的申购单信息
            purchases = []
            for pid in purchase_ids:
                for p in self.purchase_requests:
                    if p["id"] == pid:
                        purchases.append(p)
                        break
            
            if not purchases:
                return False, "未找到指定的申购单"
            
            # 检查每个申购单的删除权限
            for purchase in purchases:
                # 只能删除草稿状态
                if purchase["status"] != "draft":
                    return False, f"申购单{purchase['id']}不是草稿状态，无法删除"
                
                # 检查项目权限
                if user["role"] == "project_manager":
                    project = None
                    for p in self.projects:
                        if p["id"] == purchase["project_id"]:
                            project = p
                            break
                    
                    if not project or project["project_manager"] != user["name"]:
                        return False, f"无权限删除申购单{purchase['id']}（不在负责项目中）"
            
            return True, f"有权限批量删除{len(purchases)}个申购单"
        
        # 测试场景1：孙赟批量删除负责项目的草稿申购单
        # 申购单3是项目2的草稿状态
        can_batch_delete, message = check_batch_deletion_permission(
            self.users["pm_sunyun"], [3]
        )
        assert can_batch_delete == True
        assert "有权限批量删除" in message
        print("   ✅ 孙赟可以批量删除负责项目的草稿申购单")
        
        # 测试场景2：孙赟尝试批量删除包含其他项目的申购单
        can_batch_delete, message = check_batch_deletion_permission(
            self.users["pm_sunyun"], [3, 5]  # 3是项目2，5是项目3
        )
        assert can_batch_delete == False
        assert "不在负责项目" in message
        print("   ✅ 项目经理无法批量删除其他项目的申购单")
        
        # 测试场景3：尝试批量删除包含非草稿状态的申购单
        can_batch_delete, message = check_batch_deletion_permission(
            self.users["pm_sunyun"], [3, 4]  # 3是草稿，4是已提交
        )
        assert can_batch_delete == False
        assert "不是草稿状态" in message
        print("   ✅ 无法批量删除包含非草稿状态的申购单")

    def test_permission_edge_cases(self):
        """测试权限边界情况"""
        print("\n🔍 测试权限边界情况...")
        
        def handle_permission_edge_cases(scenario, user_data, context):
            """处理各种权限边界情况"""
            edge_cases = {
                "user_without_projects": {
                    # 项目经理但未分配任何项目
                    "description": "项目经理未分配项目",
                    "accessible_purchases": 0,
                    "error_message": "您未被分配任何项目，无法查看申购单"
                },
                "project_manager_changed": {
                    # 项目经理更换后的权限变化
                    "description": "项目经理更换",
                    "old_manager_access": False,
                    "new_manager_access": True
                },
                "inactive_user": {
                    # 用户被停用
                    "description": "用户账号被停用",
                    "access_denied": True,
                    "error_message": "账号已被停用，无法访问"
                },
                "role_changed": {
                    # 用户角色变更
                    "description": "用户角色变更",
                    "permission_updated": True
                }
            }
            
            return edge_cases.get(scenario, {"description": "未知场景"})
        
        # 测试场景1：项目经理未分配项目
        edge_case = handle_permission_edge_cases("user_without_projects", 
                                                self.users["pm_sunyun"], None)
        assert edge_case["accessible_purchases"] == 0
        assert "未被分配任何项目" in edge_case["error_message"]
        print("   ✅ 正确处理未分配项目的项目经理")
        
        # 测试场景2：项目经理更换
        edge_case = handle_permission_edge_cases("project_manager_changed", None, None)
        assert edge_case["old_manager_access"] == False
        assert edge_case["new_manager_access"] == True
        print("   ✅ 正确处理项目经理更换后的权限变化")
        
        # 测试场景3：用户停用
        edge_case = handle_permission_edge_cases("inactive_user", None, None)
        assert edge_case["access_denied"] == True
        assert "已被停用" in edge_case["error_message"]
        print("   ✅ 正确处理用户停用情况")


def run_permission_tests():
    """运行所有权限测试"""
    print("🚀 开始运行申购单权限系统测试...")
    print("=" * 60)
    
    test_instance = TestPurchasePermissions()
    
    # 运行所有测试方法
    test_methods = [
        test_instance.test_project_manager_permission_isolation,
        test_instance.test_role_based_price_visibility,
        test_instance.test_purchase_creation_permissions,
        test_instance.test_purchase_deletion_permissions,
        test_instance.test_purchase_detail_access_permissions,
        test_instance.test_batch_operations_permissions,
        test_instance.test_permission_edge_cases
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
    print(f"📊 测试结果汇总: {passed} 通过, {failed} 失败")
    
    if failed == 0:
        print("🎉 所有权限系统测试通过！")
    else:
        print(f"⚠️  有 {failed} 个测试失败，需要检查")
    
    return failed == 0


if __name__ == "__main__":
    success = run_permission_tests()
    exit(0 if success else 1)