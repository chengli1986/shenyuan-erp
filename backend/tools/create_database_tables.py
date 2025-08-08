"""
手动创建数据库表
"""

import os
import sys
# 添加backend目录到Python路径
backend_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, backend_dir)

from app.core.database import engine, Base
from app.models import project, project_file, contract, user, purchase

def create_database_tables():
    """创建数据库表"""
    
    try:
        print("="*80)
        print("创建数据库表")
        print("="*80)
        
        print("正在导入模型...")
        print(f"  - 项目模型: {project}")
        print(f"  - 项目文件模型: {project_file}")
        print(f"  - 合同模型: {contract}")
        print(f"  - 用户模型: {user}")
        print(f"  - 采购模型: {purchase}")
        
        print("\n正在创建数据库表...")
        Base.metadata.create_all(bind=engine)
        print("[SUCCESS] 数据库表创建完成!")
        
        # 验证表是否创建成功
        print("\n验证表创建结果...")
        from sqlalchemy import inspect
        inspector = inspect(engine)
        table_names = inspector.get_table_names()
        
        print(f"创建的表数量: {len(table_names)}")
        for table_name in table_names:
            print(f"  - {table_name}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] 创建数据库表失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    create_database_tables()