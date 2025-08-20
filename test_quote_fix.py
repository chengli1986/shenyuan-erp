#!/usr/bin/env python3
"""
验证询价功能修复脚本
"""
import requests
import json

def test_quote_functionality():
    """测试询价功能是否正常工作"""
    base_url = "http://localhost:8000/api/v1"
    
    # 1. 登录采购员账号
    print("1. 登录采购员账号...")
    login_response = requests.post(
        f"{base_url}/auth/login",
        data={"username": "purchaser", "password": "purchase123"}
    )
    
    if login_response.status_code != 200:
        print(f"❌ 登录失败: {login_response.text}")
        return False
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ 登录成功")
    
    # 2. 获取待询价的申购单
    print("\n2. 获取待询价申购单...")
    requests_response = requests.get(
        f"{base_url}/purchases/?status=submitted",
        headers=headers
    )
    
    if requests_response.status_code != 200:
        print(f"❌ 获取申购单失败: {requests_response.text}")
        return False
    
    submitted_requests = requests_response.json()["items"]
    if not submitted_requests:
        print("❌ 没有待询价的申购单")
        return False
    
    test_request = submitted_requests[0]
    print(f"✅ 找到待询价申购单: {test_request['request_code']}")
    
    # 3. 获取申购单详情
    print(f"\n3. 获取申购单 {test_request['id']} 详情...")
    detail_response = requests.get(
        f"{base_url}/purchases/{test_request['id']}",
        headers=headers
    )
    
    if detail_response.status_code != 200:
        print(f"❌ 获取详情失败: {detail_response.text}")
        return False
    
    detail = detail_response.json()
    if not detail.get("items"):
        print("❌ 申购单没有明细项")
        return False
    
    first_item = detail["items"][0]
    print(f"✅ 获取到明细项: {first_item['item_name']} (ID: {first_item['id']})")
    
    # 4. 提交询价
    print("\n4. 提交询价...")
    quote_data = {
        "quote_notes": "自动化测试询价",
        "items": [{
            "item_id": first_item["id"],
            "unit_price": 999,
            "supplier_name": "测试供应商",
            "supplier_contact": "13800138000",
            "supplier_contact_person": "测试经理",
            "payment_method": "月结30天",
            "estimated_delivery": "2025-09-15T00:00:00"
        }]
    }
    
    quote_response = requests.post(
        f"{base_url}/purchases/{test_request['id']}/quote",
        headers={**headers, "Content-Type": "application/json"},
        data=json.dumps(quote_data)
    )
    
    if quote_response.status_code == 200:
        result = quote_response.json()
        print(f"✅ 询价成功! 申购单状态: {result['status']}")
        print(f"   当前步骤: {result['current_step']}")
        print(f"   总金额: ¥{result['total_amount']}")
        return True
    else:
        print(f"❌ 询价失败: {quote_response.status_code}")
        print(f"   错误信息: {quote_response.text}")
        return False

if __name__ == "__main__":
    print("🔍 测试询价功能修复效果")
    print("=" * 40)
    
    success = test_quote_functionality()
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 询价功能测试通过!")
    else:
        print("❌ 询价功能测试失败!")