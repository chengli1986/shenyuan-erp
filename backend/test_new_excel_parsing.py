# 测试新Excel文件的解析过程
from app.utils.excel_parser import ContractExcelParser
import os

def test_new_excel_parsing():
    """测试新Excel文件的详细解析过程"""
    
    file_path = "../docs/【体育局】供应商询价清单（含价格）.xlsx"
    
    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}")
        return
    
    print("=== 测试新Excel文件解析 ===")
    
    try:
        parser = ContractExcelParser()
        
        # 加载文件
        print("1. 加载Excel文件...")
        success = parser.load_excel_file(file_path)
        print(f"   加载成功: {success}")
        print(f"   工作表数量: {len(parser.sheet_names)}")
        print(f"   前10个工作表: {parser.sheet_names[:10]}")
        
        # 测试解析单个工作表
        print("\n2. 测试解析单个工作表...")
        test_sheets = ["视频监控", "门禁对讲", "安防报警"]
        
        for sheet_name in test_sheets:
            if sheet_name in parser.sheet_names:
                print(f"\n--- 解析工作表: {sheet_name} ---")
                try:
                    sheet_result = parser.parse_sheet_data(sheet_name)
                    print(f"   解析成功!")
                    print(f"   表头行: {sheet_result['header_row']}")
                    print(f"   总行数: {sheet_result['total_rows']}")
                    print(f"   解析出的设备数: {len(sheet_result['items'])}")
                    
                    if sheet_result['items']:
                        print("   前3个设备:")
                        for i, item in enumerate(sheet_result['items'][:3], 1):
                            print(f"     {i}. {item.get('item_name', 'N/A')}")
                            print(f"        数量: {item.get('quantity', 'N/A')}")
                            print(f"        品牌: {item.get('brand_model', 'N/A')}")
                    else:
                        print("   ❌ 没有解析出任何设备!")
                        
                except Exception as e:
                    print(f"   ❌ 解析失败: {str(e)}")
                    import traceback
                    traceback.print_exc()
        
        # 测试完整解析
        print("\n3. 测试完整解析所有工作表...")
        try:
            result = parser.parse_all_sheets()
            
            print(f"解析完成!")
            print(f"总工作表数: {result['summary']['total_sheets']}")
            print(f"解析出的分类数: {len(result['categories'])}")
            print(f"解析出的总设备数: {len(result['items'])}")
            
            # 显示每个分类的设备数量
            print("\n各分类设备数量:")
            for category in result['categories']:
                items_in_category = [item for item in result['items'] 
                                   if item.get('category_name') == category['category_name']]
                print(f"  {category['category_name']}: {len(items_in_category)}个设备")
            
            # 显示解析错误
            if result['summary'].get('parse_errors'):
                print(f"\n解析错误 ({len(result['summary']['parse_errors'])}个):")
                for error in result['summary']['parse_errors'][:5]:  # 只显示前5个
                    print(f"  - {error}")
            
        except Exception as e:
            print(f"❌ 完整解析失败: {str(e)}")
            import traceback
            traceback.print_exc()
            
        parser.close()
        
    except Exception as e:
        print(f"测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_new_excel_parsing()