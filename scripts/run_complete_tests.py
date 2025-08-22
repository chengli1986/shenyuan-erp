#!/usr/bin/env python3
"""
运行完整的系统功能测试
包括：后端API健康检查、前端服务检查、申购模块功能测试、权限系统测试
"""

import subprocess
import requests
import json
import time
from datetime import datetime

# 配置
BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"

# 测试结果
test_results = []
passed_tests = 0
failed_tests = 0

def run_test(test_name, test_func):
    """运行单个测试"""
    global passed_tests, failed_tests
    print(f"\n🔍 测试: {test_name}")
    try:
        result = test_func()
        if result:
            print(f"  ✅ 通过")
            test_results.append({"name": test_name, "status": "PASSED", "message": ""})
            passed_tests += 1
        else:
            print(f"  ❌ 失败")
            test_results.append({"name": test_name, "status": "FAILED", "message": "测试返回False"})
            failed_tests += 1
    except Exception as e:
        print(f"  ❌ 错误: {str(e)}")
        test_results.append({"name": test_name, "status": "ERROR", "message": str(e)})
        failed_tests += 1

def test_backend_health():
    """测试后端服务健康状态"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def test_frontend_proxy():
    """测试前端代理功能"""
    try:
        response = requests.get(f"{FRONTEND_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def test_auth_login():
    """测试用户登录功能"""
    try:
        response = requests.post(f"{BASE_URL}/api/v1/auth/login", data={
            "username": "admin",
            "password": "admin123"
        })
        data = response.json()
        return "access_token" in data and data.get("user", {}).get("username") == "admin"
    except:
        return False

def test_purchase_list_api():
    """测试申购单列表API"""
    try:
        # 获取token
        login_response = requests.post(f"{BASE_URL}/api/v1/auth/login", data={
            "username": "admin",
            "password": "admin123"
        })
        token = login_response.json()["access_token"]
        
        # 获取申购单列表
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/v1/purchases/", headers=headers)
        data = response.json()
        
        return response.status_code == 200 and "items" in data
    except:
        return False

def test_project_manager_permission():
    """测试项目经理权限隔离"""
    try:
        # 登录孙赟
        login_response = requests.post(f"{BASE_URL}/api/v1/auth/login", data={
            "username": "sunyun",
            "password": "sunyun123"
        })
        
        if login_response.status_code != 200:
            return False
            
        token = login_response.json()["access_token"]
        
        # 获取申购单列表
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/v1/purchases/", headers=headers)
        data = response.json()
        
        # 验证只能看到项目2的申购单
        if response.status_code == 200 and "items" in data:
            project_ids = set([item["project_id"] for item in data["items"]])
            # 孙赟只能看到项目2的申购单
            return project_ids.issubset({2})
        return False
    except:
        return False

def test_purchase_workflow():
    """测试申购单工作流状态"""
    try:
        # 获取管理员token
        login_response = requests.post(f"{BASE_URL}/api/v1/auth/login", data={
            "username": "admin",
            "password": "admin123"
        })
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 获取申购单列表
        response = requests.get(f"{BASE_URL}/api/v1/purchases/", headers=headers)
        data = response.json()
        
        if response.status_code == 200 and "items" in data:
            if len(data["items"]) > 0:
                # 检查是否有各种状态的申购单
                statuses = set([item["status"] for item in data["items"]])
                # 验证状态是有效的工作流状态
                valid_statuses = {"draft", "submitted", "price_quoted", "dept_approved", "final_approved", "rejected"}
                # 只要有任何有效状态就算通过
                return len(statuses.intersection(valid_statuses)) > 0
            else:
                # 没有申购单也算通过（空数据库）
                return True
        return False
    except:
        return False

def test_system_categories():
    """测试系统分类功能"""
    try:
        # 获取token
        login_response = requests.post(f"{BASE_URL}/api/v1/auth/login", data={
            "username": "admin",
            "password": "admin123"
        })
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 获取项目2的系统分类
        response = requests.get(
            f"{BASE_URL}/api/v1/purchases/system-categories/by-project/2",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            # 检查是否返回了系统分类
            if isinstance(data, list):
                return len(data) > 0
            elif isinstance(data, dict) and "categories" in data:
                return len(data["categories"]) > 0
        return False
    except:
        return False

def test_purchase_detail():
    """测试申购单详情API"""
    try:
        # 获取token
        login_response = requests.post(f"{BASE_URL}/api/v1/auth/login", data={
            "username": "admin",
            "password": "admin123"
        })
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 先获取列表找到一个ID
        list_response = requests.get(f"{BASE_URL}/api/v1/purchases/", headers=headers)
        items = list_response.json().get("items", [])
        
        if items:
            # 获取第一个申购单的详情
            purchase_id = items[0]["id"]
            response = requests.get(
                f"{BASE_URL}/api/v1/purchases/{purchase_id}",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                # 检查是否有必要字段
                return "request_code" in data and "items" in data
        return False
    except:
        return False

def run_pytest_tests():
    """运行pytest测试套件"""
    print("\n🧪 运行pytest测试套件...")
    try:
        # 运行申购模块测试
        result = subprocess.run(
            ["python", "backend/tools/run_purchase_tests_standalone.py"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # 检查输出中是否有成功信息
        if "成功率: 100.0%" in result.stdout or "全部通过" in result.stdout:
            print("  ✅ 申购模块测试全部通过")
            return True
        else:
            print("  ⚠️  部分测试失败")
            print(result.stdout[-500:])  # 显示最后500个字符
            return False
    except subprocess.TimeoutExpired:
        print("  ⏱️  测试超时")
        return False
    except Exception as e:
        print(f"  ❌ 测试运行失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("🚀 深源ERP系统完整功能测试")
    print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 基础服务测试
    print("\n📡 基础服务测试")
    print("-" * 40)
    run_test("后端健康检查", test_backend_health)
    run_test("前端代理检查", test_frontend_proxy)
    
    # 认证系统测试
    print("\n🔐 认证系统测试")
    print("-" * 40)
    run_test("用户登录功能", test_auth_login)
    
    # 申购模块测试
    print("\n📦 申购模块测试")
    print("-" * 40)
    run_test("申购单列表API", test_purchase_list_api)
    run_test("申购单详情API", test_purchase_detail)
    run_test("申购单工作流状态", test_purchase_workflow)
    run_test("系统分类功能", test_system_categories)
    
    # 权限系统测试
    print("\n🔒 权限系统测试")
    print("-" * 40)
    run_test("项目经理权限隔离", test_project_manager_permission)
    
    # pytest测试套件
    print("\n🧪 自动化测试套件")
    print("-" * 40)
    run_test("申购模块单元测试", run_pytest_tests)
    
    # 测试结果汇总
    print("\n" + "=" * 60)
    print("📊 测试结果汇总")
    print("=" * 60)
    
    total_tests = passed_tests + failed_tests
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"✅ 通过: {passed_tests}")
    print(f"❌ 失败: {failed_tests}")
    print(f"📈 成功率: {success_rate:.1f}%")
    
    # 详细结果
    if failed_tests > 0:
        print("\n❌ 失败的测试:")
        for result in test_results:
            if result["status"] != "PASSED":
                print(f"  - {result['name']}: {result['status']}")
                if result["message"]:
                    print(f"    错误: {result['message']}")
    
    # 生成测试报告
    report_file = f"backend/test_reports/complete_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "passed": passed_tests,
            "failed": failed_tests,
            "success_rate": success_rate,
            "details": test_results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 测试报告已保存到: {report_file}")
    
    # 返回状态码
    return 0 if failed_tests == 0 else 1

if __name__ == "__main__":
    exit(main())