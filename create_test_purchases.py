#!/usr/bin/env python3
"""
创建测试用申购单脚本
为李强和孙赟两个项目经理创建草稿状态的申购单，便于测试批量删除功能
"""

import requests
import json
from datetime import datetime, timedelta

def login_user(username, password):
    """登录用户获取token"""
    response = requests.post('http://localhost:8000/api/v1/auth/login', data={
        'username': username,
        'password': password
    })
    if response.status_code == 200:
        return response.json()['access_token']
    else:
        print(f"登录失败: {username}")
        return None

def create_purchase_request(token, project_id, item_data, requester_name):
    """创建申购单"""
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    purchase_data = {
        "project_id": project_id,
        "required_date": (datetime.now() + timedelta(days=7)).isoformat(),
        "system_category": "视频监控系统",
        "remarks": f"测试申购单 - {requester_name}创建",
        "items": [item_data]
    }
    
    response = requests.post(
        'http://localhost:8000/api/v1/purchases/',
        headers=headers,
        json=purchase_data
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 成功创建申购单: {result['request_code']} (项目ID: {project_id})")
        return result
    else:
        print(f"❌ 创建申购单失败: {response.status_code} - {response.text}")
        return None

def main():
    print("🚀 开始创建测试用申购单...")
    
    # 登录两个项目经理
    liqiang_token = login_user('liqiang', 'liqiang123')  # 李强
    sunyun_token = login_user('sunyun', 'sunyun123')     # 孙赟
    
    if not liqiang_token or not sunyun_token:
        print("❌ 登录失败，退出")
        return
    
    # 为孙赟项目经理创建申购单 (项目2)
    print("\n🔸 为孙赟创建申购单 (项目2: 娄山关路445弄综合弱电智能化)")
    
    sunyun_items = [
        {
            "item_name": "高清网络摄像机",
            "specification": "DH-IPC-HFW2431S-S-S2",
            "brand": "大华",
            "unit": "台",
            "quantity": 8,
            "item_type": "main",
            "remarks": "孙赟项目-主要设备1"
        },
        {
            "item_name": "网络硬盘录像机",
            "specification": "DH-NVR4216-16P-4KS2",
            "brand": "大华", 
            "unit": "台",
            "quantity": 2,
            "item_type": "main",
            "remarks": "孙赟项目-主要设备2"
        },
        {
            "item_name": "网线",
            "specification": "超五类非屏蔽网线",
            "brand": "普联",
            "unit": "箱",
            "quantity": 5,
            "item_type": "auxiliary",
            "remarks": "孙赟项目-辅材1"
        },
        {
            "item_name": "配电箱",
            "specification": "PZ30-12回路",
            "brand": "正泰",
            "unit": "个",
            "quantity": 3,
            "item_type": "auxiliary", 
            "remarks": "孙赟项目-辅材2"
        }
    ]
    
    for i, item in enumerate(sunyun_items, 1):
        create_purchase_request(sunyun_token, 2, item, f"孙赟-{i}")
    
    # 为李强项目经理创建申购单 (项目3)
    print("\n🔹 为李强创建申购单 (项目3: 某小区智能化改造项目)")
    
    liqiang_items = [
        {
            "item_name": "智能门禁控制器",
            "specification": "DS-K2604T",
            "brand": "海康威视",
            "unit": "台", 
            "quantity": 6,
            "item_type": "main",
            "remarks": "李强项目-门禁设备1"
        },
        {
            "item_name": "人脸识别终端",
            "specification": "DS-K1T671MF",
            "brand": "海康威视",
            "unit": "台",
            "quantity": 4,
            "item_type": "main", 
            "remarks": "李强项目-门禁设备2"
        },
        {
            "item_name": "电子锁",
            "specification": "磁力锁-600KG",
            "brand": "亚萨合莱",
            "unit": "把",
            "quantity": 12,
            "item_type": "auxiliary",
            "remarks": "李强项目-门禁配件1"
        },
        {
            "item_name": "门禁电源",
            "specification": "12V 5A开关电源",
            "brand": "明纬",
            "unit": "个",
            "quantity": 8,
            "item_type": "auxiliary",
            "remarks": "李强项目-门禁配件2"
        },
        {
            "item_name": "管理软件",
            "specification": "门禁管理平台V3.0",
            "brand": "海康威视",
            "unit": "套",
            "quantity": 1,
            "item_type": "auxiliary",
            "remarks": "李强项目-软件"
        }
    ]
    
    for i, item in enumerate(liqiang_items, 1):
        create_purchase_request(liqiang_token, 3, item, f"李强-{i}")
    
    print("\n🎉 测试申购单创建完成！")
    print("\n📊 创建总结:")
    print("- 孙赟项目经理 (项目2): 4个草稿申购单")
    print("- 李强项目经理 (项目3): 5个草稿申购单") 
    print("- 总计: 9个草稿申购单")
    print("\n🧪 测试建议:")
    print("1. 以孙赟身份登录 - 应该只看到项目2的4个申购单")
    print("2. 以李强身份登录 - 应该只看到项目3的5个申购单")
    print("3. 以管理员身份登录 - 应该看到所有9个申购单")
    print("4. 测试批量删除功能 - 选择多个进行删除测试")

if __name__ == "__main__":
    main()