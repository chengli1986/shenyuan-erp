"""
测试修复后的Excel解析功能
验证新的表头格式和字段映射
"""

import os
import sys
sys.path.append(os.path.dirname(__file__))

from app.utils.excel_parser import ContractExcelParser

def test_new_excel_format():
    """测试新Excel格式的解析"""
    
    # 使用我们创建的新模板
    excel_file = os.path.join(os.path.dirname(__file__), 'templates', '合同清单-完整版含两个系统-表头修正版.xlsx')
    
    if not os.path.exists(excel_file):
        print(f"❌ 测试文件不存在: {excel_file}")
        return
    
    try:
        # 初始化解析器
        parser = ContractExcelParser()
        
        # 加载Excel文件
        print(f"加载Excel文件: {os.path.basename(excel_file)}")
        parser.load_excel_file(excel_file)
        
        # 解析所有工作表
        print(f"开始解析工作表...")
        parsed_data = parser.parse_all_sheets()
        
        print(f"\n解析结果汇总:")
        print(f"  - 工作表数量: {len(parser.sheet_names)}")
        print(f"  - 工作表列表: {parser.sheet_names}")
        print(f"  - 系统分类数: {len(parsed_data.get('categories', []))}")
        print(f"  - 设备明细数: {len(parsed_data.get('items', []))}")
        
        # 验证系统分类
        print(f"\n系统分类详情:")
        for category in parsed_data.get('categories', []):
            print(f"  - {category['category_name']}: {category['total_items_count']} 项设备")
        
        # 验证前几个设备的字段映射
        print(f"\n设备字段映射验证（前5项）:")
        items = parsed_data.get('items', [])
        for i, item in enumerate(items[:5]):
            print(f"\n  第{i+1}项设备:")
            print(f"    设备名称: {item.get('item_name', 'N/A')}")
            print(f"    设备品牌: {item.get('brand_model', 'N/A')}")  # 应该显示品牌
            print(f"    设备型号: {item.get('specification', 'N/A')}")  # 应该显示型号
            print(f"    单位: {item.get('unit', 'N/A')}")
            print(f"    数量: {item.get('quantity', 'N/A')}")
            print(f"    单价: {item.get('unit_price', 'N/A')}")
            print(f"    备注: {item.get('remarks', 'N/A')}")
            print(f"    所属系统: {item.get('category_name', 'N/A')}")
        
        # 验证分页数据
        total_items = len(items)
        print(f"\n分页验证:")
        print(f"  - 总设备数: {total_items}")
        
        # 模拟分页
        page_size = 20
        total_pages = (total_items + page_size - 1) // page_size
        print(f"  - 每页显示: {page_size} 项")
        print(f"  - 总页数: {total_pages}")
        
        for page in range(1, min(4, total_pages + 1)):  # 只显示前3页
            start_idx = (page - 1) * page_size
            end_idx = min(start_idx + page_size, total_items)
            page_items = items[start_idx:end_idx]
            print(f"  - 第{page}页: 第{start_idx+1}-{end_idx}项 ({len(page_items)}项)")
        
        print(f"\n[SUCCESS] Excel解析测试完成!")
        
        return parsed_data
        
    except Exception as e:
        print(f"[ERROR] 解析失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def verify_field_mapping():
    """验证字段映射是否正确"""
    
    print(f"\n验证字段映射:")
    
    # 测试映射
    test_mappings = [
        ('设备品牌', 'brand_model'),
        ('设备型号', 'specification'),
        ('综合单价', 'unit_price'),
        ('合价', 'total_price'),
        ('备注', 'remarks')
    ]
    
    parser = ContractExcelParser()
    
    for excel_header, expected_field in test_mappings:
        mapped_field = parser._normalize_column_name(excel_header)
        status = "[OK]" if mapped_field == expected_field else "[ERROR]"
        print(f"  {status} '{excel_header}' -> '{mapped_field}' (期望: '{expected_field}')")

if __name__ == "__main__":
    print("="*80)
    print("测试修复后的Excel解析功能")
    print("="*80)
    
    # 验证字段映射
    verify_field_mapping()
    
    # 测试Excel解析
    test_new_excel_format()
    
    print(f"\n测试说明:")
    print("1. 验证新表头格式：设备品牌、设备型号、综合单价、合价、备注")
    print("2. 确认字段正确映射到数据库字段")
    print("3. 验证分页功能的数据基础")
    print("4. 检查双工作表解析")