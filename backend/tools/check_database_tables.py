"""
检查数据库表结构
"""

import sqlite3
import os

def check_database_tables():
    """检查数据库表结构"""
    
    db_path = os.path.join(os.path.dirname(__file__), '..', 'erp_test.db')
    
    if not os.path.exists(db_path):
        print(f"[ERROR] 数据库文件不存在: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取所有表名
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print("="*80)
        print("数据库表结构检查")
        print("="*80)
        print(f"数据库文件: {db_path}")
        print(f"文件大小: {os.path.getsize(db_path)} 字节")
        
        print(f"\n现有表列表:")
        for table in tables:
            table_name = table[0]
            print(f"  - {table_name}")
            
            # 获取表结构
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            # 获取记录数
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            count = cursor.fetchone()[0]
            
            print(f"    记录数: {count}")
            print(f"    字段: {len(columns)} 个")
            
            # 如果是合同相关表，显示详细信息
            if 'contract' in table_name.lower():
                print(f"    详细结构:")
                for col in columns:
                    print(f"      {col[1]} ({col[2]})")
                
                # 显示一些样本数据
                if count > 0:
                    cursor.execute(f"SELECT * FROM {table_name} LIMIT 3;")
                    sample_data = cursor.fetchall()
                    print(f"    样本数据 (前3条):")
                    for i, row in enumerate(sample_data, 1):
                        print(f"      第{i}条: {row[:5]}...")  # 只显示前5个字段
        
        conn.close()
        
    except Exception as e:
        print(f"[ERROR] 检查数据库失败: {str(e)}")

if __name__ == "__main__":
    check_database_tables()