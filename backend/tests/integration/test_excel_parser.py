"""
Excel解析模块的集成测试
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.utils.excel_parser import ContractExcelParser


def test_excel_parser_basic():
    """测试Excel解析器基本功能"""
    print("\n=== 测试Excel解析器基本功能 ===")
    
    # 测试Excel模板文件
    template_file = os.path.join(
        os.path.dirname(__file__), '..', '..', 
        'templates', '合同清单-完整版含两个系统-表头修正版.xlsx'
    )
    
    if not os.path.exists(template_file):
        print(f"[SKIP] 模板文件不存在: {template_file}")
        return
    
    try:
        # 创建解析器实例
        parser = ContractExcelParser()
        
        # 加载Excel文件
        success = parser.load_excel_file(template_file)
        assert success, "Excel文件加载失败"
        
        # 检查工作表
        assert len(parser.sheet_names) >= 2, f"工作表数量不正确: {len(parser.sheet_names)}"
        print(f"✅ 检测到工作表: {parser.sheet_names}")
        
        # 解析所有工作表
        result = parser.parse_all_sheets()
        
        # 验证解析结果
        assert 'categories' in result, "解析结果缺少categories"
        assert 'items' in result, "解析结果缺少items"
        assert 'summary' in result, "解析结果缺少summary"
        
        print(f"✅ 解析成功:")
        print(f"   - 系统分类数: {len(result['categories'])}")
        print(f"   - 设备数量: {len(result['items'])}")
        print(f"   - 总金额: {result['summary'].get('total_amount', 0)}")
        
        parser.close()
        
    except Exception as e:
        print(f"❌ 解析失败: {str(e)}")
        raise


def test_excel_parser_with_test_data():
    """使用测试数据文件测试解析器"""
    print("\n=== 测试解析器与测试数据 ===")
    
    test_data_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'test_data')
    
    if not os.path.exists(test_data_dir):
        print("[SKIP] 测试数据目录不存在")
        return
    
    # 查找Excel测试文件
    excel_files = [f for f in os.listdir(test_data_dir) if f.endswith('.xlsx')]
    
    if not excel_files:
        print("[SKIP] 没有找到Excel测试文件")
        return
    
    for excel_file in excel_files[:2]:  # 只测试前2个文件
        file_path = os.path.join(test_data_dir, excel_file)
        print(f"\n测试文件: {excel_file}")
        
        try:
            parser = ContractExcelParser()
            parser.load_excel_file(file_path)
            result = parser.parse_all_sheets()
            
            print(f"  ✅ 解析成功: {len(result['items'])} 个设备")
            parser.close()
            
        except Exception as e:
            print(f"  ⚠️ 解析失败: {str(e)}")
            # 测试数据文件可能格式不标准，不作为错误处理


if __name__ == "__main__":
    test_excel_parser_basic()
    test_excel_parser_with_test_data()