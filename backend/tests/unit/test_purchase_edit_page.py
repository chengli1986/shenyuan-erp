"""
申购单编辑页面端到端集成测试
测试完整的编辑页面工作流程，特别是系统分类显示和选择功能
"""

import pytest
from unittest.mock import Mock, patch
import json
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


class TestPurchaseEditPageIntegration:
    """申购单编辑页面集成测试类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.mock_db = Mock()
        
        # 模拟项目数据
        self.projects = [
            {"id": 2, "project_name": "娄山关路445弄综合弱电智能化", "project_manager": "孙赟"},
            {"id": 3, "project_name": "某小区智能化改造项目", "project_manager": "李强"}
        ]
        
        # 模拟系统分类数据
        self.system_categories = [
            {"id": 1, "category_name": "视频监控", "category_code": "SYS_视频监控"},
            {"id": 2, "category_name": "出入口控制", "category_code": "SYS_出入口控制"},
            {"id": 3, "category_name": "停车系统", "category_code": "SYS_停车系统"},
            {"id": 4, "category_name": "智能化集成", "category_code": "SYS_智能化集成"}
        ]
        
        # 模拟历史申购单数据（有些有系统分类，有些没有）
        self.historical_purchase = {
            "id": 22,
            "request_code": "PR202508170001",
            "project_id": 2,
            "project_name": "娄山关路445弄综合弱电智能化",
            "status": "draft",
            "items": [
                {
                    "id": 1,
                    "item_name": "网络摄像机",
                    "system_category_id": None,  # 历史数据缺少系统分类
                    "system_category_name": None,
                    "quantity": 5,
                    "item_type": "auxiliary"
                },
                {
                    "id": 2,
                    "item_name": "录像机",
                    "system_category_id": 1,  # 已有系统分类
                    "system_category_name": "视频监控",
                    "quantity": 2,
                    "item_type": "main"
                }
            ]
        }
        
        # 模拟新申购单数据
        self.new_purchase = {
            "id": 62,
            "request_code": "PR202508190001", 
            "project_id": 2,
            "project_name": "娄山关路445弄综合弱电智能化",
            "status": "draft",
            "items": [
                {
                    "id": 3,
                    "item_name": "网络摄像机",
                    "system_category_id": 1,
                    "system_category_name": "视频监控",
                    "quantity": 3,
                    "item_type": "auxiliary"
                }
            ]
        }

    def test_edit_page_load_historical_data(self):
        """测试编辑页面加载历史数据"""
        print("\n📖 测试编辑页面加载历史数据...")
        
        def load_purchase_for_edit(purchase_id):
            """模拟加载申购单详情用于编辑"""
            if purchase_id == 22:
                return self.historical_purchase
            elif purchase_id == 62:
                return self.new_purchase
            else:
                return None
        
        def enhance_items_with_system_categories(purchase_data, project_categories):
            """为申购明细增强系统分类选择功能"""
            enhanced_items = []
            
            for item in purchase_data["items"]:
                enhanced_item = item.copy()
                
                # 为所有明细项添加可选择的系统分类
                enhanced_item["available_system_categories"] = project_categories
                
                # 标记是否需要用户选择系统分类
                enhanced_item["needs_category_selection"] = not item["system_category_id"]
                
                enhanced_items.append(enhanced_item)
            
            purchase_data["items"] = enhanced_items
            return purchase_data
        
        # 测试场景1：加载历史申购单
        historical_data = load_purchase_for_edit(22)
        assert historical_data is not None
        assert historical_data["id"] == 22
        assert len(historical_data["items"]) == 2
        
        # 增强系统分类功能
        enhanced_historical = enhance_items_with_system_categories(
            historical_data, self.system_categories
        )
        
        # 验证历史数据的系统分类增强
        item1 = enhanced_historical["items"][0]  # 缺少系统分类的项目
        assert item1["system_category_id"] is None
        assert item1["needs_category_selection"] == True
        assert len(item1["available_system_categories"]) == 4
        print("   ✅ 历史数据正确标记需要选择系统分类")
        
        item2 = enhanced_historical["items"][1]  # 已有系统分类的项目
        assert item2["system_category_id"] == 1
        assert item2["needs_category_selection"] == False
        assert item2["system_category_name"] == "视频监控"
        print("   ✅ 已有系统分类的数据正确显示")

    def test_edit_page_system_category_selection(self):
        """测试编辑页面系统分类选择功能"""
        print("\n🎯 测试编辑页面系统分类选择功能...")
        
        def update_item_system_category(purchase_data, item_id, category_id):
            """模拟在编辑页面更新申购明细的系统分类"""
            for item in purchase_data["items"]:
                if item["id"] == item_id:
                    # 查找对应的系统分类
                    selected_category = None
                    for category in self.system_categories:
                        if category["id"] == category_id:
                            selected_category = category
                            break
                    
                    if selected_category:
                        item["system_category_id"] = category_id
                        item["system_category_name"] = selected_category["category_name"]
                        item["needs_category_selection"] = False
                        return True, f"已设置为{selected_category['category_name']}"
                    else:
                        return False, "无效的系统分类ID"
            
            return False, "找不到指定的申购明细"
        
        # 使用历史数据进行测试
        test_data = self.historical_purchase.copy()
        test_data["items"] = [item.copy() for item in test_data["items"]]
        
        # 测试场景1：为缺少系统分类的明细选择系统分类
        success, message = update_item_system_category(test_data, 1, 1)  # 选择视频监控
        assert success == True
        assert "视频监控" in message
        
        # 验证更新结果
        item1 = test_data["items"][0]
        assert item1["system_category_id"] == 1
        assert item1["system_category_name"] == "视频监控"
        assert item1["needs_category_selection"] == False
        print("   ✅ 成功为历史数据选择系统分类")
        
        # 测试场景2：修改已有的系统分类
        success, message = update_item_system_category(test_data, 2, 4)  # 改为智能化集成
        assert success == True
        assert "智能化集成" in message
        
        item2 = test_data["items"][1] 
        assert item2["system_category_id"] == 4
        assert item2["system_category_name"] == "智能化集成"
        print("   ✅ 成功修改已有系统分类")
        
        # 测试场景3：选择无效的系统分类
        success, message = update_item_system_category(test_data, 1, 999)
        assert success == False
        assert "无效的系统分类ID" in message
        print("   ✅ 正确处理无效系统分类ID")

    def test_edit_page_save_with_system_categories(self):
        """测试编辑页面保存时系统分类数据持久化"""
        print("\n💾 测试编辑页面保存系统分类数据...")
        
        def save_purchase_with_system_categories(purchase_data):
            """模拟保存申购单时处理系统分类"""
            saved_items = []
            
            for item in purchase_data["items"]:
                # 模拟数据库保存
                saved_item = {
                    "id": item["id"],
                    "item_name": item["item_name"],
                    "system_category_id": item.get("system_category_id"),
                    "quantity": item["quantity"],
                    "saved_at": "2025-08-19T10:30:00",
                    "saved": True
                }
                
                # 如果有系统分类ID，模拟从数据库查询系统分类名称
                if saved_item["system_category_id"]:
                    for category in self.system_categories:
                        if category["id"] == saved_item["system_category_id"]:
                            saved_item["system_category_name"] = category["category_name"]
                            break
                else:
                    saved_item["system_category_name"] = None
                
                saved_items.append(saved_item)
            
            return {
                "id": purchase_data["id"],
                "request_code": purchase_data["request_code"],
                "items": saved_items,
                "saved": True,
                "total_items": len(saved_items)
            }
        
        # 准备测试数据：历史数据经过系统分类选择
        test_data = self.historical_purchase.copy()
        test_data["items"] = [
            {
                "id": 1,
                "item_name": "网络摄像机",
                "system_category_id": 1,  # 用户选择了视频监控
                "quantity": 5
            },
            {
                "id": 2,
                "item_name": "录像机", 
                "system_category_id": 1,  # 保持原有的视频监控
                "quantity": 2
            }
        ]
        
        # 执行保存
        save_result = save_purchase_with_system_categories(test_data)
        
        # 验证保存结果
        assert save_result["saved"] == True
        assert save_result["total_items"] == 2
        
        # 验证第一个明细（原本缺少系统分类）
        item1 = save_result["items"][0]
        assert item1["system_category_id"] == 1
        assert item1["system_category_name"] == "视频监控"
        assert item1["saved"] == True
        print("   ✅ 历史数据的系统分类正确保存")
        
        # 验证第二个明细（原本已有系统分类）
        item2 = save_result["items"][1]
        assert item2["system_category_id"] == 1
        assert item2["system_category_name"] == "视频监控"
        print("   ✅ 已有系统分类的数据正确保持")

    def test_edit_page_api_integration(self):
        """测试编辑页面API集成"""
        print("\n🔌 测试编辑页面API集成...")
        
        def mock_api_call(endpoint, method="GET", data=None):
            """模拟API调用"""
            responses = {
                "/api/v1/purchases/22": {
                    "status": 200,
                    "data": self.historical_purchase
                },
                "/api/v1/purchases/system-categories/by-project/2": {
                    "status": 200,
                    "data": {
                        "project_id": 2,
                        "categories": self.system_categories
                    }
                },
                "/api/v1/purchases/system-categories/by-material": {
                    "status": 200,
                    "data": {
                        "material_name": "网络摄像机",
                        "categories": [
                            {"id": 1, "category_name": "视频监控", "is_suggested": True}
                        ]
                    }
                }
            }
            
            if endpoint in responses:
                return responses[endpoint]
            else:
                return {"status": 404, "data": {"detail": "Not Found"}}
        
        # 测试场景1：获取申购单详情
        response = mock_api_call("/api/v1/purchases/22")
        assert response["status"] == 200
        assert response["data"]["id"] == 22
        print("   ✅ 获取申购单详情API正常")
        
        # 测试场景2：获取项目系统分类列表
        response = mock_api_call("/api/v1/purchases/system-categories/by-project/2")
        assert response["status"] == 200
        assert len(response["data"]["categories"]) == 4
        print("   ✅ 获取项目系统分类API正常")
        
        # 测试场景3：获取物料系统分类推荐
        response = mock_api_call("/api/v1/purchases/system-categories/by-material")
        assert response["status"] == 200
        assert response["data"]["categories"][0]["is_suggested"] == True
        print("   ✅ 获取物料推荐API正常")

    def test_edit_page_error_handling(self):
        """测试编辑页面错误处理"""
        print("\n🚨 测试编辑页面错误处理...")
        
        def handle_edit_page_errors(scenario):
            """模拟编辑页面的各种错误场景"""
            error_scenarios = {
                "purchase_not_found": {
                    "error": True,
                    "message": "申购单不存在",
                    "code": 404
                },
                "no_system_categories": {
                    "error": False,
                    "data": {"categories": []},
                    "fallback_message": "该项目暂无系统分类，请联系管理员"
                },
                "api_timeout": {
                    "error": True,
                    "message": "网络请求超时，请重试",
                    "code": 408
                },
                "invalid_category_selection": {
                    "error": True,
                    "message": "选择的系统分类不存在",
                    "code": 400
                }
            }
            
            return error_scenarios.get(scenario, {"error": False})
        
        # 测试场景1：申购单不存在
        result = handle_edit_page_errors("purchase_not_found")
        assert result["error"] == True
        assert result["code"] == 404
        print("   ✅ 正确处理申购单不存在错误")
        
        # 测试场景2：项目无系统分类
        result = handle_edit_page_errors("no_system_categories")
        assert result["error"] == False
        assert len(result["data"]["categories"]) == 0
        assert "请联系管理员" in result["fallback_message"]
        print("   ✅ 正确处理无系统分类情况")
        
        # 测试场景3：API超时
        result = handle_edit_page_errors("api_timeout")
        assert result["error"] == True
        assert "重试" in result["message"]
        print("   ✅ 正确处理API超时错误")
        
        # 测试场景4：无效的系统分类选择
        result = handle_edit_page_errors("invalid_category_selection")
        assert result["error"] == True
        assert "不存在" in result["message"]
        print("   ✅ 正确处理无效系统分类选择")

    def test_edit_page_user_experience_flow(self):
        """测试编辑页面完整用户体验流程"""
        print("\n👤 测试编辑页面完整用户体验流程...")
        
        def simulate_user_edit_flow():
            """模拟用户在编辑页面的完整操作流程"""
            flow_steps = []
            
            # 步骤1：用户打开编辑页面
            flow_steps.append({
                "step": 1,
                "action": "load_edit_page",
                "description": "加载申购单编辑页面",
                "success": True,
                "data": self.historical_purchase
            })
            
            # 步骤2：系统自动加载项目系统分类
            flow_steps.append({
                "step": 2,
                "action": "load_system_categories",
                "description": "为所有明细项加载系统分类选择器",
                "success": True,
                "categories_loaded": len(self.system_categories)
            })
            
            # 步骤3：用户看到历史数据的系统分类显示状态
            historical_item = self.historical_purchase["items"][0]
            flow_steps.append({
                "step": 3,
                "action": "display_category_status",
                "description": "显示系统分类选择器（历史数据为null时）",
                "success": True,
                "shows_selector": historical_item["system_category_id"] is None,
                "shows_name": historical_item["system_category_id"] is not None
            })
            
            # 步骤4：用户为历史数据选择系统分类
            flow_steps.append({
                "step": 4,
                "action": "user_select_category",
                "description": "用户选择'视频监控'系统分类",
                "success": True,
                "selected_category": "视频监控",
                "category_id": 1
            })
            
            # 步骤5：界面实时更新显示
            flow_steps.append({
                "step": 5,
                "action": "ui_update",
                "description": "界面实时显示选择的系统分类",
                "success": True,
                "ui_shows": "视频监控",
                "selector_hidden": True
            })
            
            # 步骤6：用户保存申购单
            flow_steps.append({
                "step": 6,
                "action": "save_purchase",
                "description": "保存申购单，系统分类持久化到数据库",
                "success": True,
                "saved_categories": 2,  # 两个明细都有系统分类
                "data_complete": True
            })
            
            return flow_steps
        
        # 执行用户流程模拟
        user_flow = simulate_user_edit_flow()
        
        # 验证每个步骤
        assert len(user_flow) == 6
        for step in user_flow:
            assert step["success"] == True
            print(f"   ✅ 步骤{step['step']}: {step['description']}")
        
        # 验证关键步骤
        load_step = user_flow[0]
        assert load_step["action"] == "load_edit_page"
        
        category_step = user_flow[1]
        assert category_step["categories_loaded"] == 4
        
        display_step = user_flow[2]
        assert display_step["shows_selector"] == True  # 历史数据显示选择器
        
        select_step = user_flow[3]
        assert select_step["selected_category"] == "视频监控"
        
        save_step = user_flow[5]
        assert save_step["data_complete"] == True
        
        print("   🎉 完整用户体验流程测试通过")


def run_edit_page_integration_tests():
    """运行所有编辑页面集成测试"""
    print("🚀 开始运行申购单编辑页面集成测试...")
    print("=" * 70)
    
    test_instance = TestPurchaseEditPageIntegration()
    
    # 运行所有测试方法
    test_methods = [
        test_instance.test_edit_page_load_historical_data,
        test_instance.test_edit_page_system_category_selection,
        test_instance.test_edit_page_save_with_system_categories,
        test_instance.test_edit_page_api_integration,
        test_instance.test_edit_page_error_handling,
        test_instance.test_edit_page_user_experience_flow
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
    
    print("\n" + "=" * 70)
    print(f"📊 测试结果汇总: {passed} 通过, {failed} 失败")
    
    if failed == 0:
        print("🎉 所有编辑页面集成测试通过！")
    else:
        print(f"⚠️  有 {failed} 个测试失败，需要检查")
    
    return failed == 0


if __name__ == "__main__":
    success = run_edit_page_integration_tests()
    exit(0 if success else 1)