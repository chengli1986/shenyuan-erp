#!/usr/bin/env python3
"""
通过API创建申购单工作流测试数据
创建不同工作流状态的申购单，用于测试工作流历史记录和状态显示功能
"""

import requests
import json
from datetime import datetime, timedelta

# API配置
BASE_URL = "http://localhost:8000/api/v1"
FRONTEND_URL = "http://localhost:3000/api/v1"

def get_auth_token(username, password):
    """获取认证token"""
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            data={"username": username, "password": password}
        )
        if response.status_code == 200:
            return response.json()['access_token']
        else:
            print(f"登录失败 {username}: {response.status_code}")
            return None
    except Exception as e:
        print(f"登录错误 {username}: {e}")
        return None

def create_test_purchase_request(token, request_data):
    """创建测试申购单"""
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/purchases/",
            json=request_data,
            headers=headers
        )
        if response.status_code == 200:
            return response.json()
        else:
            print(f"创建申购单失败: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"创建申购单错误: {e}")
        return None

def create_workflow_test_data():
    """创建工作流测试数据"""
    print("🚀 开始通过API创建申购单工作流测试数据...")
    
    # 获取用户tokens
    tokens = {
        'admin': get_auth_token('admin', 'admin123'),
        'sunyun': get_auth_token('sunyun', 'sunyun123'),
        'liqiang': get_auth_token('liqiang', 'liqiang123'),
        'purchaser': get_auth_token('purchaser', 'purchase123'),
        'dept_manager': get_auth_token('dept_manager', 'dept123'),
        'general_manager': get_auth_token('general_manager', 'gm123'),
    }
    
    print(f"📊 获取用户token: {[k for k, v in tokens.items() if v]}")
    
    # 测试数据配置
    test_scenarios = [
        {
            "name": "草稿状态申购单",
            "token_user": "sunyun",
            "data": {
                "project_id": 2,
                "required_date": (datetime.now() + timedelta(days=30)).isoformat(),
                "remarks": "工作流测试数据 - 草稿状态申购单",
                "items": [
                    {
                        "item_name": "测试物料A",
                        "quantity": 10,
                        "unit": "个",
                        "item_type": "auxiliary",
                        "remarks": "工作流测试用"
                    },
                    {
                        "item_name": "测试物料B", 
                        "quantity": 5,
                        "unit": "台",
                        "item_type": "auxiliary",
                        "remarks": "工作流测试用"
                    }
                ]
            }
        },
        {
            "name": "已提交待询价申购单",
            "token_user": "sunyun",
            "data": {
                "project_id": 2,
                "required_date": (datetime.now() + timedelta(days=25)).isoformat(),
                "remarks": "工作流测试数据 - 已提交待询价申购单",
                "items": [
                    {
                        "item_name": "监控摄像头",
                        "quantity": 20,
                        "unit": "台", 
                        "item_type": "auxiliary",
                        "remarks": "高清监控设备"
                    },
                    {
                        "item_name": "网络交换机",
                        "quantity": 2,
                        "unit": "台",
                        "item_type": "auxiliary", 
                        "remarks": "网络基础设备"
                    }
                ]
            },
            "workflow_actions": ["submit"]  # 创建后执行提交
        },
        {
            "name": "门禁设备申购单",
            "token_user": "liqiang",
            "data": {
                "project_id": 3,
                "required_date": (datetime.now() + timedelta(days=20)).isoformat(),
                "remarks": "工作流测试数据 - 门禁设备申购单",
                "items": [
                    {
                        "item_name": "门禁控制器",
                        "quantity": 5,
                        "unit": "台",
                        "item_type": "auxiliary",
                        "remarks": "智能门禁主控制器"
                    },
                    {
                        "item_name": "读卡器",
                        "quantity": 10, 
                        "unit": "个",
                        "item_type": "auxiliary",
                        "remarks": "IC卡读取设备"
                    }
                ]
            },
            "workflow_actions": ["submit"]  # 创建后执行提交
        },
        {
            "name": "高清监控系统申购单",
            "token_user": "sunyun",
            "data": {
                "project_id": 2,
                "required_date": (datetime.now() + timedelta(days=35)).isoformat(),
                "remarks": "工作流测试数据 - 高清监控系统申购单",
                "items": [
                    {
                        "item_name": "高清摄像机",
                        "quantity": 15,
                        "unit": "台",
                        "item_type": "auxiliary",
                        "remarks": "4K高清网络摄像机"
                    },
                    {
                        "item_name": "录像主机",
                        "quantity": 1,
                        "unit": "台", 
                        "item_type": "auxiliary",
                        "remarks": "网络录像机NVR"
                    }
                ]
            },
            "workflow_actions": ["submit"]  # 创建后执行提交
        },
        {
            "name": "智能锁系统申购单",
            "token_user": "liqiang",
            "data": {
                "project_id": 3,
                "required_date": (datetime.now() + timedelta(days=40)).isoformat(),
                "remarks": "工作流测试数据 - 智能锁系统申购单",
                "items": [
                    {
                        "item_name": "智能锁",
                        "quantity": 50,
                        "unit": "把",
                        "item_type": "auxiliary",
                        "remarks": "指纹+密码智能门锁"
                    },
                    {
                        "item_name": "指纹识别器", 
                        "quantity": 10,
                        "unit": "台",
                        "item_type": "auxiliary",
                        "remarks": "独立指纹识别模块"
                    }
                ]
            },
            "workflow_actions": ["submit"]  # 创建后执行提交
        },
        {
            "name": "测试设备申购单",
            "token_user": "sunyun",
            "data": {
                "project_id": 2,
                "required_date": (datetime.now() + timedelta(days=15)).isoformat(),
                "remarks": "工作流测试数据 - 测试设备申购单",
                "items": [
                    {
                        "item_name": "测试设备X",
                        "quantity": 1,
                        "unit": "台",
                        "item_type": "auxiliary",
                        "remarks": "昂贵测试设备"
                    }
                ]
            },
            "workflow_actions": ["submit"]  # 创建后执行提交
        }
    ]
    
    created_requests = []
    
    # 创建申购单
    for i, scenario in enumerate(test_scenarios):
        print(f"\n📝 创建测试场景 {i+1}: {scenario['name']}")
        
        user_token = tokens.get(scenario['token_user'])
        if not user_token:
            print(f"   ⚠️  跳过: 用户 {scenario['token_user']} token获取失败")
            continue
        
        # 创建申购单
        result = create_test_purchase_request(user_token, scenario['data'])
        if result:
            print(f"   ✅ 申购单创建成功: {result.get('request_code')}")
            created_requests.append({
                "request": result,
                "token": user_token,
                "scenario": scenario
            })
            
            # 执行工作流操作
            if scenario.get('workflow_actions'):
                purchase_id = result['id']
                for action in scenario['workflow_actions']:
                    try:
                        if action == 'submit':
                            submit_response = requests.post(
                                f"{BASE_URL}/purchases/{purchase_id}/submit",
                                headers={'Authorization': f'Bearer {user_token}'}
                            )
                            if submit_response.status_code == 200:
                                print(f"      📊 提交成功")
                            else:
                                print(f"      ❌ 提交失败: {submit_response.status_code}")
                    except Exception as e:
                        print(f"      ❌ 工作流操作失败 {action}: {e}")
        else:
            print(f"   ❌ 申购单创建失败")
    
    print(f"\n🎉 工作流测试数据创建完成!")
    print(f"📊 总计创建: {len(created_requests)} 个申购单")
    
    # 验证创建结果
    if tokens['admin']:
        try:
            response = requests.get(
                f"{BASE_URL}/purchases/?page=1&size=50",
                headers={'Authorization': f'Bearer {tokens["admin"]}'}
            )
            if response.status_code == 200:
                data = response.json()
                total_requests = data.get('total', 0)
                print(f"📊 数据库中总申购单数: {total_requests}")
                
                # 显示最新创建的申购单
                recent_requests = [
                    r for r in data.get('items', [])
                    if 'WF-' in r.get('request_code', '') or '工作流测试' in r.get('remarks', '')
                ]
                
                print(f"\n🔍 工作流测试申购单:")
                for req in recent_requests[:10]:  # 显示最多10个
                    print(f"   {req.get('request_code')}: {req.get('status')} -> {req.get('current_step', 'N/A')}")
        except Exception as e:
            print(f"❌ 验证数据失败: {e}")
    
    print(f"\n🚀 现在可以在前端测试以下功能:")
    print(f"   1. 工作流状态显示组件 - 不同状态的标签显示")
    print(f"   2. 工作流历史记录功能 - 点击'工作流历史'按钮")
    print(f"   3. 不同角色的操作权限 - 登录不同用户查看")
    print(f"   4. 工作流按钮和操作流程 - 提交、询价、审批等")
    print(f"\n📱 访问地址: http://localhost:3000 或 http://18.219.25.24:3000")

if __name__ == "__main__":
    create_workflow_test_data()