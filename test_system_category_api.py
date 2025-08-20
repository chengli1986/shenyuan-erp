#!/usr/bin/env python3
"""
通过API测试系统分类功能
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def get_admin_token():
    """获取管理员token"""
    response = requests.post(f"{BASE_URL}/api/v1/auth/login", data={
        "username": "admin",
        "password": "admin123"
    })
    return response.json()['access_token']

def test_system_category_api():
    """测试系统分类API"""
    token = get_admin_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    print("=== 系统分类API测试 ===")
    
    # 1. 获取项目2的系统分类
    response = requests.get(f"{BASE_URL}/api/v1/purchases/system-categories/by-project/2", headers=headers)
    if response.status_code == 200:
        data = response.json()
        categories = data if isinstance(data, list) else data.get('categories', [])
        print(f"项目2的系统分类数量: {len(categories)}")
        for cat in categories[:3]:
            print(f"  - ID: {cat['id']}, 名称: {cat['category_name']}")
    
    # 2. 获取摄像机的系统分类推荐
    response = requests.get(f"{BASE_URL}/api/v1/purchases/system-categories/by-material", 
                          params={"project_id": 2, "material_name": "网络摄像机"}, 
                          headers=headers)
    if response.status_code == 200:
        result = response.json()
        print(f"\n摄像机推荐的系统分类: {len(result.get('categories', []))}")
        for cat in result.get('categories', [])[:3]:
            print(f"  - ID: {cat['id']}, 名称: {cat['category_name']}, 推荐: {cat.get('is_suggested', False)}")
    
    # 3. 创建一个测试申购单，包含系统分类
    print("\n=== 创建测试申购单 ===")
    test_purchase = {
        "project_id": 2,
        "required_date": "2025-08-20T00:00:00",
        "items": [
            {
                "item_name": "网络摄像机",
                "specification": "DH-IPC-HFW5831EP-ZE",
                "brand": "大华",
                "unit": "个",
                "quantity": 2,
                "item_type": "auxiliary",
                "system_category_id": 1,  # 设置系统分类ID
                "remarks": "测试系统分类功能"
            }
        ]
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/purchases/", 
                           json=test_purchase, 
                           headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        purchase_id = result['id']
        print(f"创建成功，申购单ID: {purchase_id}")
        
        # 4. 获取创建的申购单详情，检查系统分类是否保存
        response = requests.get(f"{BASE_URL}/api/v1/purchases/{purchase_id}", headers=headers)
        if response.status_code == 200:
            purchase_detail = response.json()
            item = purchase_detail['items'][0]
            print(f"申购明细:")
            print(f"  - 物料名称: {item['item_name']}")
            print(f"  - system_category_id: {item.get('system_category_id')}")
            print(f"  - system_category_name: {item.get('system_category_name')}")
    else:
        print(f"创建失败: {response.status_code} - {response.text}")

if __name__ == "__main__":
    test_system_category_api()