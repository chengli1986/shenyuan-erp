# 模拟前端的数据加载流程
import requests
import json

def test_frontend_data_flow():
    """测试前端数据加载流程"""
    
    base_url = "http://localhost:8000/api/v1"
    project_id = 3
    
    print("=== 模拟前端数据加载流程 ===\n")
    
    # 步骤1: 加载合同汇总信息 (ContractManagement组件)
    print("1. 加载合同汇总信息...")
    try:
        response = requests.get(f"{base_url}/contracts/projects/{project_id}/contract-summary")
        if response.status_code == 200:
            summary = response.json()
            print(f"   Summary loaded successfully")
            print(f"   - Total items: {summary['total_items']}")
            print(f"   - Current version exists: {bool(summary.get('current_version'))}")
            
            if summary.get('current_version'):
                current_version = summary['current_version']
                version_id = current_version['id']
                print(f"   - 版本ID: {version_id}")
                print(f"   - 版本号: {current_version['version_number']}")
                
                # 步骤2: 使用当前版本加载设备清单 (ContractItemList组件)
                print(f"\n2. 使用版本ID {version_id} 加载设备清单...")
                
                items_response = requests.get(
                    f"{base_url}/contracts/projects/{project_id}/versions/{version_id}/items",
                    params={"page": 1, "size": 5}
                )
                
                if items_response.status_code == 200:
                    items_data = items_response.json()
                    print(f"   ✅ 设备清单加载成功")
                    print(f"   - 返回数据类型: {type(items_data)}")
                    print(f"   - 包含键: {list(items_data.keys())}")
                    print(f"   - items数组长度: {len(items_data.get('items', []))}")
                    print(f"   - 总记录数: {items_data.get('total', 0)}")
                    
                    if items_data.get('items'):
                        first_item = items_data['items'][0]
                        print(f"   - 第一个设备: {first_item.get('item_name', 'N/A')}")
                        print(f"   - 设备字段: {list(first_item.keys())}")
                    else:
                        print("   ❌ items数组为空!")
                        
                else:
                    print(f"   ❌ 设备清单加载失败: {items_response.status_code}")
                    print(f"   错误: {items_response.text}")
                    
                # 步骤3: 尝试加载系统分类 (ContractItemList组件)
                print(f"\n3. 加载系统分类...")
                categories_response = requests.get(
                    f"{base_url}/contracts/projects/{project_id}/versions/{version_id}/categories"
                )
                
                if categories_response.status_code == 200:
                    categories_data = categories_response.json()
                    print(f"   ✅ 系统分类加载成功")
                    print(f"   - 分类数量: {len(categories_data)}")
                    if categories_data:
                        print(f"   - 第一个分类: {categories_data[0].get('category_name', 'N/A')}")
                else:
                    print(f"   ❌ 系统分类加载失败: {categories_response.status_code}")
                    print(f"   这不会影响设备清单显示")
                    
            else:
                print("   ❌ 没有当前版本，ContractItemList不会加载数据")
                
        else:
            print(f"   ❌ 汇总加载失败: {response.status_code}")
            print(f"   错误: {response.text}")
            
    except Exception as e:
        print(f"   ❌ 请求失败: {str(e)}")
    
    print("\n=== 结论 ===")
    print("如果以上所有步骤都成功，那么前端应该能够显示设备数据")
    print("如果前端仍显示'暂无数据'，问题可能在于:")
    print("1. 前端状态管理或渲染逻辑")
    print("2. 前端错误处理")
    print("3. 浏览器控制台可能有JavaScript错误")

if __name__ == "__main__":
    test_frontend_data_flow()