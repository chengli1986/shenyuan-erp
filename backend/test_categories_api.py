# 测试categories API
import sys
import traceback
from app.core.database import get_db
from app.models.contract import SystemCategory

def test_categories_api():
    """测试categories API的逻辑"""
    print("=== 测试categories API ===")
    
    project_id = 3
    version_id = 5
    
    try:
        # 获取数据库会话
        db = next(get_db())
        
        print(f"查询项目{project_id}版本{version_id}的分类...")
        
        categories = db.query(SystemCategory).filter(
            SystemCategory.project_id == project_id,
            SystemCategory.version_id == version_id
        ).all()
        
        print(f"找到 {len(categories)} 个分类")
        
        # 转换为响应格式
        result = []
        for i, category in enumerate(categories[:3], 1):  # 只处理前3个做测试
            print(f"\n处理第{i}个分类:")
            print(f"  ID: {category.id}")
            print(f"  名称: {category.category_name}")
            print(f"  代码: {category.category_code}")
            print(f"  预算: {category.budget_amount}")
            print(f"  设备数: {category.total_items_count}")
            print(f"  创建时间: {category.created_at}")
            
            category_dict = {
                "id": category.id,
                "project_id": category.project_id,
                "version_id": category.version_id,
                "category_name": category.category_name,
                "category_code": category.category_code,
                "excel_sheet_name": category.excel_sheet_name,
                "budget_amount": str(category.budget_amount) if category.budget_amount else "0",
                "total_items_count": category.total_items_count,
                "description": category.description,
                "remarks": category.remarks,
                "created_at": category.created_at.isoformat() if category.created_at else None,
                "updated_at": category.updated_at.isoformat() if category.updated_at else None
            }
            
            result.append(category_dict)
            print(f"  转换成功: {category_dict}")
        
        print(f"\n✅ API逻辑测试成功！返回{len(result)}个分类")
        return result
        
    except Exception as e:
        print(f"❌ API逻辑测试失败: {str(e)}")
        traceback.print_exc()
        return None
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    test_categories_api()