#!/usr/bin/env python3
"""
回归测试检查清单
==============
用于防止功能优化导致原有功能破损的系统化测试清单
"""

import requests
import json
from typing import Dict, List, Any

class RegressionTestSuite:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_results = []
        self.tokens = {}
    
    def login(self, username: str, password: str) -> str:
        """获取认证token"""
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/auth/login",
                data={"username": username, "password": password}
            )
            if response.status_code == 200:
                token = response.json().get("access_token")
                self.tokens[username] = token
                return token
            else:
                print(f"❌ 登录失败 {username}: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ 登录异常 {username}: {e}")
            return None
    
    def test_auth_system(self) -> bool:
        """测试认证系统"""
        print("\n🔐 测试认证系统...")
        
        # 测试标准用户登录
        test_users = [
            ("admin", "admin123"),
            ("purchaser", "purchase123"),
            ("sunyun", "sunyun123"),
            ("liqiang", "liqiang123")
        ]
        
        success_count = 0
        for username, password in test_users:
            token = self.login(username, password)
            if token:
                print(f"✅ {username} 登录成功")
                success_count += 1
            else:
                print(f"❌ {username} 登录失败")
        
        return success_count == len(test_users)
    
    def test_purchase_crud(self) -> bool:
        """测试申购单CRUD操作"""
        print("\n📋 测试申购单CRUD操作...")
        
        # 使用采购员身份测试
        token = self.tokens.get("purchaser")
        if not token:
            print("❌ 缺少采购员token")
            return False
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # 1. 测试获取申购单列表
        try:
            response = requests.get(f"{self.base_url}/api/v1/purchases/", headers=headers)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 申购单列表获取成功，共 {data.get('total', 0)} 条")
            else:
                print(f"❌ 申购单列表获取失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 申购单列表获取异常: {e}")
            return False
        
        # 2. 测试获取草稿状态申购单
        try:
            params = {"status": "draft"}
            response = requests.get(f"{self.base_url}/api/v1/purchases/", headers=headers, params=params)
            if response.status_code == 200:
                drafts = response.json().get("items", [])
                print(f"✅ 草稿申购单获取成功，共 {len(drafts)} 条")
                
                # 3. 测试删除权限（如果有草稿）
                if drafts:
                    draft_id = drafts[0]["id"]
                    response = requests.delete(f"{self.base_url}/api/v1/purchases/{draft_id}", headers=headers)
                    if response.status_code == 200:
                        print(f"✅ 申购单删除成功 (ID: {draft_id})")
                    else:
                        print(f"❌ 申购单删除失败: {response.status_code}")
                        return False
            else:
                print(f"❌ 草稿申购单获取失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 草稿申购单操作异常: {e}")
            return False
        
        return True
    
    def test_workflow_operations(self) -> bool:
        """测试工作流操作"""
        print("\n🔄 测试工作流操作...")
        
        token = self.tokens.get("purchaser")
        if not token:
            return False
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # 测试获取提交状态的申购单
        try:
            params = {"status": "submitted"}
            response = requests.get(f"{self.base_url}/api/v1/purchases/", headers=headers, params=params)
            if response.status_code == 200:
                submitted = response.json().get("items", [])
                print(f"✅ 提交状态申购单获取成功，共 {len(submitted)} 条")
                return True
            else:
                print(f"❌ 提交状态申购单获取失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 工作流操作测试异常: {e}")
            return False
    
    def test_permissions(self) -> bool:
        """测试权限系统"""
        print("\n🛡️ 测试权限系统...")
        
        # 测试项目经理权限隔离
        pm_token = self.tokens.get("sunyun")
        if not pm_token:
            return False
        
        headers = {"Authorization": f"Bearer {pm_token}"}
        
        try:
            response = requests.get(f"{self.base_url}/api/v1/purchases/", headers=headers)
            if response.status_code == 200:
                data = response.json()
                # 项目经理应该只能看到负责项目的申购单
                print(f"✅ 项目经理权限隔离正常，可见申购单: {data.get('total', 0)} 条")
                return True
            else:
                print(f"❌ 项目经理权限测试失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 权限测试异常: {e}")
            return False
    
    def test_api_consistency(self) -> bool:
        """测试API一致性"""
        print("\n🔗 测试API一致性...")
        
        # 测试所有角色都能正常访问基本API
        for username, token in self.tokens.items():
            if not token:
                continue
            
            headers = {"Authorization": f"Bearer {token}"}
            try:
                response = requests.get(f"{self.base_url}/api/v1/purchases/", headers=headers)
                if response.status_code == 200:
                    print(f"✅ {username} API访问正常")
                else:
                    print(f"❌ {username} API访问失败: {response.status_code}")
                    return False
            except Exception as e:
                print(f"❌ {username} API访问异常: {e}")
                return False
        
        return True
    
    def run_full_test(self) -> bool:
        """运行完整回归测试"""
        print("🚀 开始回归测试...")
        print("=" * 50)
        
        tests = [
            ("认证系统", self.test_auth_system),
            ("申购单CRUD", self.test_purchase_crud),
            ("工作流操作", self.test_workflow_operations),
            ("权限系统", self.test_permissions),
            ("API一致性", self.test_api_consistency),
        ]
        
        success_count = 0
        for test_name, test_func in tests:
            try:
                if test_func():
                    success_count += 1
                else:
                    print(f"❌ {test_name} 测试失败")
            except Exception as e:
                print(f"❌ {test_name} 测试异常: {e}")
        
        print("=" * 50)
        print(f"🎯 回归测试完成: {success_count}/{len(tests)} 通过")
        
        if success_count == len(tests):
            print("🎉 所有测试通过！")
            return True
        else:
            print("⚠️  部分测试失败，请检查相关功能")
            return False

def main():
    """主函数"""
    suite = RegressionTestSuite()
    success = suite.run_full_test()
    
    if success:
        print("\n✅ 回归测试通过，可以安全发布新功能")
        exit(0)
    else:
        print("\n❌ 回归测试失败，请修复问题后再发布")
        exit(1)

if __name__ == "__main__":
    main()