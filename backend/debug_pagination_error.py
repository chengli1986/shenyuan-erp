"""
调试分页API错误
"""

import os
import sys
sys.path.append(os.path.dirname(__file__))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.contract import ContractItem, SystemCategory, ContractFileVersion
import math

def debug_pagination_error():
    """调试分页API错误"""
    
    # 创建数据库连接
    database_url = "sqlite:///./erp_test.db"
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    try:
        db = SessionLocal()
        
        print("=" * 80)
        print("调试分页API错误")
        print("=" * 80)
        
        # 使用API相同的查询逻辑
        project_id = 3
        version_id = 7
        
        print(f"项目ID: {project_id}, 版本ID: {version_id}")
        
        # 验证版本是否存在
        version = db.query(ContractFileVersion).filter(
            ContractFileVersion.id == version_id,
            ContractFileVersion.project_id == project_id
        ).first()
        
        if not version:
            print("[ERROR] 版本不存在")
            return
        
        print(f"版本存在: {version.original_filename}")
        
        # 构建查询 - 完全模拟API逻辑
        query = db.query(ContractItem).filter(
            ContractItem.version_id == version_id,
            ContractItem.is_active == True
        )
        
        # 计算总数
        total = query.count()
        print(f"总记录数: {total}")
        
        # 测试不同的分页参数
        test_cases = [
            (1, 20),  # 第1页，每页20条
            (2, 20),  # 第2页，每页20条  
            (3, 20),  # 第3页，每页20条
            (4, 20),  # 第4页，每页20条
            (1, 50),  # 第1页，每页50条
        ]
        
        for page, size in test_cases:
            print(f"\n测试分页: 第{page}页，每页{size}条")
            
            try:
                # 分页查询
                offset = (page - 1) * size
                print(f"  offset: {offset}, limit: {size}")
                
                items = query.offset(offset).limit(size).all()
                print(f"  返回记录数: {len(items)}")
                
                # 计算总页数
                pages = math.ceil(total / size)
                print(f"  总页数: {pages}")
                
                if items:
                    print(f"  第一条记录: {items[0].item_name[:30]}...")
                    print(f"  最后一条记录: {items[-1].item_name[:30]}...")
                
                # 模拟API响应构建
                response_data = {
                    'items': [item.to_dict() for item in items],
                    'total': total,
                    'page': page,
                    'size': size,
                    'pages': pages
                }
                
                print(f"  API响应项目数: {len(response_data['items'])}")
                
            except Exception as e:
                print(f"  [ERROR] 分页查询失败: {str(e)}")
                import traceback
                traceback.print_exc()
        
        # 特别检查数据转换
        print(f"\n检查数据转换:")
        try:
            first_item = query.first()
            if first_item:
                item_dict = first_item.to_dict()
                print(f"  第一条记录转换成功")
                print(f"  字段数量: {len(item_dict)}")
                
                # 检查可能有问题的字段
                problematic_fields = []
                for key, value in item_dict.items():
                    try:
                        # 尝试JSON序列化
                        import json
                        json.dumps(value, default=str)
                    except Exception as e:
                        problematic_fields.append((key, type(value), str(e)))
                
                if problematic_fields:
                    print(f"  [WARNING] 可能有问题的字段:")
                    for field, field_type, error in problematic_fields:
                        print(f"    {field} ({field_type}): {error}")
                else:
                    print(f"  所有字段都可以序列化")
            
        except Exception as e:
            print(f"  [ERROR] 数据转换失败: {str(e)}")
            import traceback
            traceback.print_exc()
        
        db.close()
        
    except Exception as e:
        print(f"[ERROR] 调试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_pagination_error()