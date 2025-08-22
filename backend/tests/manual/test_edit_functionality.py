#!/usr/bin/env python3
"""
测试申购单编辑功能完整流程
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_edit_functionality():
    print("=== 申购单编辑功能测试 ===")
    
    # 1. 登录获取token
    print("1. 登录管理员账号...")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    response = requests.post(f"{BASE_URL}/api/v1/auth/login", data=login_data)
    if response.status_code != 200:
        print(f"登录失败: {response.status_code} - {response.text}")
        return False
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ 登录成功")
    
    # 2. 获取申购单列表，找一个草稿状态的
    print("2. 获取申购单列表...")
    response = requests.get(f"{BASE_URL}/api/v1/purchases/?page=1&size=10", headers=headers)
    if response.status_code != 200:
        print(f"获取申购单失败: {response.status_code} - {response.text}")
        return False
    
    purchases = response.json()
    draft_purchases = [p for p in purchases["items"] if p["status"] == "draft"]
    
    if not draft_purchases:
        print("❌ 没有找到草稿状态的申购单")
        return False
    
    purchase = draft_purchases[0]
    print(f"✅ 找到草稿申购单: {purchase['request_code']}")
    
    # 3. 获取申购单详情
    print("3. 获取申购单详情...")
    response = requests.get(f"{BASE_URL}/api/v1/purchases/{purchase['id']}", headers=headers)
    if response.status_code != 200:
        print(f"获取详情失败: {response.status_code} - {response.text}")
        return False
    
    detail = response.json()
    print(f"✅ 获取详情成功，包含 {len(detail.get('items', []))} 个明细")
    
    # 4. 准备编辑数据
    print("4. 准备编辑数据...")
    edit_data = {
        "required_date": "2024-12-31T10:00:00",
        "remarks": "测试编辑功能 - 已更新",
        "items": []
    }
    
    # 保留原有明细并修改第一个
    for i, item in enumerate(detail.get("items", [])):
        edited_item = {
            "contract_item_id": item.get("contract_item_id"),
            "system_category_id": item.get("system_category_id"),
            "item_name": item["item_name"],
            "specification": item.get("specification"),
            "brand": item.get("brand"),
            "unit": item["unit"],
            "quantity": float(item["quantity"]) + (1 if i == 0 else 0),  # 第一个数量+1
            "unit_price": item.get("unit_price"),
            "total_price": item.get("total_price"),
            "item_type": item.get("item_type", "auxiliary"),
            "remarks": item.get("remarks") + " [已编辑]" if i == 0 and item.get("remarks") else item.get("remarks")
        }
        edit_data["items"].append(edited_item)
    
    # 添加一个新的明细
    new_item = {
        "contract_item_id": None,
        "system_category_id": None,
        "item_name": "编辑测试新增物料",
        "specification": "测试规格",
        "brand": "测试品牌",
        "unit": "个",
        "quantity": 5,
        "item_type": "auxiliary",
        "remarks": "编辑时新增的测试物料"
    }
    edit_data["items"].append(new_item)
    
    print(f"准备更新 {len(edit_data['items'])} 个明细（包含1个新增）")
    
    # 5. 执行编辑
    print("5. 执行编辑...")
    response = requests.put(f"{BASE_URL}/api/v1/purchases/{purchase['id']}", 
                          headers={**headers, "Content-Type": "application/json"}, 
                          data=json.dumps(edit_data))
    
    if response.status_code != 200:
        print(f"编辑失败: {response.status_code} - {response.text}")
        return False
    
    print("✅ 编辑成功")
    
    # 6. 验证编辑结果
    print("6. 验证编辑结果...")
    response = requests.get(f"{BASE_URL}/api/v1/purchases/{purchase['id']}", headers=headers)
    if response.status_code != 200:
        print(f"获取编辑后详情失败: {response.status_code} - {response.text}")
        return False
    
    updated_detail = response.json()
    
    # 检查备注是否更新
    if updated_detail.get("remarks") == "测试编辑功能 - 已更新":
        print("✅ 备注更新成功")
    else:
        print(f"❌ 备注更新失败: 期望 '测试编辑功能 - 已更新'，实际 '{updated_detail.get('remarks')}'")
        return False
    
    # 检查明细数量
    if len(updated_detail.get("items", [])) == len(edit_data["items"]):
        print(f"✅ 明细数量正确: {len(updated_detail['items'])}")
    else:
        print(f"❌ 明细数量不匹配: 期望 {len(edit_data['items'])}，实际 {len(updated_detail.get('items', []))}")
        return False
    
    # 检查是否有新增的测试物料
    test_items = [item for item in updated_detail.get("items", []) if item["item_name"] == "编辑测试新增物料"]
    if test_items:
        print("✅ 新增物料保存成功")
    else:
        print("❌ 新增物料未找到")
        return False
    
    print("🎉 申购单编辑功能测试通过！")
    return True

if __name__ == "__main__":
    success = test_edit_functionality()
    exit(0 if success else 1)