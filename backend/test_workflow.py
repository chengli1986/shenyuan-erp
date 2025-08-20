#!/usr/bin/env python3
"""
测试申购单工作流API的完整脚本
"""
import requests
import json
import time

# 配置
BASE_URL = "http://localhost:8000"
ADMIN_CREDENTIALS = {"username": "admin", "password": "admin123"}
PM_CREDENTIALS = {"username": "liqiang", "password": "liqiang123"}
PURCHASER_CREDENTIALS = {"username": "admin", "password": "admin123"}  # 使用admin作为采购员测试
DEPT_MANAGER_CREDENTIALS = {"username": "admin", "password": "admin123"}  # 使用admin作为部门主管测试
GENERAL_MANAGER_CREDENTIALS = {"username": "admin", "password": "admin123"}  # 使用admin作为总经理测试

def login(credentials):
    """登录获取token"""
    response = requests.post(f"{BASE_URL}/api/v1/auth/login", data=credentials)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"登录失败: {response.text}")
        return None

def test_create_purchase_request():
    """测试创建申购单"""
    token = login(PM_CREDENTIALS)
    if not token:
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 创建申购单数据
    purchase_data = {
        "project_id": 3,  # 李强负责的项目
        "system_category": "视频监控系统",  # 添加所属系统信息
        "required_date": "2025-09-01T00:00:00",
        "remarks": "测试工作流申购单",
        "items": [
            {
                "item_name": "网络摄像机",
                "specification": "4MP网络摄像机",
                "brand": "大华",
                "unit": "台",
                "quantity": 5,
                "item_type": "main"
            }
        ]
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/purchases/",
        headers=headers,
        json=purchase_data
    )
    
    if response.status_code == 200:
        purchase = response.json()
        print(f"✅ 创建申购单成功: {purchase['request_code']}")
        print(f"   当前状态: {purchase['status']}")
        print(f"   当前步骤: {purchase.get('current_step', 'N/A')}")
        return purchase['id']
    else:
        print(f"❌ 创建申购单失败: {response.text}")
        return None

def test_submit_purchase_request(purchase_id):
    """测试提交申购单"""
    token = login(PM_CREDENTIALS)
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.post(
        f"{BASE_URL}/api/v1/purchases/{purchase_id}/submit",
        headers=headers
    )
    
    if response.status_code == 200:
        purchase = response.json()
        print(f"✅ 提交申购单成功: {purchase['request_code']}")
        print(f"   当前状态: {purchase['status']}")
        print(f"   当前步骤: {purchase.get('current_step', 'N/A')}")
        print(f"   当前审批人: {purchase.get('current_approver_id', 'N/A')}")
        return True
    else:
        print(f"❌ 提交申购单失败: {response.text}")
        return False

def test_purchaser_quote(purchase_id):
    """测试采购员询价"""
    token = login(PURCHASER_CREDENTIALS)
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 首先获取申购单明细，获取item_id
    response = requests.get(f"{BASE_URL}/api/v1/purchases/{purchase_id}", headers=headers)
    if response.status_code != 200:
        print(f"❌ 获取申购单详情失败: {response.text}")
        return False
    
    purchase = response.json()
    if not purchase.get('items'):
        print("❌ 申购单没有明细项")
        return False
    
    # 构造询价数据
    quote_data = {
        "payment_method": "prepayment",
        "estimated_delivery_date": "2025-09-15T00:00:00",
        "quote_notes": "已联系供应商，价格优惠",
        "items": []
    }
    
    for item in purchase['items']:
        quote_data["items"].append({
            "item_id": item['id'],
            "unit_price": 2800.00,  # 单价
            "supplier_name": "大华科技有限公司",
            "supplier_contact": "张经理 13800138000",
            "estimated_delivery": "2025-09-15T00:00:00"
        })
    
    response = requests.post(
        f"{BASE_URL}/api/v1/purchases/{purchase_id}/quote",
        headers=headers,
        json=quote_data
    )
    
    if response.status_code == 200:
        purchase = response.json()
        print(f"✅ 采购员询价成功: {purchase['request_code']}")
        print(f"   当前状态: {purchase['status']}")
        print(f"   当前步骤: {purchase.get('current_step', 'N/A')}")
        print(f"   总金额: {purchase.get('total_amount', 'N/A')}")
        return True
    else:
        print(f"❌ 采购员询价失败: {response.text}")
        return False

def test_dept_approve(purchase_id, approve=True):
    """测试部门主管审批"""
    token = login(DEPT_MANAGER_CREDENTIALS)
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    approval_data = {
        "approval_status": "approved" if approve else "rejected",
        "approval_notes": "技术规格符合要求，预算合理" if approve else "预算超标，请重新询价"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/purchases/{purchase_id}/dept-approve",
        headers=headers,
        json=approval_data
    )
    
    if response.status_code == 200:
        purchase = response.json()
        status_text = "批准" if approve else "拒绝"
        print(f"✅ 部门主管{status_text}成功: {purchase['request_code']}")
        print(f"   当前状态: {purchase['status']}")
        print(f"   当前步骤: {purchase.get('current_step', 'N/A')}")
        return True
    else:
        print(f"❌ 部门主管审批失败: {response.text}")
        return False

def test_final_approve(purchase_id, approve=True):
    """测试总经理最终审批"""
    token = login(GENERAL_MANAGER_CREDENTIALS)
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    approval_data = {
        "approval_status": "approved" if approve else "rejected",
        "approval_notes": "同意采购，注意按时交付" if approve else "暂缓采购，需要重新评估"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/purchases/{purchase_id}/final-approve",
        headers=headers,
        json=approval_data
    )
    
    if response.status_code == 200:
        purchase = response.json()
        status_text = "最终批准" if approve else "最终拒绝"
        print(f"✅ 总经理{status_text}成功: {purchase['request_code']}")
        print(f"   当前状态: {purchase['status']}")
        print(f"   当前步骤: {purchase.get('current_step', 'N/A')}")
        return True
    else:
        print(f"❌ 总经理审批失败: {response.text}")
        return False

def test_workflow_logs(purchase_id):
    """测试查看工作流日志"""
    token = login(ADMIN_CREDENTIALS)
    if not token:
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/api/v1/purchases/{purchase_id}/workflow-logs",
        headers=headers
    )
    
    if response.status_code == 200:
        logs_data = response.json()
        print(f"✅ 工作流日志查询成功: {logs_data['request_code']}")
        print(f"   当前状态: {logs_data['current_status']}")
        print(f"   当前步骤: {logs_data['current_step']}")
        print(f"   操作记录数: {logs_data['total_logs']}")
        
        for i, log in enumerate(logs_data['logs'], 1):
            print(f"   {i}. {log['operation']} | {log['operator_name']} ({log['operator_role']}) | {log['created_at']}")
            if log['operation_notes']:
                print(f"      备注: {log['operation_notes']}")
    else:
        print(f"❌ 工作流日志查询失败: {response.text}")

def test_complete_workflow():
    """测试完整工作流：创建 -> 提交 -> 询价 -> 部门审批 -> 最终审批"""
    print("🚀 开始测试完整申购单工作流...")
    
    # 步骤1: 项目经理创建申购单
    print("\n--- 步骤1: 项目经理创建申购单 ---")
    purchase_id = test_create_purchase_request()
    if not purchase_id:
        return
    
    time.sleep(1)
    
    # 步骤2: 项目经理提交申购单
    print("\n--- 步骤2: 项目经理提交申购单 ---")
    if not test_submit_purchase_request(purchase_id):
        return
    
    time.sleep(1)
    
    # 步骤3: 采购员询价
    print("\n--- 步骤3: 采购员询价 ---")
    if not test_purchaser_quote(purchase_id):
        return
    
    time.sleep(1)
    
    # 步骤4: 部门主管审批
    print("\n--- 步骤4: 部门主管审批 ---")
    if not test_dept_approve(purchase_id, approve=True):
        return
    
    time.sleep(1)
    
    # 步骤5: 总经理最终审批
    print("\n--- 步骤5: 总经理最终审批 ---")
    if not test_final_approve(purchase_id, approve=True):
        return
    
    time.sleep(1)
    
    # 步骤6: 查看完整工作流日志
    print("\n--- 步骤6: 查看工作流历史 ---")
    test_workflow_logs(purchase_id)
    
    print(f"\n🎉 完整工作流测试成功! 申购单ID: {purchase_id}")

def test_rejection_workflow():
    """测试拒绝流程"""
    print("\n🔄 开始测试拒绝流程...")
    
    # 创建并提交申购单
    purchase_id = test_create_purchase_request()
    if not purchase_id:
        return
    
    test_submit_purchase_request(purchase_id)
    test_purchaser_quote(purchase_id)
    
    # 部门主管拒绝
    print("\n--- 测试部门主管拒绝 ---")
    test_dept_approve(purchase_id, approve=False)
    
    # 查看工作流日志
    test_workflow_logs(purchase_id)

if __name__ == "__main__":
    print("🚀 申购单工作流API测试套件")
    print("=" * 50)
    
    # 测试完整的通过流程
    test_complete_workflow()
    
    # 测试拒绝流程（可选）
    print("\n" + "=" * 50)
    # test_rejection_workflow()
    
    print("\n✅ 所有测试完成!")