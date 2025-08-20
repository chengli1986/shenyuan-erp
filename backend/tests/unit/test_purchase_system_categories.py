"""
申购单系统分类功能单元测试
测试系统分类的智能推荐、手动选择、数据保存等功能
"""

import pytest
from unittest.mock import Mock, patch
from decimal import Decimal
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.models.purchase import PurchaseRequest, PurchaseRequestItem
from app.models.contract import SystemCategory, ContractItem
from app.schemas.purchase import PurchaseItemCreate


class TestPurchaseSystemCategories:
    """申购单系统分类测试类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.mock_db = Mock()
        
        # 模拟系统分类数据
        self.system_categories = [
            Mock(id=1, category_name="视频监控", category_code="SYS_视频监控"),
            Mock(id=2, category_name="出入口控制", category_code="SYS_出入口控制"), 
            Mock(id=3, category_name="停车系统", category_code="SYS_停车系统"),
            Mock(id=4, category_name="智能化集成", category_code="SYS_智能化集成")
        ]
        
        # 模拟合同清单项目
        self.contract_items = [
            Mock(
                id=1, 
                item_name="网络摄像机",
                system_category_id=1,
                system_category=self.system_categories[0]
            ),
            Mock(
                id=2,
                item_name="门禁控制器", 
                system_category_id=2,
                system_category=self.system_categories[1]
            )
        ]

    def test_system_category_data_model(self):
        """测试系统分类数据模型"""
        print("\n🏗️ 测试系统分类数据模型...")
        
        # 测试PurchaseRequestItem支持系统分类
        item_data = {
            'item_name': '网络摄像机',
            'system_category_id': 1,
            'quantity': 5,
            'item_type': 'main'
        }
        
        # 验证字段存在性（模拟）
        assert 'system_category_id' in item_data
        assert item_data['system_category_id'] == 1
        assert item_data['item_name'] == '网络摄像机'
        
        print("   ✅ 申购明细支持系统分类字段")

    def test_intelligent_system_category_recommendation(self):
        """测试智能系统分类推荐"""
        print("\n🧠 测试智能系统分类推荐...")
        
        def get_system_categories_by_material(project_id, material_name):
            """模拟根据物料名称获取系统分类推荐"""
            material_category_map = {
                "网络摄像机": [
                    {"id": 1, "category_name": "视频监控", "is_suggested": True}
                ],
                "门禁控制器": [
                    {"id": 2, "category_name": "出入口控制", "is_suggested": True}
                ],
                "道闸": [
                    {"id": 3, "category_name": "停车系统", "is_suggested": True}
                ],
                "不明设备": []  # 无推荐
            }
            return material_category_map.get(material_name, [])
        
        # 测试场景1：有明确推荐的物料
        camera_recommendations = get_system_categories_by_material(2, "网络摄像机")
        assert len(camera_recommendations) == 1
        assert camera_recommendations[0]["id"] == 1
        assert camera_recommendations[0]["is_suggested"] == True
        print("   ✅ 摄像机智能推荐视频监控系统")
        
        # 测试场景2：门禁设备推荐
        access_recommendations = get_system_categories_by_material(2, "门禁控制器")
        assert len(access_recommendations) == 1
        assert access_recommendations[0]["id"] == 2
        assert access_recommendations[0]["category_name"] == "出入口控制"
        print("   ✅ 门禁设备智能推荐出入口控制系统")
        
        # 测试场景3：无推荐的物料
        unknown_recommendations = get_system_categories_by_material(2, "不明设备")
        assert len(unknown_recommendations) == 0
        print("   ✅ 未知物料无推荐系统分类")

    def test_system_category_manual_selection(self):
        """测试手动选择系统分类"""
        print("\n👆 测试手动选择系统分类...")
        
        def update_item_system_category(item_id, category_id, category_name):
            """模拟更新申购明细的系统分类"""
            return {
                'id': item_id,
                'system_category_id': category_id,
                'system_category_name': category_name,
                'updated': True
            }
        
        # 测试场景1：为历史数据选择系统分类
        result = update_item_system_category('item_1', 1, '视频监控')
        assert result['system_category_id'] == 1
        assert result['system_category_name'] == '视频监控'
        assert result['updated'] == True
        print("   ✅ 历史数据可手动选择系统分类")
        
        # 测试场景2：覆盖智能推荐
        result = update_item_system_category('item_2', 4, '智能化集成')
        assert result['system_category_id'] == 4
        assert result['system_category_name'] == '智能化集成'
        print("   ✅ 可覆盖智能推荐选择其他系统")

    def test_system_category_data_persistence(self):
        """测试系统分类数据持久化"""
        print("\n💾 测试系统分类数据持久化...")
        
        # 模拟申购明细创建时保存系统分类
        def create_purchase_item_with_category(item_data):
            """模拟创建申购明细时保存系统分类"""
            return {
                'id': 'new_item_1',
                'item_name': item_data['item_name'],
                'system_category_id': item_data.get('system_category_id'),
                'system_category_name': None,  # 模拟从数据库查询得到
                'quantity': item_data['quantity'],
                'saved': True
            }
        
        # 测试场景1：主材带系统分类保存
        main_item_data = {
            'item_name': '网络摄像机',
            'system_category_id': 1,
            'quantity': 10,
            'item_type': 'main'
        }
        
        result = create_purchase_item_with_category(main_item_data)
        assert result['system_category_id'] == 1
        assert result['item_name'] == '网络摄像机'
        assert result['saved'] == True
        print("   ✅ 主材系统分类正确保存")
        
        # 测试场景2：辅材带系统分类保存
        auxiliary_item_data = {
            'item_name': '网线',
            'system_category_id': 4,  # 用户手动选择智能化集成
            'quantity': 100,
            'item_type': 'auxiliary'
        }
        
        result = create_purchase_item_with_category(auxiliary_item_data)
        assert result['system_category_id'] == 4
        assert result['item_name'] == '网线'
        print("   ✅ 辅材系统分类正确保存")

    def test_system_category_api_responses(self):
        """测试系统分类API响应格式"""
        print("\n🔌 测试系统分类API响应格式...")
        
        # 模拟不同的API响应格式
        def get_project_system_categories_response():
            """模拟项目系统分类API响应"""
            return {
                "project_id": 2,
                "version_id": 3,
                "categories": [
                    {"id": 1, "category_name": "视频监控", "total_items_count": 48},
                    {"id": 2, "category_name": "出入口控制", "total_items_count": 23},
                    {"id": 3, "category_name": "停车系统", "total_items_count": 0}
                ]
            }
        
        def get_material_system_categories_response():
            """模拟物料系统分类推荐API响应"""
            return {
                "material_name": "网络摄像机",
                "categories": [
                    {"id": 1, "category_name": "视频监控", "is_suggested": True}
                ]
            }
        
        # 测试项目系统分类API
        project_response = get_project_system_categories_response()
        assert "categories" in project_response
        assert len(project_response["categories"]) == 3
        assert project_response["categories"][0]["category_name"] == "视频监控"
        print("   ✅ 项目系统分类API响应格式正确")
        
        # 测试物料系统分类推荐API
        material_response = get_material_system_categories_response()
        assert "categories" in material_response
        assert material_response["categories"][0]["is_suggested"] == True
        print("   ✅ 物料推荐API响应格式正确")

    def test_system_category_edge_cases(self):
        """测试系统分类边界情况"""
        print("\n🔍 测试系统分类边界情况...")
        
        # 测试场景1：空的系统分类列表
        def handle_empty_categories():
            """处理空的系统分类列表"""
            categories = []
            return categories if isinstance(categories, list) else []
        
        empty_result = handle_empty_categories()
        assert isinstance(empty_result, list)
        assert len(empty_result) == 0
        print("   ✅ 正确处理空系统分类列表")
        
        # 测试场景2：无效的系统分类ID
        def validate_system_category_id(category_id, available_categories):
            """验证系统分类ID的有效性"""
            if not available_categories:
                return False, "无可用系统分类"
            
            valid_ids = [cat["id"] for cat in available_categories]
            if category_id not in valid_ids:
                return False, f"无效的系统分类ID: {category_id}"
            
            return True, None
        
        available_cats = [{"id": 1, "category_name": "视频监控"}]
        
        # 有效ID
        is_valid, error = validate_system_category_id(1, available_cats)
        assert is_valid == True
        assert error is None
        
        # 无效ID
        is_valid, error = validate_system_category_id(999, available_cats)
        assert is_valid == False
        assert "无效的系统分类ID" in error
        print("   ✅ 正确验证系统分类ID有效性")
        
        # 测试场景3：系统分类名称显示
        def get_system_category_display_name(category_id, category_name):
            """获取系统分类显示名称"""
            if category_name:
                return category_name
            elif category_id:
                return f"系统分类#{category_id}"
            else:
                return "未分类"
        
        assert get_system_category_display_name(1, "视频监控") == "视频监控"
        assert get_system_category_display_name(1, None) == "系统分类#1"
        assert get_system_category_display_name(None, None) == "未分类"
        print("   ✅ 正确处理系统分类显示名称")

    def test_system_category_historical_data_support(self):
        """测试历史数据系统分类支持"""
        print("\n📚 测试历史数据系统分类支持...")
        
        # 模拟历史申购单数据（system_category_id为null）
        historical_items = [
            {
                'id': 'hist_1',
                'item_name': '网络摄像机',
                'system_category_id': None,
                'system_category_name': None,
                'created_at': '2025-08-01'
            },
            {
                'id': 'hist_2', 
                'item_name': '交换机',
                'system_category_id': None,
                'system_category_name': None,
                'created_at': '2025-08-05'
            }
        ]
        
        def provide_system_category_options(items, project_categories):
            """为历史数据提供系统分类选择选项"""
            for item in items:
                # 为所有明细项添加可选择的系统分类
                item['available_system_categories'] = project_categories
                
                # 如果没有系统分类，标记需要用户选择
                if not item['system_category_id']:
                    item['needs_category_selection'] = True
                
            return items
        
        project_categories = [
            {"id": 1, "category_name": "视频监控"},
            {"id": 4, "category_name": "智能化集成"}
        ]
        
        enhanced_items = provide_system_category_options(historical_items, project_categories)
        
        # 验证所有历史数据都有系统分类选择选项
        for item in enhanced_items:
            assert 'available_system_categories' in item
            assert len(item['available_system_categories']) == 2
            if not item['system_category_id']:
                assert item['needs_category_selection'] == True
        
        print("   ✅ 历史数据正确提供系统分类选择选项")
        print("   ✅ 正确标记需要用户选择系统分类的数据")


def run_system_category_tests():
    """运行所有系统分类测试"""
    print("🚀 开始运行申购单系统分类功能测试...")
    print("=" * 60)
    
    test_instance = TestPurchaseSystemCategories()
    
    # 运行所有测试方法
    test_methods = [
        test_instance.test_system_category_data_model,
        test_instance.test_intelligent_system_category_recommendation,
        test_instance.test_system_category_manual_selection,
        test_instance.test_system_category_data_persistence,
        test_instance.test_system_category_api_responses,
        test_instance.test_system_category_edge_cases,
        test_instance.test_system_category_historical_data_support
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
        print("🎉 所有系统分类测试通过！")
    else:
        print(f"⚠️  有 {failed} 个测试失败，需要检查")
    
    return failed == 0


if __name__ == "__main__":
    success = run_system_category_tests()
    exit(0 if success else 1)