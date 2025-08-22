#!/usr/bin/env python3
"""
清理根目录下的临时测试文件
将有用的文件移动到合适的位置
"""
import os
import shutil
from pathlib import Path

# 定义根目录
ROOT_DIR = Path("/home/ubuntu/shenyuan-erp")

# 要移动到backend/tests/manual的文件（手动测试脚本）
MANUAL_TEST_FILES = [
    "test_array_fix.py",
    "test_quote_fix.py", 
    "test_edit_functionality.py",
    "test_system_category_api.py",
    "test_system_category_creation.py",
    "validate_edit_functionality.py",
    "verify_system_category_fix.py",
]

# 要移动到backend/tools的文件（测试数据创建工具）
TEST_DATA_TOOLS = [
    "create_api_test_data.py",
    "create_test_purchases.py", 
    "create_workflow_test_data.py",
    "fix_historical_system_categories.py",
]

# 要移动到backend/tests/fixtures的文件（测试数据文件）
TEST_DATA_FILES = [
    "test_edit_data.json",
    "test_simple_edit.json",
]

# 要移动到frontend/public/debug的文件（调试HTML）
DEBUG_HTML_FILES = [
    "test_edit_save.html",
]

# 要删除的临时文件（已经没有用了）
FILES_TO_DELETE = [
    "commit_message.txt",  # commit message已经用过了
    "erp_test.db",  # 测试数据库文件（backend里有）
]

def create_directories():
    """创建必要的目录"""
    directories = [
        ROOT_DIR / "backend" / "tests" / "manual",
        ROOT_DIR / "backend" / "tests" / "fixtures",
        ROOT_DIR / "frontend" / "public" / "debug",
    ]
    for dir in directories:
        dir.mkdir(parents=True, exist_ok=True)
        print(f"✅ 确保目录存在: {dir}")

def move_files():
    """移动文件到合适的位置"""
    moved_count = 0
    
    # 移动手动测试脚本
    for file in MANUAL_TEST_FILES:
        src = ROOT_DIR / file
        dst = ROOT_DIR / "backend" / "tests" / "manual" / file
        if src.exists():
            shutil.move(str(src), str(dst))
            print(f"📦 移动: {file} -> backend/tests/manual/")
            moved_count += 1
    
    # 移动测试数据创建工具
    for file in TEST_DATA_TOOLS:
        src = ROOT_DIR / file
        dst = ROOT_DIR / "backend" / "tools" / file
        if src.exists():
            shutil.move(str(src), str(dst))
            print(f"📦 移动: {file} -> backend/tools/")
            moved_count += 1
    
    # 移动测试数据文件
    for file in TEST_DATA_FILES:
        src = ROOT_DIR / file
        dst = ROOT_DIR / "backend" / "tests" / "fixtures" / file
        if src.exists():
            shutil.move(str(src), str(dst))
            print(f"📦 移动: {file} -> backend/tests/fixtures/")
            moved_count += 1
    
    # 移动调试HTML文件
    for file in DEBUG_HTML_FILES:
        src = ROOT_DIR / file
        dst = ROOT_DIR / "frontend" / "public" / "debug" / file
        if src.exists():
            shutil.move(str(src), str(dst))
            print(f"📦 移动: {file} -> frontend/public/debug/")
            moved_count += 1
    
    return moved_count

def delete_temp_files():
    """删除不需要的临时文件"""
    deleted_count = 0
    
    for file in FILES_TO_DELETE:
        file_path = ROOT_DIR / file
        if file_path.exists():
            os.remove(file_path)
            print(f"🗑️  删除: {file}")
            deleted_count += 1
    
    return deleted_count

def main():
    """主函数"""
    print("🧹 开始清理根目录文件...")
    print("=" * 50)
    
    # 创建必要的目录
    create_directories()
    print()
    
    # 移动文件
    print("📂 移动文件到合适位置...")
    moved_count = move_files()
    print(f"✅ 共移动 {moved_count} 个文件")
    print()
    
    # 删除临时文件
    print("🗑️  删除临时文件...")
    deleted_count = delete_temp_files()
    print(f"✅ 共删除 {deleted_count} 个文件")
    print()
    
    print("=" * 50)
    print("✨ 清理完成！")
    print(f"📊 统计: 移动 {moved_count} 个文件, 删除 {deleted_count} 个文件")
    
    # 显示根目录剩余的Python文件
    remaining_py_files = list(ROOT_DIR.glob("*.py"))
    if remaining_py_files:
        print("\n⚠️  根目录仍有以下Python文件（可能需要手动检查）:")
        for file in remaining_py_files:
            print(f"  - {file.name}")

if __name__ == "__main__":
    main()