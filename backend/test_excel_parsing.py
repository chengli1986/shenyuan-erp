# 测试Excel解析过程
from app.utils.excel_parser import ContractExcelParser
import os

def test_excel_parsing():
    """测试Excel解析过程"""
    
    file_path = "../docs/体育局投标清单.xlsx"
    
    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}")
        return
    
    print("=== 测试Excel解析过程 ===")
    
    try:
        # 创建解析器
        parser = ContractExcelParser()
        
        # 加载文件
        print("1. 加载Excel文件...")
        success = parser.load_excel_file(file_path)
        print(f"   加载结果: {success}")
        print(f"   工作表数量: {len(parser.sheet_names)}")
        print(f"   工作表列表: {parser.sheet_names}")
        
        # 解析所有sheet
        print("\n2. 解析所有工作表...")
        result = parser.parse_all_sheets()
        
        print(f"\n=== 解析结果汇总 ===")
        print(f"总工作表数: {result['summary']['total_sheets']}")
        print(f"解析出的分类数: {len(result['categories'])}")
        print(f"解析出的设备数: {len(result['items'])}")
        print(f"总金额: {result['summary']['total_amount']}")
        
        print(f"\n=== 系统分类详情 ===")
        for i, category in enumerate(result['categories'], 1):
            print(f"{i}. {category['category_name']}")
            print(f"   - 分类代码: {category['category_code']}")
            print(f"   - 设备数量: {category['total_items_count']}")
            print(f"   - 预算金额: {category.get('budget_amount', 0)}")
        
        print(f"\n=== 设备明细样例（前5个）===")
        for i, item in enumerate(result['items'][:5], 1):
            print(f"{i}. {item['item_name']}")
            print(f"   - 品牌型号: {item.get('brand_model', 'N/A')}")
            print(f"   - 数量: {item.get('quantity', 'N/A')}")
            print(f"   - 单价: {item.get('unit_price', 'N/A')}")
            print(f"   - 分类: {item.get('category_name', 'N/A')}")
        
        # 检查是否有解析错误
        if result['summary'].get('parse_errors'):
            print(f"\n=== 解析错误 ===")
            for error in result['summary']['parse_errors']:
                print(f"- {error}")
        
        print(f"\n=== 验证与数据库对比 ===")
        print(f"解析器结果: {len(result['items'])} 个设备")
        print(f"数据库实际: 869 个设备")
        
        if len(result['items']) != 869:
            print("⚠️  数量不匹配，可能有数据丢失或重复!")
        else:
            print("✅ 数量匹配")
            
        parser.close()
        
    except Exception as e:
        print(f"测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_excel_parsing()