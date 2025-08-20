#!/usr/bin/env python3
"""
测试数组类型修复效果
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

def test_api_response_format():
    """测试API响应格式"""
    token = get_admin_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    print("=== API响应格式测试 ===")
    
    # 测试系统分类API响应格式
    response = requests.get(f"{BASE_URL}/api/v1/purchases/system-categories/by-project/2", headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"API响应类型: {type(data)}")
        print(f"API响应内容: {data}")
        
        if isinstance(data, list):
            print("✅ 响应是数组格式")
            print(f"数组长度: {len(data)}")
        elif isinstance(data, dict) and 'categories' in data:
            print("✅ 响应是对象格式，包含categories字段")
            print(f"categories数组长度: {len(data['categories'])}")
        else:
            print("❌ 响应格式异常")
    else:
        print(f"❌ API调用失败: {response.status_code}")

if __name__ == "__main__":
    test_api_response_format()