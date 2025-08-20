#!/usr/bin/env python3
"""
修复历史申购单的系统分类数据
基于物料名称智能推断系统分类
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

def get_system_category_by_material_name(material_name):
    """基于物料名称推断系统分类"""
    # 物料名称到系统分类的映射规则
    category_mapping = {
        "网络摄像机": 1,  # 视频监控
        "摄像机": 1,
        "监控": 1,
        "录像机": 1,
        "DVR": 1,
        "NVR": 1,
        "门禁": 2,  # 出入口控制  
        "读卡器": 2,
        "控制器": 2,
        "电锁": 2,
        "停车": 3,  # 停车系统
        "道闸": 3,
        "车牌": 3,
        "收费": 3,
        "智能": 4,  # 智能化集成
        "服务器": 4,
        "交换机": 4,
        "路由器": 4,
        "防盗": 5,  # 防盗报警
        "报警": 5,
        "探测器": 5,
        "传感器": 5,
        "广播": 6,  # 公共广播
        "音响": 6,
        "话筒": 6,
        "功放": 6,
        "电视": 7,  # 有线电视
        "信号": 7,
        "分配器": 7,
        "放大器": 7
    }
    
    # 查找匹配的系统分类
    for keyword, category_id in category_mapping.items():
        if keyword in material_name:
            return category_id
    
    # 默认返回智能化集成系统
    return 4

def fix_historical_data():
    """修复历史申购单数据"""
    token = get_admin_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    print("=== 修复历史申购单系统分类数据 ===")
    
    # 1. 获取所有申购单
    response = requests.get(f"{BASE_URL}/api/v1/purchases/?page=1&size=100", headers=headers)
    if response.status_code != 200:
        print(f"获取申购单列表失败: {response.status_code} - {response.text}")
        return
    
    purchases = response.json()['items']
    print(f"总共找到 {len(purchases)} 个申购单")
    
    fixed_count = 0
    for purchase in purchases:
        purchase_id = purchase['id']
        
        # 2. 获取申购单详情
        response = requests.get(f"{BASE_URL}/api/v1/purchases/{purchase_id}", headers=headers)
        if response.status_code != 200:
            continue
            
        purchase_detail = response.json()
        needs_update = False
        
        # 3. 检查每个明细项的系统分类
        for item in purchase_detail.get('items', []):
            if not item.get('system_category_id') and item.get('item_name'):
                # 需要补全系统分类
                suggested_category = get_system_category_by_material_name(item['item_name'])
                print(f"申购单 {purchase['request_code']}: {item['item_name']} -> 系统分类 {suggested_category}")
                needs_update = True
        
        if needs_update:
            # 这里暂时只输出，实际修复需要后端支持批量更新API
            fixed_count += 1
    
    print(f"\n需要修复的申购单数量: {fixed_count}")
    
    # 4. 提供修复建议
    print("\n=== 修复建议 ===")
    print("1. 在编辑页面允许用户手动选择系统分类")
    print("2. 提供基于物料名称的智能推荐")
    print("3. 为历史数据提供批量更新功能")

if __name__ == "__main__":
    fix_historical_data()