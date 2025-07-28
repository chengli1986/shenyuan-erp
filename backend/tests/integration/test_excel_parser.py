"""
Excel解析模块的测试脚本
用于测试各种格式的Excel文件解析功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.utils.excel_parser import ContractExcelParser
import pandas as pd
from datetime import datetime

def test_parser_with_file(file_path: str, test_name: str):
    """测试单个Excel文件的解析"""
    print(f"\n{'='*60}")
    print(f"测试: {test_name}")
    print(f"文件: {file_path}")
    print(f"{'='*60}")
    
    if not os.path.exists(file_path):
        print(f"[ERROR] 文件不存在: {file_path}")
        return False
    
    parser = ContractExcelParser()
    
    try:
        # 1. 测试读取Excel文件
        print("\n1. 读取Excel文件...")
        success = parser.load_excel_file(file_path)
        if not success:
            print("[FAIL] 无法读取Excel文件")
            return False
        print("[OK] Excel文件读取成功")
        
        # 2. 获取所有sheet名称
        print("\n2. 获取sheet信息...")
        sheet_names = parser.sheet_names
        print(f"[INFO] 找到 {len(sheet_names)} 个sheet: {sheet_names}")
        
        # 3. 解析所有sheets
        print("\n3. 解析所有sheets...")
        result = parser.parse_all_sheets()
        
        # 显示解析结果
        categories = result.get('categories', [])
        items = result.get('items', [])
        summary = result.get('summary', {})
        
        print(f"\n[INFO] 解析完成:")
        print(f"  - 分类数: {len(categories)}")
        print(f"  - 设备数: {len(items)}")
        print(f"  - 总金额: {summary.get('total_amount', 0)}")
        
        # 显示每个分类的信息
        if categories:
            print(f"\n[INFO] 系统分类:")
            for cat in categories:
                print(f"  - {cat['category_name']}: {cat['total_items_count']} 个设备, "
                      f"金额: {cat['budget_amount']}")
        
        # 显示前3个设备的信息
        if items:
            print(f"\n[INFO] 设备明细 (前3个):")
            for i, item in enumerate(items[:3], 1):
                print(f"  {i}. {item.get('item_name', 'N/A')} - "
                      f"数量: {item.get('quantity', 0)} - "
                      f"单价: {item.get('unit_price', 0)}")
            if len(items) > 3:
                print(f"  ... 还有 {len(items)-3} 个设备")
        
        # 显示解析错误（如果有）
        parse_errors = summary.get('parse_errors', [])
        if parse_errors:
            print(f"\n[WARNING] 解析错误:")
            for error in parse_errors:
                print(f"  - {error}")
        
        print(f"\n[SUCCESS] 测试通过!")
        return True
        
    except Exception as e:
        print(f"\n[ERROR] 解析失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def run_all_tests():
    """运行所有测试"""
    test_data_dir = os.path.join(os.path.dirname(__file__), 'test_data')
    
    # 测试用例列表
    test_cases = [
        ('test_minimal.xlsx', '最小化Excel测试'),
        ('test_simple_single_sheet.xlsx', '简单单sheet测试'),
        ('test_multi_sheet.xlsx', '多sheet测试'),
        ('test_empty_cells.xlsx', '包含空单元格测试'),
        ('test_complex_format.xlsx', '复杂格式测试'),
    ]
    
    print(f"开始运行Excel解析器测试")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    for filename, test_name in test_cases:
        file_path = os.path.join(test_data_dir, filename)
        success = test_parser_with_file(file_path, test_name)
        results.append((test_name, success))
    
    # 显示测试结果汇总
    print(f"\n{'='*60}")
    print("测试结果汇总:")
    print(f"{'='*60}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "[PASS]" if success else "[FAIL]"
        print(f"{status} {test_name}")
    
    print(f"\n总计: {passed}/{total} 通过")
    
    # 测试真实的项目Excel文件（如果存在）
    print(f"\n{'='*60}")
    print("测试真实项目文件:")
    print(f"{'='*60}")
    
    real_files = [
        '体育综合体弱电清单汇总表（设计版） - 加价版.xlsx',
        '【体育局】供应商询价清单（含价格）.xlsx'
    ]
    
    uploads_dir = os.path.join(os.path.dirname(__file__), '..', 'uploads')
    for filename in real_files:
        file_path = os.path.join(uploads_dir, filename)
        if os.path.exists(file_path):
            test_parser_with_file(file_path, f"真实项目文件: {filename}")
        else:
            print(f"\n[INFO] 跳过不存在的文件: {filename}")

if __name__ == "__main__":
    run_all_tests()