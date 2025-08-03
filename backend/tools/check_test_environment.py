#!/usr/bin/env python3
"""
测试环境依赖检查脚本
在运行测试之前验证所有必需的依赖项和工具是否正确安装
"""

import os
import sys
import subprocess
import importlib
from typing import List, Dict, Tuple
import logging

try:
    import pkg_resources
except ImportError:
    pkg_resources = None

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnvironmentChecker:
    """测试环境检查器"""
    
    def __init__(self):
        self.checks_passed = 0
        self.checks_failed = 0
        self.warnings = []
        
    def run_all_checks(self) -> bool:
        """运行所有环境检查"""
        print("🔍 开始检查测试环境...")
        print("=" * 50)
        
        # 基础Python环境检查
        self._check_python_version()
        
        # 虚拟环境检查
        self._check_virtual_environment()
        
        # 必需包检查
        self._check_required_packages()
        
        # 可选包检查
        self._check_optional_packages()
        
        # 数据库连接检查
        self._check_database_connection()
        
        # 测试文件检查
        self._check_test_files()
        
        # 权限检查
        self._check_permissions()
        
        # 输出总结
        self._print_summary()
        
        return self.checks_failed == 0
    
    def _check_python_version(self):
        """检查Python版本"""
        print("📋 检查Python版本...")
        
        version = sys.version_info
        required_major = 3
        required_minor = 8
        
        if version.major >= required_major and version.minor >= required_minor:
            self._pass(f"Python版本: {version.major}.{version.minor}.{version.micro}")
        else:
            self._fail(f"Python版本过低: {version.major}.{version.minor}.{version.micro}, 需要 >= {required_major}.{required_minor}")
    
    def _check_virtual_environment(self):
        """检查虚拟环境"""
        print("\n🏠 检查虚拟环境...")
        
        # 检查是否在虚拟环境中
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            self._pass("已激活虚拟环境")
            
            # 检查虚拟环境路径
            venv_path = sys.prefix
            if 'venv' in venv_path:
                self._pass(f"虚拟环境路径: {venv_path}")
            else:
                self._warn(f"虚拟环境路径异常: {venv_path}")
        else:
            self._fail("未检测到虚拟环境，建议在虚拟环境中运行测试")
    
    def _check_required_packages(self):
        """检查必需的Python包"""
        print("\n📦 检查必需依赖包...")
        
        required_packages = [
            ('pytest', '7.0.0'),
            ('fastapi', '0.95.0'),
            ('sqlalchemy', '1.4.0'),
            ('pydantic', '1.10.0'),
            ('uvicorn', '0.20.0'),
            ('requests', '2.25.0'),
        ]
        
        for package_name, min_version in required_packages:
            self._check_package(package_name, min_version, required=True)
    
    def _check_optional_packages(self):
        """检查可选的Python包"""
        print("\n📦 检查可选依赖包...")
        
        optional_packages = [
            ('pytest-asyncio', '0.21.0'),
            ('pytest-cov', '4.0.0'),
            ('black', '22.0.0'),
            ('flake8', '5.0.0'),
        ]
        
        for package_name, min_version in optional_packages:
            self._check_package(package_name, min_version, required=False)
    
    def _check_package(self, package_name: str, min_version: str, required: bool = True):
        """检查单个包"""
        try:
            # 尝试导入包
            if package_name == 'pytest':
                import pytest
                version = pytest.__version__
            elif package_name == 'fastapi':
                import fastapi
                version = fastapi.__version__
            elif package_name == 'sqlalchemy':
                import sqlalchemy
                version = sqlalchemy.__version__
            elif package_name == 'pydantic':
                import pydantic
                version = pydantic.VERSION
            elif package_name == 'uvicorn':
                import uvicorn
                version = uvicorn.__version__
            elif package_name == 'requests':
                import requests
                version = requests.__version__
            else:
                # 对于其他包，尝试使用pkg_resources
                try:
                    if pkg_resources:
                        distribution = pkg_resources.get_distribution(package_name)
                        version = distribution.version
                    else:
                        version = "unknown"
                except (Exception, AttributeError):
                    if required:
                        self._fail(f"{package_name}: 未安装")
                    else:
                        self._warn(f"{package_name}: 未安装（可选）")
                    return
            
            # 检查版本
            if self._compare_versions(version, min_version):
                self._pass(f"{package_name}: {version}")
            else:
                msg = f"{package_name}: 版本过低 ({version} < {min_version})"
                if required:
                    self._fail(msg)
                else:
                    self._warn(msg)
                    
        except ImportError:
            msg = f"{package_name}: 导入失败"
            if required:
                self._fail(msg)
            else:
                self._warn(msg)
        except Exception as e:
            msg = f"{package_name}: 检查异常 - {str(e)}"
            if required:
                self._fail(msg)
            else:
                self._warn(msg)
    
    def _check_database_connection(self):
        """检查数据库连接"""
        print("\n🗄️ 检查数据库连接...")
        
        try:
            # 尝试连接到测试数据库
            backend_path = os.path.dirname(os.path.dirname(__file__))
            sys.path.insert(0, backend_path)
            
            from app.core.database import engine
            
            # 尝试连接
            from sqlalchemy import text
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1")).fetchone()
                if result:
                    self._pass("数据库连接正常")
                else:
                    self._fail("数据库连接异常")
                    
        except Exception as e:
            self._fail(f"数据库连接失败: {str(e)}")
    
    def _check_test_files(self):
        """检查测试文件"""
        print("\n📁 检查测试文件...")
        
        backend_path = os.path.dirname(os.path.dirname(__file__))
        
        # 检查测试目录
        test_dirs = [
            os.path.join(backend_path, 'tests'),
            os.path.join(backend_path, 'tests', 'unit'),
            os.path.join(backend_path, 'tests', 'integration'),
        ]
        
        for test_dir in test_dirs:
            if os.path.exists(test_dir):
                test_files = [f for f in os.listdir(test_dir) if f.startswith('test_') and f.endswith('.py')]
                if test_files:
                    self._pass(f"{os.path.basename(test_dir)}目录: {len(test_files)}个测试文件")
                else:
                    self._warn(f"{os.path.basename(test_dir)}目录: 无测试文件")
            else:
                self._fail(f"测试目录不存在: {test_dir}")
    
    def _check_permissions(self):
        """检查文件权限"""
        print("\n🔐 检查文件权限...")
        
        backend_path = os.path.dirname(os.path.dirname(__file__))
        
        # 检查关键目录的读写权限
        key_paths = [
            backend_path,
            os.path.join(backend_path, 'tests'),
            os.path.join(backend_path, 'app'),
        ]
        
        for path in key_paths:
            if os.path.exists(path):
                if os.access(path, os.R_OK | os.W_OK):
                    self._pass(f"权限正常: {os.path.basename(path)}")
                else:
                    self._fail(f"权限不足: {path}")
            else:
                self._fail(f"路径不存在: {path}")
    
    def _compare_versions(self, current: str, required: str) -> bool:
        """比较版本号"""
        try:
            from packaging import version
            return version.parse(current) >= version.parse(required)
        except ImportError:
            # 简单的版本比较
            current_parts = [int(x) for x in current.split('.')]
            required_parts = [int(x) for x in required.split('.')]
            
            # 补齐长度
            max_len = max(len(current_parts), len(required_parts))
            current_parts.extend([0] * (max_len - len(current_parts)))
            required_parts.extend([0] * (max_len - len(required_parts)))
            
            return current_parts >= required_parts
    
    def _pass(self, message: str):
        """记录通过的检查"""
        print(f"  ✅ {message}")
        self.checks_passed += 1
    
    def _fail(self, message: str):
        """记录失败的检查"""
        print(f"  ❌ {message}")
        self.checks_failed += 1
    
    def _warn(self, message: str):
        """记录警告"""
        print(f"  ⚠️  {message}")
        self.warnings.append(message)
    
    def _print_summary(self):
        """打印检查总结"""
        print("\n" + "=" * 50)
        print("📊 环境检查总结")
        print("=" * 50)
        
        print(f"✅ 通过: {self.checks_passed}")
        print(f"❌ 失败: {self.checks_failed}")
        print(f"⚠️  警告: {len(self.warnings)}")
        
        if self.checks_failed == 0:
            print("\n🎉 环境检查通过！可以安全运行测试。")
        else:
            print("\n🚨 环境检查失败！请修复上述问题后再运行测试。")
            
        if self.warnings:
            print("\n⚠️  警告详情:")
            for warning in self.warnings:
                print(f"  - {warning}")


def main():
    """主函数"""
    checker = EnvironmentChecker()
    success = checker.run_all_checks()
    
    # 返回适当的退出码
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()