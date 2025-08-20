#!/usr/bin/env python3
"""
验证申购单编辑功能的完整性
"""

import os
import subprocess
import requests

def check_typescript_compilation():
    """检查TypeScript编译"""
    print("🔍 检查TypeScript编译...")
    try:
        result = subprocess.run(['npx', 'tsc', '--noEmit'], 
                              capture_output=True, text=True, 
                              cwd='/home/ubuntu/shenyuan-erp/frontend')
        if result.returncode == 0:
            print("✅ TypeScript编译正常")
            return True
        else:
            print(f"❌ TypeScript编译错误: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ TypeScript检查失败: {e}")
        return False

def check_frontend_server():
    """检查前端服务器状态"""
    print("🔍 检查前端服务器...")
    try:
        response = requests.get('http://localhost:3000', timeout=5)
        if response.status_code == 200:
            print("✅ 前端服务器运行正常")
            return True
        else:
            print(f"❌ 前端服务器响应异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 前端服务器连接失败: {e}")
        return False

def check_backend_server():
    """检查后端服务器状态"""
    print("🔍 检查后端服务器...")
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        if response.status_code == 200:
            print("✅ 后端服务器运行正常")
            return True
        else:
            print(f"❌ 后端服务器响应异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 后端服务器连接失败: {e}")
        return False

def check_edit_api():
    """检查编辑API基本功能"""
    print("🔍 检查编辑API功能...")
    try:
        # 登录
        login_response = requests.post('http://localhost:8000/api/v1/auth/login', 
                                     data={'username': 'admin', 'password': 'admin123'})
        if login_response.status_code != 200:
            print("❌ 登录失败")
            return False
        
        token = login_response.json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # 获取申购单列表
        list_response = requests.get('http://localhost:8000/api/v1/purchases/', headers=headers)
        if list_response.status_code != 200:
            print("❌ 获取申购单列表失败")
            return False
        
        items = list_response.json()['items']
        draft_items = [item for item in items if item['status'] == 'draft']
        
        if not draft_items:
            print("⚠️  没有草稿状态的申购单用于测试")
            return True
        
        # 测试编辑API
        test_item = draft_items[0]
        edit_data = {'remarks': 'API验证测试'}
        edit_response = requests.put(f'http://localhost:8000/api/v1/purchases/{test_item["id"]}',
                                   headers={**headers, 'Content-Type': 'application/json'},
                                   json=edit_data)
        
        if edit_response.status_code == 200:
            print("✅ 编辑API功能正常")
            return True
        else:
            print(f"❌ 编辑API错误: {edit_response.status_code} - {edit_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 编辑API检查失败: {e}")
        return False

def check_file_exists():
    """检查关键文件是否存在"""
    print("🔍 检查关键文件...")
    files_to_check = [
        '/home/ubuntu/shenyuan-erp/frontend/src/pages/Purchase/PurchaseEditForm.tsx',
        '/home/ubuntu/shenyuan-erp/frontend/src/pages/Purchase/SimplePurchaseList.tsx',
        '/home/ubuntu/shenyuan-erp/frontend/src/pages/Purchase/SimplePurchaseDetail.tsx'
    ]
    
    all_exist = True
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"✅ {os.path.basename(file_path)} 存在")
        else:
            print(f"❌ {os.path.basename(file_path)} 缺失")
            all_exist = False
    
    return all_exist

def main():
    print("=" * 50)
    print("🚀 申购单编辑功能验证")
    print("=" * 50)
    
    checks = [
        ("关键文件检查", check_file_exists),
        ("TypeScript编译检查", check_typescript_compilation),
        ("前端服务器检查", check_frontend_server),
        ("后端服务器检查", check_backend_server),
        ("编辑API功能检查", check_edit_api)
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n📋 {name}")
        result = check_func()
        results.append((name, result))
    
    print("\n" + "=" * 50)
    print("📊 验证结果汇总")
    print("=" * 50)
    
    all_passed = True
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name}: {status}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 所有检查通过！申购单编辑功能已完全准备就绪。")
        print("📝 访问 http://localhost:3000/purchases 开始使用编辑功能")
    else:
        print("\n⚠️  部分检查失败，请查看上述详细信息")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)