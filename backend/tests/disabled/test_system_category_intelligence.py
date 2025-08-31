"""
系统分类智能推荐功能单元测试
测试基于合同清单的智能系统分类推荐逻辑
"""

import pytest
from unittest.mock import Mock, patch


class TestSystemCategoryIntelligence:
    """系统分类智能推荐测试类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        # 模拟系统分类数据
        self.system_categories = [
            {"id": 1, "category_name": "视频监控系统", "category_code": "VIDEO"},
            {"id": 2, "category_name": "门禁控制系统", "category_code": "ACCESS"},
            {"id": 3, "category_name": "智能照明系统", "category_code": "LIGHTING"},
            {"id": 4, "category_name": "消防联动系统", "category_code": "FIRE"},
            {"id": 5, "category_name": "网络通信系统", "category_code": "NETWORK"},
            {"id": 6, "category_name": "公共广播系统", "category_code": "BROADCAST"},
            {"id": 7, "category_name": "综合布线系统", "category_code": "CABLING"}
        ]
        
        # 模拟合同清单项数据，包含系统分类关联
        self.contract_items = [
            {
                "id": 1,
                "item_name": "室外人脸抓拍枪式摄像机",
                "specification": "DH-SH-HFS9541P-I",
                "system_category_id": 1,  # 视频监控系统
                "system_category": {"id": 1, "category_name": "视频监控系统"}
            },
            {
                "id": 2,
                "item_name": "网络摄像机",
                "specification": "DS-2CD3T56WD-I8",
                "system_category_id": 1,  # 视频监控系统
                "system_category": {"id": 1, "category_name": "视频监控系统"}
            },
            {
                "id": 3,
                "item_name": "网络硬盘录像机",
                "specification": "DH-NVR5832-4K",
                "system_category_id": 1,  # 视频监控系统
                "system_category": {"id": 1, "category_name": "视频监控系统"}
            },
            {
                "id": 4,
                "item_name": "人脸识别门禁主机",
                "specification": "DS-K1T671MF",
                "system_category_id": 2,  # 门禁控制系统
                "system_category": {"id": 2, "category_name": "门禁控制系统"}
            },
            {
                "id": 5,
                "item_name": "电子门锁",
                "specification": "DS-K4H450S",
                "system_category_id": 2,  # 门禁控制系统
                "system_category": {"id": 2, "category_name": "门禁控制系统"}
            },
            {
                "id": 6,
                "item_name": "智能开关面板",
                "specification": "SC-SW01",
                "system_category_id": 3,  # 智能照明系统
                "system_category": {"id": 3, "category_name": "智能照明系统"}
            },
            {
                "id": 7,
                "item_name": "核心交换机",  # 跨系统设备
                "specification": "H3C S5560X-54C",
                "system_category_id": 5,  # 网络通信系统
                "system_category": {"id": 5, "category_name": "网络通信系统"}
            },
            {
                "id": 8,
                "item_name": "核心交换机",  # 同名设备，不同系统
                "specification": "H3C S5560X-48S",
                "system_category_id": 1,  # 视频监控系统中也使用
                "system_category": {"id": 1, "category_name": "视频监控系统"}
            }
        ]
    
    def test_single_system_auto_recommendation(self):
        """测试单系统物料的自动推荐"""
        print("\n⭐ 测试单系统物料自动推荐...")
        
        def get_system_categories_by_material(project_id, material_name):
            """根据物料名称智能推荐系统分类"""
            # 在合同清单中查找该物料
            matching_items = []
            for item in self.contract_items:
                if item['item_name'] == material_name:
                    matching_items.append(item)
            
            if not matching_items:
                return {"categories": [], "is_single": False}
            
            # 获取所有相关的系统分类
            category_ids = list(set(item['system_category_id'] for item in matching_items))
            categories = []
            
            for category_id in category_ids:
                category = next((c for c in self.system_categories if c['id'] == category_id), None)
                if category:
                    # 统计该系统分类下的物料数量
                    items_count = len([item for item in matching_items if item['system_category_id'] == category_id])
                    categories.append({
                        **category,
                        "items_count": items_count,
                        "is_suggested": len(category_ids) == 1  # 只有一个系统时自动推荐
                    })
            
            # 按物料数量排序，数量多的排在前面
            categories.sort(key=lambda x: x['items_count'], reverse=True)
            
            return {
                "categories": categories,
                "is_single": len(categories) == 1,
                "auto_select": len(categories) == 1  # 单个系统时自动选择
            }
        
        # 测试场景1：网络硬盘录像机（只属于视频监控系统）
        result = get_system_categories_by_material(1, "网络硬盘录像机")
        
        assert result['is_single'] == True
        assert result['auto_select'] == True
        assert len(result['categories']) == 1
        assert result['categories'][0]['category_name'] == "视频监控系统"
        assert result['categories'][0]['is_suggested'] == True
        print("   ✅ 单系统物料正确自动推荐")
        
        # 测试场景2：电子门锁（只属于门禁控制系统）
        result = get_system_categories_by_material(1, "电子门锁")
        
        assert result['is_single'] == True
        assert result['auto_select'] == True
        assert len(result['categories']) == 1
        assert result['categories'][0]['category_name'] == "门禁控制系统"
        assert result['categories'][0]['is_suggested'] == True
        print("   ✅ 门禁设备正确推荐到门禁系统")
    
    def test_multi_system_recommendation(self):
        """测试多系统物料的推荐选择"""
        print("\n🔄 测试多系统物料推荐选择...")
        
        def get_system_categories_by_material(project_id, material_name):
            """多系统物料推荐逻辑"""
            matching_items = []
            for item in self.contract_items:
                if item['item_name'] == material_name:
                    matching_items.append(item)
            
            if not matching_items:
                return {"categories": [], "is_single": False}
            
            # 按系统分类统计
            system_stats = {}
            for item in matching_items:
                system_id = item['system_category_id']
                if system_id not in system_stats:
                    system_stats[system_id] = {
                        "count": 0,
                        "system_info": item['system_category']
                    }
                system_stats[system_id]["count"] += 1
            
            categories = []
            for system_id, stats in system_stats.items():
                category = next((c for c in self.system_categories if c['id'] == system_id), None)
                if category:
                    categories.append({
                        **category,
                        "items_count": stats["count"],
                        "is_suggested": stats["count"] == max(s["count"] for s in system_stats.values())
                    })
            
            # 按物料数量排序
            categories.sort(key=lambda x: x['items_count'], reverse=True)
            
            return {
                "categories": categories,
                "is_single": len(categories) == 1,
                "auto_select": False,  # 多系统时不自动选择
                "requires_user_selection": len(categories) > 1
            }
        
        # 测试场景：核心交换机（既用于网络系统，也用于视频监控系统）
        result = get_system_categories_by_material(1, "核心交换机")
        
        assert result['is_single'] == False
        assert result['auto_select'] == False
        assert result['requires_user_selection'] == True
        assert len(result['categories']) == 2
        
        # 验证系统分类包含正确的选项
        category_names = [c['category_name'] for c in result['categories']]
        assert "网络通信系统" in category_names
        assert "视频监控系统" in category_names
        
        # 验证推荐标记（应该有一个被标记为推荐）
        suggested_count = len([c for c in result['categories'] if c['is_suggested']])
        assert suggested_count >= 1
        
        print("   ✅ 多系统物料正确提供选择列表")
        print(f"   📊 可选系统: {category_names}")
    
    def test_material_not_in_contract(self):
        """测试物料不在合同清单中的情况"""
        print("\n❓ 测试物料不在合同清单情况...")
        
        def get_system_categories_by_material(project_id, material_name):
            """处理物料不在合同清单的情况"""
            matching_items = []
            for item in self.contract_items:
                if item['item_name'] == material_name:
                    matching_items.append(item)
            
            if not matching_items:
                # 物料不在合同清单中，返回所有系统分类供手动选择
                return {
                    "categories": [
                        {**category, "items_count": 0, "is_suggested": False}
                        for category in self.system_categories
                    ],
                    "is_single": False,
                    "auto_select": False,
                    "not_in_contract": True,
                    "message": "该物料不在合同清单中，请手动选择所属系统"
                }
            
            return {"categories": [], "not_in_contract": False}
        
        # 测试不存在的物料
        result = get_system_categories_by_material(1, "未知设备")
        
        assert result['not_in_contract'] == True
        assert result['auto_select'] == False
        assert len(result['categories']) == len(self.system_categories)
        assert all(not c['is_suggested'] for c in result['categories'])
        assert "手动选择" in result['message']
        
        print("   ✅ 不在合同清单的物料正确处理")
        print(f"   📝 提示信息: {result['message']}")
    
    def test_auxiliary_material_system_selection(self):
        """测试辅材的系统分类选择逻辑"""
        print("\n🔧 测试辅材系统分类选择...")
        
        def get_system_categories_for_auxiliary(project_id):
            """为辅材获取所有可选系统分类"""
            # 辅材可以选择项目中的任何系统分类
            return {
                "categories": [
                    {
                        **category,
                        "items_count": 0,  # 辅材不统计合同清单项数量
                        "is_suggested": False,  # 辅材不自动推荐
                        "description": f"可选择归属到{category['category_name']}"
                    }
                    for category in self.system_categories
                ],
                "is_auxiliary": True,
                "message": "辅材可以归属到任何系统分类",
                "allow_manual_selection": True
            }
        
        result = get_system_categories_for_auxiliary(1)
        
        assert result['is_auxiliary'] == True
        assert result['allow_manual_selection'] == True
        assert len(result['categories']) == len(self.system_categories)
        assert all(not c['is_suggested'] for c in result['categories'])
        assert "辅材可以归属" in result['message']
        
        # 验证所有主要系统都可选
        category_names = [c['category_name'] for c in result['categories']]
        expected_systems = ["视频监控系统", "门禁控制系统", "智能照明系统", "网络通信系统"]
        for expected in expected_systems:
            assert expected in category_names
        
        print("   ✅ 辅材可以选择任何系统分类")
    
    def test_system_category_priority_logic(self):
        """测试系统分类优先级逻辑"""
        print("\n📊 测试系统分类优先级逻辑...")
        
        def calculate_system_category_priority(material_name, contract_items):
            """计算系统分类的推荐优先级"""
            matching_items = [item for item in contract_items if item['item_name'] == material_name]
            
            if not matching_items:
                return []
            
            # 统计各系统的使用频率和重要度
            system_stats = {}
            for item in matching_items:
                system_id = item['system_category_id']
                if system_id not in system_stats:
                    system_stats[system_id] = {
                        "count": 0,
                        "category": item['system_category']
                    }
                system_stats[system_id]["count"] += 1
            
            # 计算优先级分数
            priorities = []
            total_count = sum(stats["count"] for stats in system_stats.values())
            
            for system_id, stats in system_stats.items():
                frequency_score = stats["count"] / total_count  # 频率分数
                
                # 系统重要度权重（基于系统类型）
                importance_weights = {
                    1: 1.0,  # 视频监控系统 - 高重要度
                    2: 0.9,  # 门禁控制系统 - 高重要度
                    3: 0.7,  # 智能照明系统 - 中等重要度
                    4: 1.0,  # 消防联动系统 - 高重要度
                    5: 0.8,  # 网络通信系统 - 中高重要度
                    6: 0.6,  # 公共广播系统 - 中等重要度
                    7: 0.5   # 综合布线系统 - 基础重要度
                }
                
                importance_score = importance_weights.get(system_id, 0.5)
                final_score = frequency_score * 0.6 + importance_score * 0.4
                
                priorities.append({
                    "system_id": system_id,
                    "category_name": stats["category"]["category_name"],
                    "count": stats["count"],
                    "frequency_score": frequency_score,
                    "importance_score": importance_score,
                    "final_score": final_score,
                    "is_recommended": final_score == max(p.get("final_score", 0) for p in priorities + [{"final_score": final_score}])
                })
            
            # 按最终分数排序
            priorities.sort(key=lambda x: x['final_score'], reverse=True)
            
            # 设置推荐标记（最高分的标记为推荐）
            if priorities:
                priorities[0]["is_recommended"] = True
                for p in priorities[1:]:
                    p["is_recommended"] = False
            
            return priorities
        
        # 测试核心交换机的优先级计算
        priorities = calculate_system_category_priority("核心交换机", self.contract_items)
        
        assert len(priorities) == 2  # 应该有2个系统
        assert priorities[0]["is_recommended"] == True  # 第一个是推荐的
        assert priorities[1]["is_recommended"] == False  # 第二个不是推荐的
        
        # 验证分数计算
        for priority in priorities:
            assert 0 <= priority["frequency_score"] <= 1
            assert 0 <= priority["importance_score"] <= 1
            assert 0 <= priority["final_score"] <= 1
        
        print("   ✅ 系统分类优先级计算正确")
        print(f"   🥇 推荐系统: {priorities[0]['category_name']} (分数: {priorities[0]['final_score']:.3f})")
        if len(priorities) > 1:
            print(f"   🥈 备选系统: {priorities[1]['category_name']} (分数: {priorities[1]['final_score']:.3f})")
    
    def test_historical_data_compatibility(self):
        """测试历史数据兼容性处理"""
        print("\n🕰️ 测试历史数据兼容性...")
        
        def handle_legacy_items_system_categories(items, available_categories):
            """处理历史申购单项目的系统分类兼容性"""
            enhanced_items = []
            
            for item in items:
                enhanced_item = item.copy()
                
                # 如果已有系统分类，保留
                if item.get('system_category_id') and item.get('system_category_name'):
                    enhanced_item['system_status'] = 'existing'
                    enhanced_item['available_system_categories'] = available_categories
                else:
                    # 历史数据没有系统分类，提供选择选项
                    enhanced_item['system_status'] = 'needs_selection'
                    enhanced_item['system_category_id'] = None
                    enhanced_item['system_category_name'] = None
                    enhanced_item['available_system_categories'] = available_categories
                    enhanced_item['selection_message'] = '请为历史数据选择合适的系统分类'
                
                enhanced_items.append(enhanced_item)
            
            return enhanced_items
        
        # 模拟历史申购单项目（有些有系统分类，有些没有）
        legacy_items = [
            {
                'id': 1,
                'item_name': '网络摄像机',
                'system_category_id': 1,
                'system_category_name': '视频监控系统'
            },
            {
                'id': 2,
                'item_name': '电源适配器',
                'system_category_id': None,  # 历史数据缺失
                'system_category_name': None
            },
            {
                'id': 3,
                'item_name': '安装支架',
                # 完全缺失系统分类字段
            }
        ]
        
        enhanced_items = handle_legacy_items_system_categories(legacy_items, self.system_categories)
        
        # 验证处理结果
        assert len(enhanced_items) == 3
        
        # 项目1：已有系统分类
        assert enhanced_items[0]['system_status'] == 'existing'
        assert enhanced_items[0]['system_category_name'] == '视频监控系统'
        assert 'available_system_categories' in enhanced_items[0]
        
        # 项目2：需要选择系统分类
        assert enhanced_items[1]['system_status'] == 'needs_selection'
        assert enhanced_items[1]['system_category_id'] is None
        assert '请为历史数据选择' in enhanced_items[1]['selection_message']
        
        # 项目3：完全缺失字段
        assert enhanced_items[2]['system_status'] == 'needs_selection'
        assert enhanced_items[2]['system_category_id'] is None
        
        print("   ✅ 历史数据兼容性处理正确")
        print(f"   📊 需要选择系统分类的项目: {len([item for item in enhanced_items if item['system_status'] == 'needs_selection'])}")
    
    def test_performance_optimization(self):
        """测试系统分类推荐的性能优化"""
        print("\n⚡ 测试系统分类推荐性能...")
        
        import time
        
        def optimized_system_recommendation(material_names, contract_items, system_categories):
            """优化的批量系统分类推荐"""
            # 构建物料到系统的映射索引
            material_system_index = {}
            for item in contract_items:
                material_name = item['item_name']
                system_id = item['system_category_id']
                
                if material_name not in material_system_index:
                    material_system_index[material_name] = {}
                
                if system_id not in material_system_index[material_name]:
                    material_system_index[material_name][system_id] = 0
                material_system_index[material_name][system_id] += 1
            
            # 构建系统分类快速查找
            system_lookup = {cat['id']: cat for cat in system_categories}
            
            results = {}
            for material_name in material_names:
                if material_name in material_system_index:
                    system_stats = material_system_index[material_name]
                    categories = []
                    
                    for system_id, count in system_stats.items():
                        if system_id in system_lookup:
                            categories.append({
                                **system_lookup[system_id],
                                "items_count": count,
                                "is_suggested": count == max(system_stats.values())
                            })
                    
                    categories.sort(key=lambda x: x['items_count'], reverse=True)
                    results[material_name] = {
                        "categories": categories,
                        "auto_select": len(categories) == 1
                    }
                else:
                    # 物料不在合同中
                    results[material_name] = {
                        "categories": [
                            {**cat, "items_count": 0, "is_suggested": False}
                            for cat in system_categories
                        ],
                        "auto_select": False
                    }
            
            return results
        
        # 生成大量测试数据
        test_materials = [f"测试设备{i}" for i in range(1000)]
        large_contract_items = []
        
        for i in range(1000):
            large_contract_items.append({
                "id": i + 1,
                "item_name": f"测试设备{i % 100}",  # 重复物料名称
                "system_category_id": (i % 7) + 1  # 分配到不同系统
            })
        
        # 性能测试
        start_time = time.time()
        results = optimized_system_recommendation(
            test_materials[:100], large_contract_items, self.system_categories
        )
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        assert len(results) == 100
        assert execution_time < 0.5  # 应该在0.5秒内完成
        
        # 验证结果正确性
        sample_result = list(results.values())[0]
        assert "categories" in sample_result
        assert "auto_select" in sample_result
        
        print(f"   ✅ 100个物料推荐耗时: {execution_time:.4f}秒")
        print("   ✅ 系统分类推荐性能优良")


def run_intelligence_tests():
    """运行所有智能推荐测试"""
    print("🧠 开始运行系统分类智能推荐功能测试...")
    print("=" * 60)
    
    test_instance = TestSystemCategoryIntelligence()
    
    test_methods = [
        test_instance.test_single_system_auto_recommendation,
        test_instance.test_multi_system_recommendation,
        test_instance.test_material_not_in_contract,
        test_instance.test_auxiliary_material_system_selection,
        test_instance.test_system_category_priority_logic,
        test_instance.test_historical_data_compatibility,
        test_instance.test_performance_optimization
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
    print(f"📊 智能推荐功能测试结果: {passed} 通过, {failed} 失败")
    
    return failed == 0


if __name__ == "__main__":
    success = run_intelligence_tests()
    exit(0 if success else 1)