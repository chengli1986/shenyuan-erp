"""
测试真实项目Excel文件的解析
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.utils.excel_parser import ContractExcelParser
from datetime import datetime
import json

def test_real_project_file(file_path: str):
    """测试真实项目文件"""
    print(f"\n{'='*80}")
    print(f"测试文件: {os.path.basename(file_path)}")
    print(f"文件路径: {file_path}")
    print(f"文件大小: {os.path.getsize(file_path) / 1024:.2f} KB")
    print(f"{'='*80}")
    
    if not os.path.exists(file_path):
        print(f"[ERROR] 文件不存在")
        return
    
    parser = ContractExcelParser()
    
    try:
        # 1. 加载文件
        print("\n1. 加载Excel文件...")
        parser.load_excel_file(file_path)
        print(f"[OK] 文件加载成功")
        print(f"[INFO] 工作表数量: {len(parser.sheet_names)}")
        print(f"[INFO] 工作表列表:")
        for i, sheet in enumerate(parser.sheet_names, 1):
            print(f"  {i}. {sheet}")
        
        # 2. 解析所有工作表
        print("\n2. 开始解析所有工作表...")
        result = parser.parse_all_sheets()
        
        # 3. 显示解析结果
        categories = result.get('categories', [])
        items = result.get('items', [])
        summary = result.get('summary', {})
        
        print(f"\n3. 解析结果汇总:")
        print(f"[INFO] 系统分类数: {len(categories)}")
        print(f"[INFO] 设备总数: {len(items)}")
        print(f"[INFO] 总金额: {summary.get('total_amount', 0):,.2f}")
        
        # 4. 按系统分类显示统计
        print(f"\n4. 系统分类统计:")
        total_by_category = 0
        for i, cat in enumerate(categories, 1):
            item_count = cat['total_items_count']
            amount = float(cat['budget_amount'])
            total_by_category += amount
            
            print(f"{i:2d}. {cat['category_name']:<20} | "
                  f"设备数: {item_count:>4} | "
                  f"金额: {amount:>12,.2f}")
        
        print(f"{'总计':>24} | "
              f"设备数: {len(items):>4} | "
              f"金额: {total_by_category:>12,.2f}")
        
        # 5. 显示解析错误（如果有）
        parse_errors = summary.get('parse_errors', [])
        if parse_errors:
            print(f"\n5. 解析警告/错误 ({len(parse_errors)}条):")
            for i, error in enumerate(parse_errors[:10], 1):  # 只显示前10条
                print(f"  {i}. {error}")
            if len(parse_errors) > 10:
                print(f"  ... 还有 {len(parse_errors) - 10} 条警告")
        
        # 6. 显示部分设备明细
        if items:
            print(f"\n6. 设备明细示例 (随机显示5个):")
            import random
            sample_items = random.sample(items, min(5, len(items)))
            
            for i, item in enumerate(sample_items, 1):
                print(f"\n  [{i}] {item.get('item_name', 'N/A')}")
                print(f"      分类: {item.get('category_name', 'N/A')}")
                print(f"      品牌型号: {item.get('brand_model', 'N/A')}")
                print(f"      规格: {item.get('specification', 'N/A')[:50]}...")
                print(f"      数量: {item.get('quantity', 0)} {item.get('unit', '')}")
                print(f"      单价: {item.get('unit_price', 0):,.2f}")
                print(f"      合价: {item.get('total_price', 0):,.2f}")
        
        # 7. 数据质量检查
        print(f"\n7. 数据质量检查:")
        # 检查缺失数据
        missing_name = sum(1 for item in items if not item.get('item_name'))
        missing_brand = sum(1 for item in items if not item.get('brand_model'))
        missing_spec = sum(1 for item in items if not item.get('specification'))
        missing_quantity = sum(1 for item in items if item.get('quantity', 0) == 0)
        missing_price = sum(1 for item in items if item.get('unit_price', 0) == 0)
        
        print(f"  - 缺少设备名称: {missing_name} 个")
        print(f"  - 缺少品牌型号: {missing_brand} 个")
        print(f"  - 缺少技术规格: {missing_spec} 个")
        print(f"  - 缺少数量: {missing_quantity} 个")
        print(f"  - 缺少单价: {missing_price} 个")
        
        # 计算数据完整率
        total_checks = len(items) * 5  # 5个关键字段
        missing_total = missing_name + missing_brand + missing_spec + missing_quantity + missing_price
        completeness = ((total_checks - missing_total) / total_checks * 100) if total_checks > 0 else 0
        print(f"\n  数据完整率: {completeness:.2f}%")
        
        print(f"\n[SUCCESS] 文件解析完成!")
        
    except Exception as e:
        print(f"\n[ERROR] 解析失败: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    """主函数"""
    print("真实项目Excel文件解析测试")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 查找Excel文件的目录列表
    search_dirs = [
        (os.path.join(os.path.dirname(__file__), 'uploads', 'contracts'), 'uploads/contracts'),
        (os.path.join(os.path.dirname(__file__), '..', 'docs'), 'docs')
    ]
    
    all_excel_files = []
    
    for dir_path, dir_name in search_dirs:
        if os.path.exists(dir_path):
            excel_files = [(os.path.join(dir_path, f), f, dir_name) 
                          for f in os.listdir(dir_path) 
                          if f.endswith(('.xlsx', '.xls')) and not f.startswith('~$')]
            all_excel_files.extend(excel_files)
            print(f"\n[INFO] 在 {dir_name} 目录找到 {len(excel_files)} 个Excel文件")
        else:
            print(f"\n[INFO] {dir_name} 目录不存在: {dir_path}")
    
    if not all_excel_files:
        print(f"\n[INFO] 没有找到任何Excel文件")
        return
    
    print(f"\n总共找到 {len(all_excel_files)} 个Excel文件:")
    for i, (_, filename, location) in enumerate(all_excel_files, 1):
        print(f"  {i}. [{location}] {filename}")
    
    # 测试每个文件
    for file_path, filename, location in all_excel_files:
        print(f"\n[测试文件来源: {location}]")
        test_real_project_file(file_path)
    
    print(f"\n{'='*80}")
    print("测试完成!")

if __name__ == "__main__":
    main()