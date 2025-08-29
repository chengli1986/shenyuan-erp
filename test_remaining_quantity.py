#!/usr/bin/env python3
"""
测试申购单剩余数量计算逻辑
验证只有总经理批准后的申购单才会影响剩余可申购数量
"""

import json
import requests
from datetime import datetime
from typing import Dict, Any

# API基础配置
BASE_URL = "http://localhost:8000/api/v1"

def login(username: str, password: str) -> str:
    """登录获取token"""
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data={"username": username, "password": password}
    )
    if response.status_code == 200:
        return response.json()['access_token']
    raise Exception(f"登录失败: {response.text}")

def get_contract_item_details(token: str, item_id: int) -> Dict[str, Any]:
    """获取合同清单项详情（包含剩余数量）"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/purchases/contract-items/{item_id}/details",
        headers=headers
    )
    if response.status_code == 200:
        return response.json()
    raise Exception(f"获取合同清单项失败: {response.text}")

def get_purchase_requests(token: str, status: str = None) -> Dict[str, Any]:
    """获取申购单列表"""
    headers = {"Authorization": f"Bearer {token}"}
    params = {"size": 100}
    if status:
        params["status"] = status
    
    response = requests.get(
        f"{BASE_URL}/purchases/",
        headers=headers,
        params=params
    )
    return response.json()

def get_purchase_detail(token: str, request_id: int) -> Dict[str, Any]:
    """获取申购单详情"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/purchases/{request_id}",
        headers=headers
    )
    if response.status_code == 200:
        return response.json()
    raise Exception(f"获取申购单详情失败: {response.text}")

def main():
    print("=" * 70)
    print("申购单剩余数量计算逻辑测试")
    print("验证：只有总经理批准后的申购单才会影响剩余可申购数量")
    print("=" * 70)
    
    # 登录
    token = login("admin", "admin123")
    print("✓ 登录成功\n")
    
    # 查找一个典型的合同清单项进行测试（例如：摄像机）
    # 使用项目2的数据
    contract_item_id = 1  # 这个需要根据实际数据调整
    
    try:
        # 获取合同清单项详情
        item_details = get_contract_item_details(token, contract_item_id)
        print(f"合同清单项信息:")
        print(f"  物料名称: {item_details['item']['item_name']}")
        print(f"  规格型号: {item_details['item']['specification']}")
        print(f"  合同数量: {item_details['item']['quantity']}")
        print(f"  已申购数量: {item_details['purchased_quantity']}")
        print(f"  剩余可申购: {item_details['remaining_quantity']}")
        print()
        
        # 获取不同状态的申购单统计
        print("申购单状态统计:")
        statuses = ['draft', 'submitted', 'price_quoted', 'dept_approved', 'final_approved']
        status_names = {
            'draft': '草稿',
            'submitted': '已提交',
            'price_quoted': '已询价',
            'dept_approved': '部门已批准',
            'final_approved': '总经理已批准'
        }
        
        total_by_status = {}
        for status in statuses:
            purchases = get_purchase_requests(token, status)
            count = 0
            quantity_sum = 0
            
            # 统计该状态下涉及该合同清单项的数量
            for pr in purchases['items']:
                pr_detail = get_purchase_detail(token, pr['id'])
                if 'items' in pr_detail:
                    for item in pr_detail['items']:
                        if item.get('contract_item_id') == contract_item_id:
                            quantity_sum += item['quantity']
                            count += 1
            
            total_by_status[status] = {
                'count': count,
                'quantity': quantity_sum
            }
            
            print(f"  {status_names[status]}: {count}个申购单，总数量{quantity_sum}")
        
        print()
        print("验证结果:")
        
        # 计算应该计入的数量（只有final_approved）
        should_count = total_by_status['final_approved']['quantity']
        
        print(f"  应计入已申购数量（仅总经理批准）: {should_count}")
        print(f"  API返回的已申购数量: {item_details['purchased_quantity']}")
        
        if abs(should_count - item_details['purchased_quantity']) < 0.01:
            print("  ✅ 计算逻辑正确！只统计了总经理批准的申购单")
        else:
            print("  ❌ 计算逻辑可能有问题，数量不匹配")
        
        print()
        print("其他状态的申购单数量（不应计入）:")
        for status in ['draft', 'submitted', 'price_quoted', 'dept_approved']:
            if total_by_status[status]['quantity'] > 0:
                print(f"  {status_names[status]}: {total_by_status[status]['quantity']} (不计入)")
        
    except Exception as e:
        print(f"测试过程中出错: {e}")
        print("\n提示：请确保数据库中有申购单数据，并调整contract_item_id为实际存在的ID")
    
    print("\n" + "=" * 70)
    print("测试完成")
    print("=" * 70)

if __name__ == "__main__":
    main()