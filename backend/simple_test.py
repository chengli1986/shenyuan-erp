# backend/simple_test.py
"""
简化的合同清单模型测试
测试基本功能是否正常工作
"""

from sqlalchemy.orm import sessionmaker
from app.core.database import engine
from app.models.project import Project
from app.models.contract import ContractFileVersion, SystemCategory, ContractItem

def test_contract_models():
    """测试合同清单模型的基本功能"""
    print("开始测试合同清单模型...")
    
    # 创建数据库会话
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # 第一步：创建测试项目
        print("\n1. 创建测试项目...")
        test_project = Project(
            project_code="TEST001",
            project_name="体育局测试项目",
            contract_amount=1000000.00,
            project_manager="张工程师",
            description="这是一个用于测试合同清单功能的项目"
        )
        db.add(test_project)
        db.commit()
        db.refresh(test_project)
        print(f"   项目创建成功，ID: {test_project.id}")
        
        # 第二步：创建合同清单版本
        print("\n2. 创建合同清单版本...")
        contract_version = ContractFileVersion(
            project_id=test_project.id,
            version_number=1,
            upload_user_name="管理员",
            original_filename="体育局投标清单.xlsx",
            stored_filename="contract_v1_20241227.xlsx",
            file_size=2048000,
            upload_reason="初始投标清单上传",
            is_current=True
        )
        db.add(contract_version)
        db.commit()
        db.refresh(contract_version)
        print(f"   合同清单版本创建成功，ID: {contract_version.id}")
        
        # 第三步：创建系统分类
        print("\n3. 创建系统分类...")
        
        video_system = SystemCategory(
            project_id=test_project.id,
            version_id=contract_version.id,
            category_name="视频安防监控系统",
            category_code="VIDEO_SURVEILLANCE",
            excel_sheet_name="视频监控",
            budget_amount=500000.00,
            description="包含摄像机、录像机、显示器等设备"
        )
        
        access_system = SystemCategory(
            project_id=test_project.id,
            version_id=contract_version.id,
            category_name="门禁道闸系统",
            category_code="ACCESS_CONTROL",
            excel_sheet_name="门禁道闸",
            budget_amount=300000.00,
            description="包含门禁控制器、读卡器、道闸等设备"
        )
        
        db.add(video_system)
        db.add(access_system)
        db.commit()
        db.refresh(video_system)
        db.refresh(access_system)
        print(f"   视频监控系统创建成功，ID: {video_system.id}")
        print(f"   门禁系统创建成功，ID: {access_system.id}")
        
        # 第四步：创建合同清单明细
        print("\n4. 创建合同清单明细...")
        
        camera_item = ContractItem(
            project_id=test_project.id,
            version_id=contract_version.id,
            category_id=video_system.id,
            serial_number="001",
            item_name="网络摄像机",
            brand_model="海康威视 DS-2CD2155FWD-IS",
            specification="500万像素，H.265编码",
            unit="台",
            quantity=50,
            unit_price=1200.00,
            origin_place="中国",
            item_type="主材"
        )
        
        # 计算总价
        camera_item.calculate_total_price()
        
        access_item = ContractItem(
            project_id=test_project.id,
            version_id=contract_version.id,
            category_id=access_system.id,
            serial_number="001",
            item_name="门禁控制器",
            brand_model="海康威视 DS-K2801",
            specification="单门控制器",
            unit="台",
            quantity=20,
            unit_price=800.00,
            origin_place="中国",
            item_type="主材"
        )
        
        access_item.calculate_total_price()
        
        db.add(camera_item)
        db.add(access_item)
        db.commit()
        db.refresh(camera_item)
        db.refresh(access_item)
        
        print(f"   摄像机设备创建成功，ID: {camera_item.id}, 总价: {camera_item.total_price} 元")
        print(f"   门禁控制器创建成功，ID: {access_item.id}, 总价: {access_item.total_price} 元")
        
        # 第五步：测试关联查询
        print("\n5. 测试关联查询...")
        
        # 查询项目的所有合同清单版本
        versions = db.query(ContractFileVersion).filter(
            ContractFileVersion.project_id == test_project.id
        ).all()
        print(f"   项目 {test_project.project_name} 有 {len(versions)} 个版本")
        
        # 查询当前版本的所有系统分类
        categories = db.query(SystemCategory).filter(
            SystemCategory.version_id == contract_version.id
        ).all()
        print(f"   当前版本有 {len(categories)} 个系统分类:")
        for category in categories:
            print(f"      - {category.category_name}")
        
        # 查询每个系统的设备数量
        for category in categories:
            items_count = db.query(ContractItem).filter(
                ContractItem.category_id == category.id
            ).count()
            print(f"      - {category.category_name}: {items_count} 个设备")
        
        # 第六步：测试数据转换
        print("\n6. 测试数据转换...")
        item_dict = camera_item.to_dict()
        print(f"   摄像机数据转换成功:")
        print(f"      设备名称: {item_dict['item_name']}")
        print(f"      数量: {item_dict['quantity']}")
        print(f"      单价: {item_dict['unit_price']} 元")
        print(f"      总价: {item_dict['total_price']} 元")
        
        print("\n所有测试通过！合同清单模型工作正常！")
        
        # 返回创建的数据ID，供清理使用
        return test_project.id
        
    except Exception as e:
        print(f"\n测试失败: {str(e)}")
        db.rollback()
        raise
    
    finally:
        db.close()

def cleanup_test_data(project_id):
    """清理测试数据"""
    print("\n清理测试数据...")
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # 删除测试数据（按照外键约束的顺序）
        db.query(ContractItem).filter(ContractItem.project_id == project_id).delete()
        db.query(SystemCategory).filter(SystemCategory.project_id == project_id).delete()
        db.query(ContractFileVersion).filter(ContractFileVersion.project_id == project_id).delete()
        db.query(Project).filter(Project.id == project_id).delete()
        db.commit()
        print("   测试数据清理完成")
    except Exception as e:
        print(f"   测试数据清理失败: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    try:
        project_id = test_contract_models()
        cleanup_test_data(project_id)
    except Exception as e:
        print(f"测试运行出错: {str(e)}")
        import traceback
        traceback.print_exc()