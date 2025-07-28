"""
调试Excel列映射过程
"""

import os
import sys
sys.path.append(os.path.dirname(__file__))

from app.utils.excel_parser import ContractExcelParser
import pandas as pd

def debug_column_mapping():
    """调试列映射过程"""
    
    excel_file = os.path.join(os.path.dirname(__file__), 'templates', '合同清单-完整版含两个系统-表头修正版.xlsx')
    
    if not os.path.exists(excel_file):
        print(f"[ERROR] Excel文件不存在: {excel_file}")
        return
    
    try:
        parser = ContractExcelParser()
        parser.load_excel_file(excel_file)
        
        print("="*80)
        print("Excel列映射调试")
        print("="*80)
        
        # 检查视频监控工作表
        sheet_name = '视频监控'
        worksheet = parser.workbook[sheet_name]
        
        print(f"\n工作表: {sheet_name}")
        
        # 检测表头行
        header_row = parser.detect_header_row(worksheet)
        print(f"检测到的表头行: {header_row}")
        
        # 获取表头
        headers = []
        for col in range(1, 10):
            header_value = worksheet.cell(row=header_row, column=col).value
            if header_value:
                headers.append(str(header_value).strip())
            else:
                headers.append('')
        
        print(f"原始表头: {headers}")
        
        # 映射表头到标准字段名
        print(f"\n列映射过程:")
        mapped_columns = {}
        for i, header in enumerate(headers):
            if header:
                normalized_name = parser._normalize_column_name(header)
                mapped_columns[i] = {
                    '原始表头': header,
                    '映射字段': normalized_name,
                    '列索引': i
                }
                print(f"  第{i+1}列: '{header}' -> '{normalized_name}'")
        
        # 读取为DataFrame
        print(f"\n转换为DataFrame:")
        df = pd.read_excel(excel_file, sheet_name=sheet_name, header=header_row-1)
        print(f"DataFrame列名: {list(df.columns)}")
        
        # 重命名列名
        renamed_columns = {}
        for col in df.columns:
            normalized = parser._normalize_column_name(str(col))
            renamed_columns[col] = normalized
            print(f"  重命名: '{col}' -> '{normalized}'")
        
        df = df.rename(columns=renamed_columns)
        print(f"重命名后的列名: {list(df.columns)}")
        
        # 检查第一行数据
        print(f"\n第一行数据:")
        if len(df) > 0:
            first_row = df.iloc[0]
            for field_name in ['item_name', 'brand_model', 'specification', 'unit', 'quantity', 'unit_price', 'remarks']:
                if field_name in first_row.index:
                    value = first_row[field_name]
                    print(f"  {field_name}: '{value}'")
                else:
                    print(f"  {field_name}: [字段不存在]")
        
    except Exception as e:
        print(f"[ERROR] 调试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_column_mapping()