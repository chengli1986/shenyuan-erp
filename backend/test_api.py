# 测试API功能
from app.core.database import get_db
from app.models.contract import ContractFileVersion, SystemCategory, ContractItem
from sqlalchemy.orm import Session

def test_categories_api():
    """测试分类API的核心逻辑"""
    db = next(get_db())
    
    try:
        project_id = 3
        version_id = 1
        
        print(f"测试项目 {project_id}, 版本 {version_id}")
        
        # 验证版本是否存在
        version = db.query(ContractFileVersion).filter(
            ContractFileVersion.id == version_id,
            ContractFileVersion.project_id == project_id
        ).first()
        
        if not version:
            print("Version not found")
            return
        
        print(f"Version found: ID={version.id}, number={version.version_number}")
        
        # 查询系统分类
        categories = db.query(SystemCategory).filter(
            SystemCategory.version_id == version_id
        ).all()
        
        print(f"Found {len(categories)} categories")
        
        # 为每个分类计算设备数量
        category_list = []
        for category in categories:
            print(f"  Processing category: {category.category_name}")
            
            items_count = db.query(ContractItem).filter(
                ContractItem.category_id == category.id,
                ContractItem.is_active == True
            ).count()
            
            print(f"    Item count: {items_count}")
            
            # 创建响应对象
            category_dict = {
                "id": category.id,
                "project_id": category.project_id,
                "version_id": category.version_id,
                "category_name": category.category_name,
                "category_code": category.category_code,
                "excel_sheet_name": category.excel_sheet_name,
                "budget_amount": float(category.budget_amount) if category.budget_amount else None,
                "total_items_count": items_count,
                "description": category.description,
                "remarks": category.remarks,
                "created_at": category.created_at.isoformat() if category.created_at else None,
                "updated_at": category.updated_at.isoformat() if category.updated_at else None
            }
            category_list.append(category_dict)
        
        print(f"Successfully created {len(category_list)} category responses")
        
        # 打印第一个分类的详细信息
        if category_list:
            print("First category details:")
            for key, value in category_list[0].items():
                print(f"  {key}: {value}")
        
        return category_list
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        db.close()

if __name__ == "__main__":
    test_categories_api()