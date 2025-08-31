#!/usr/bin/env python3
"""
测试申购单完整工作流
"""
import requests
import json
import time

# 配置
BASE_URL = "http://localhost:8000"

# 用户凭证
USERS = {
    "pm": {"username": "liqiang", "password": "liqiang123", "name": "李强", "role": "项目经理"},
    "purchaser": {"username": "purchaser", "password": "purchase123", "name": "赵采购员", "role": "采购员"},
    "dept": {"username": "dept_manager", "password": "dept123", "name": "李工程部主管", "role": "部门主管"},
    "gm": {"username": "general_manager", "password": "gm123", "name": "张总经理", "role": "总经理"}
}

def login(credentials):
    """登录获取token"""
    response = requests.post(f"{BASE_URL}/api/v1/auth/login", data=credentials)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 登录成功: {data['user']['name']} ({data['user']['role']})")
        return data["access_token"], data["user"]
    else:
        print(f"❌ 登录失败: {response.text}")
        return None, None

def create_purchase_request(token):
    """创建申购单"""
    headers = {"Authorization": f"Bearer {token}"}
    
    purchase_data = {
        "project_id": 3,  # 李强负责的项目
        "system_category": "视频监控系统",
        "required_date": "2025-09-01T00:00:00",
        "remarks": "测试完整工作流",
        "items": [
            {
                "item_name": "网络摄像机",
                "specification": "4MP高清摄像机",
                "brand": "大华",
                "unit": "台",
                "quantity": 10,
                "item_type": "main"
            },
            {
                "item_name": "网线",
                "specification": "超六类网线",
                "brand": "泛达",
                "unit": "米",
                "quantity": 500,
                "item_type": "auxiliary"
            }
        ]
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/purchases/",
        headers=headers,
        json=purchase_data
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 创建申购单成功: {data['request_code']}")
        return data["id"], data["request_code"]
    else:
        print(f"❌ 创建申购单失败: {response.text}")
        return None, None

def submit_purchase_request(token, request_id):
    """提交申购单"""
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.post(
        f"{BASE_URL}/api/v1/purchases/{request_id}/submit",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 提交申购单成功，当前状态: {data['status']}")
        return True
    else:
        print(f"❌ 提交申购单失败: {response.text}")
        return False

def quote_price(token, request_id):
    """采购员询价"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # 先获取申购单详情，获取items的ID
    response = requests.get(
        f"{BASE_URL}/api/v1/purchases/{request_id}",
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"❌ 获取申购单详情失败: {response.text}")
        return False
    
    purchase_detail = response.json()
    items = purchase_detail.get("items", [])
    
    if not items:
        print("❌ 申购单没有明细项")
        return False
    
    # 构建询价明细
    quote_items = []
    total_price = 0
    for item in items:
        unit_price = 2000.00 if "摄像机" in item["item_name"] else 10.00
        quantity = float(item["quantity"]) if isinstance(item["quantity"], str) else item["quantity"]
        item_total = unit_price * quantity
        quote_items.append({
            "item_id": item["id"],
            "unit_price": unit_price,
            "total_price": item_total
        })
        total_price += item_total
    
    quote_data = {
        "quote_price": total_price,
        "expected_delivery_date": "2025-09-15T00:00:00",
        "payment_method": "transfer",
        "payment_terms": "货到付款",
        "quote_notes": "已经与供应商确认价格和交期",
        "items": quote_items
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/purchases/{request_id}/quote",
        headers=headers,
        json=quote_data
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 询价成功，报价: {quote_data['quote_price']}元")
        return True
    else:
        print(f"❌ 询价失败: {response.text}")
        return False

def dept_approve(token, request_id, approved=True):
    """部门主管审批"""
    headers = {"Authorization": f"Bearer {token}"}
    
    approval_data = {
        "approval_status": "approved" if approved else "rejected",
        "approval_notes": "符合项目预算，同意采购" if approved else "预算超支，需要重新询价"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/purchases/{request_id}/dept-approve",
        headers=headers,
        json=approval_data
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 部门主管{'批准' if approved else '拒绝'}申购单")
        return True
    else:
        print(f"❌ 部门审批失败: {response.text}")
        return False

def final_approve(token, request_id, approved=True):
    """总经理最终审批"""
    headers = {"Authorization": f"Bearer {token}"}
    
    approval_data = {
        "approval_status": "approved" if approved else "rejected",
        "approval_notes": "批准采购，尽快执行" if approved else "暂缓采购"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/purchases/{request_id}/final-approve",
        headers=headers,
        json=approval_data
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 总经理最终{'批准' if approved else '拒绝'}申购单")
        return True
    else:
        print(f"❌ 最终审批失败: {response.text}")
        return False

def get_purchase_detail(token, request_id):
    """获取申购单详情"""
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/api/v1/purchases/{request_id}",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n📋 申购单详情:")
        print(f"   编号: {data['request_code']}")
        print(f"   状态: {data['status']}")
        print(f"   当前步骤: {data.get('current_step', 'N/A')}")
        print(f"   总金额: {data.get('total_amount', 'N/A')}")
        return data
    else:
        print(f"❌ 获取详情失败: {response.text}")
        return None

def main():
    print("="*60)
    print("🚀 申购单完整工作流测试")
    print("="*60)
    
    # 1. 项目经理创建并提交申购单
    print("\n📌 步骤1: 项目经理创建并提交申购单")
    pm_token, pm_user = login(USERS["pm"])
    if not pm_token:
        return
    
    request_id, request_code = create_purchase_request(pm_token)
    if not request_id:
        return
    
    time.sleep(1)
    if not submit_purchase_request(pm_token, request_id):
        return
    
    # 2. 采购员询价
    print("\n📌 步骤2: 采购员询价")
    purchaser_token, purchaser_user = login(USERS["purchaser"])
    if not purchaser_token:
        return
    
    time.sleep(1)
    if not quote_price(purchaser_token, request_id):
        return
    
    # 3. 部门主管审批
    print("\n📌 步骤3: 部门主管审批")
    dept_token, dept_user = login(USERS["dept"])
    if not dept_token:
        return
    
    time.sleep(1)
    if not dept_approve(dept_token, request_id, True):
        return
    
    # 4. 总经理最终审批
    print("\n📌 步骤4: 总经理最终审批")
    gm_token, gm_user = login(USERS["gm"])
    if not gm_token:
        return
    
    time.sleep(1)
    if not final_approve(gm_token, request_id, True):
        return
    
    # 5. 查看最终状态
    print("\n📌 步骤5: 查看最终状态")
    detail = get_purchase_detail(gm_token, request_id)
    
    print("\n" + "="*60)
    print("✅ 工作流测试完成！")
    print("="*60)

if __name__ == "__main__":
    main()