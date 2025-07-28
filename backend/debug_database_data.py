"""
调试数据库中的数据，检查字段映射和分页问题
"""

import os
import sys
sys.path.append(os.path.dirname(__file__))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.contract import ContractItem, SystemCategory, ContractFileVersion

def debug_database_data():
    """调试数据库中的数据"""
    
    # 创建数据库连接
    database_url = "sqlite:///./erp_test.db"  # 使用正确的数据库文件
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    try:
        db = SessionLocal()
        
        print("="*80)
        print("调试数据库数据")
        print("="*80)
        
        # 1. 检查合同版本
        print("\n1. 检查合同版本:")
        versions = db.query(ContractFileVersion).order_by(ContractFileVersion.id.desc()).limit(3).all()
        for version in versions:
            print(f"  版本ID: {version.id}, 项目ID: {version.project_id}, 版本号: {version.version_number}")
            print(f"  文件名: {version.original_filename}")
            print(f"  是否当前: {version.is_current}")
        
        if not versions:
            print("  [ERROR] 没有找到任何合同版本")
            return
        
        # 使用最新版本
        current_version = versions[0]
        print(f"\n使用版本: {current_version.id} (项目{current_version.project_id})")
        
        # 2. 检查系统分类
        print(f"\n2. 检查系统分类:")
        categories = db.query(SystemCategory).filter(
            SystemCategory.version_id == current_version.id
        ).all()
        
        for category in categories:
            print(f"  分类ID: {category.id}, 名称: {category.category_name}")
            print(f"  Excel工作表: {category.excel_sheet_name}")
            print(f"  设备数量: {category.total_items_count}")
        
        # 3. 检查设备明细数据 - 重点检查字段内容
        print(f"\n3. 检查设备明细数据:")
        total_items = db.query(ContractItem).filter(
            ContractItem.version_id == current_version.id,
            ContractItem.is_active == True
        ).count()
        
        print(f"  总设备数: {total_items}")
        
        # 检查前5个设备的字段内容
        items = db.query(ContractItem).filter(
            ContractItem.version_id == current_version.id,
            ContractItem.is_active == True
        ).limit(5).all()
        
        print(f"\n  前5个设备的字段详情:")
        for i, item in enumerate(items, 1):
            print(f"    设备{i}:")
            print(f"      ID: {item.id}")
            print(f"      设备名称: {item.item_name}")
            print(f"      brand_model字段: '{item.brand_model}'")  # 这应该是设备品牌
            print(f"      specification字段: '{item.specification}'")  # 这应该是设备型号
            print(f"      单位: {item.unit}")
            print(f"      数量: {item.quantity}")
            print(f"      单价: {item.unit_price}")
            print(f"      备注: {item.remarks}")
            print(f"      分类ID: {item.category_id}")
            print()
        
        # 4. 测试分页查询
        print(f"4. 测试分页查询:")
        
        # 第1页，每页20条
        page1_items = db.query(ContractItem).filter(
            ContractItem.version_id == current_version.id,
            ContractItem.is_active == True
        ).offset(0).limit(20).all()
        
        print(f"  第1页(1-20): {len(page1_items)} 条记录")
        if page1_items:
            print(f"    第1条: {page1_items[0].item_name}")
            print(f"    第20条: {page1_items[-1].item_name if len(page1_items) >= 20 else '不足20条'}")
        
        # 第2页，每页20条
        page2_items = db.query(ContractItem).filter(
            ContractItem.version_id == current_version.id,
            ContractItem.is_active == True
        ).offset(20).limit(20).all()
        
        print(f"  第2页(21-40): {len(page2_items)} 条记录")
        if page2_items:
            print(f"    第21条: {page2_items[0].item_name}")
            print(f"    最后一条: {page2_items[-1].item_name}")
        
        # 第3页，每页20条
        page3_items = db.query(ContractItem).filter(
            ContractItem.version_id == current_version.id,
            ContractItem.is_active == True
        ).offset(40).limit(20).all()
        
        print(f"  第3页(41-60): {len(page3_items)} 条记录")
        if page3_items:
            print(f"    第41条: {page3_items[0].item_name}")
            print(f"    最后一条: {page3_items[-1].item_name}")
        
        # 第4页，每页20条
        page4_items = db.query(ContractItem).filter(
            ContractItem.version_id == current_version.id,
            ContractItem.is_active == True
        ).offset(60).limit(20).all()
        
        print(f"  第4页(61-end): {len(page4_items)} 条记录")
        if page4_items:
            print(f"    第61条: {page4_items[0].item_name}")
            print(f"    最后一条: {page4_items[-1].item_name}")
        
        # 5. 检查某个具体设备的完整信息
        print(f"\n5. 检查一个具体设备的完整信息:")
        if items:
            item = items[0]
            print(f"  设备名称: {item.item_name}")
            print(f"  brand_model: '{item.brand_model}' (应该显示为设备品牌)")
            print(f"  specification: '{item.specification}' (应该显示为设备型号)")
            print(f"  origin_place: '{item.origin_place}'")
            print(f"  remarks: '{item.remarks}'")
            print(f"  序列号: {item.serial_number}")
            print(f"  创建时间: {item.created_at}")
            
            # 转换为字典格式（模拟API返回）
            item_dict = item.to_dict()
            print(f"\n  API返回格式:")
            print(f"    brand_model: '{item_dict.get('brand_model')}'")
            print(f"    specification: '{item_dict.get('specification')}'")
            print(f"    remarks: '{item_dict.get('remarks')}'")
        
        db.close()
        
    except Exception as e:
        print(f"[ERROR] 调试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_database_data()