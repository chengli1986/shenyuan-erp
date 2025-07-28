# backend/tests/unit/models/test_contract.py
"""
合同清单模型单元测试

测试合同清单相关数据库模型的基本功能：
1. 模型字段验证
2. 关联关系测试
3. 业务方法测试
4. 数据转换测试
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.models.project import Project
from app.models.contract import ContractFileVersion, SystemCategory, ContractItem


class TestContractModels:
    """合同清单模型测试类"""
    
    @classmethod
    def setup_class(cls):
        """测试类初始化 - 创建内存数据库"""
        # 使用内存SQLite数据库进行测试，不影响实际数据
        cls.engine = create_engine("sqlite:///:memory:", echo=False)
        Base.metadata.create_all(bind=cls.engine)
        cls.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=cls.engine)
        print("测试数据库初始化完成")
    
    def setup_method(self):
        """每个测试方法前的准备工作"""
        self.db = self.SessionLocal()
        
        # 为每个测试创建唯一的项目代码，避免冲突
        import uuid
        unique_code = f"TEST_{str(uuid.uuid4())[:8]}"
        
        # 创建测试项目
        self.test_project = Project(
            project_code=unique_code,
            project_name="合同清单测试项目",
            contract_amount=1000000.00,
            project_manager="测试工程师"
        )
        self.db.add(self.test_project)
        self.db.commit()
        self.db.refresh(self.test_project)
    
    def teardown_method(self):
        """每个测试方法后的清理工作"""
        self.db.rollback()
        self.db.close()
        
    @classmethod
    def teardown_class(cls):
        """测试类清理"""
        cls.engine.dispose()
    
    def test_contract_file_version_creation(self):
        """测试合同清单版本创建"""
        print("\n📄 测试合同清单版本创建...")
        
        # 创建合同清单版本
        version = ContractFileVersion(
            project_id=self.test_project.id,
            version_number=1,
            upload_user_name="测试用户",
            original_filename="test_contract.xlsx",
            stored_filename="stored_test_contract.xlsx",
            file_size=1024,
            upload_reason="单元测试",
            is_current=True
        )
        
        self.db.add(version)
        self.db.commit()
        self.db.refresh(version)
        
        # 验证数据
        assert version.id is not None
        assert version.project_id == self.test_project.id
        assert version.version_number == 1
        assert version.upload_user_name == "测试用户"
        assert version.is_current is True
        print("   ✅ 合同清单版本创建成功")
    
    def test_system_category_creation(self):
        """测试系统分类创建"""
        print("\n🏗️ 测试系统分类创建...")
        
        # 先创建版本
        version = ContractFileVersion(
            project_id=self.test_project.id,
            version_number=1,
            upload_user_name="测试用户",
            original_filename="test.xlsx",
            stored_filename="stored_test.xlsx"
        )
        self.db.add(version)
        self.db.commit()
        self.db.refresh(version)
        
        # 创建系统分类
        category = SystemCategory(
            project_id=self.test_project.id,
            version_id=version.id,
            category_name="视频监控系统",
            category_code="VIDEO",
            excel_sheet_name="视频监控",
            budget_amount=500000.00
        )
        
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        
        # 验证数据
        assert category.id is not None
        assert category.category_name == "视频监控系统"
        assert category.category_code == "VIDEO"
        assert float(category.budget_amount) == 500000.00
        print("   ✅ 系统分类创建成功")
    
    def test_contract_item_creation_and_calculation(self):
        """测试合同清单明细创建和价格计算"""
        print("\n📦 测试合同清单明细创建和价格计算...")
        
        # 创建版本和分类
        version = ContractFileVersion(
            project_id=self.test_project.id,
            version_number=1,
            upload_user_name="测试用户",
            original_filename="test.xlsx",
            stored_filename="stored_test.xlsx"
        )
        self.db.add(version)
        self.db.commit()
        self.db.refresh(version)
        
        category = SystemCategory(
            project_id=self.test_project.id,
            version_id=version.id,
            category_name="测试系统",
            category_code="TEST"
        )
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        
        # 创建合同清单明细
        item = ContractItem(
            project_id=self.test_project.id,
            version_id=version.id,
            category_id=category.id,
            serial_number="001",
            item_name="测试摄像机",
            brand_model="测试品牌 TEST-001",
            specification="测试规格",
            unit="台",
            quantity=10,
            unit_price=1500.00,
            origin_place="中国"
        )
        
        # 测试价格计算
        total_price = item.calculate_total_price()
        expected_total = 10 * 1500.00  # 数量 × 单价
        
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        
        # 验证数据
        assert item.id is not None
        assert item.item_name == "测试摄像机"
        assert float(item.quantity) == 10
        assert float(item.unit_price) == 1500.00
        assert float(item.total_price) == expected_total
        assert float(total_price) == expected_total
        print(f"   ✅ 明细创建成功，总价计算正确：{expected_total}")
    
    def test_relationships(self):
        """测试模型之间的关联关系"""
        print("\n🔗 测试模型关联关系...")
        
        # 创建完整的关联数据
        version = ContractFileVersion(
            project_id=self.test_project.id,
            version_number=1,
            upload_user_name="测试用户",
            original_filename="test.xlsx",
            stored_filename="stored_test.xlsx"
        )
        self.db.add(version)
        self.db.commit()
        self.db.refresh(version)
        
        category = SystemCategory(
            project_id=self.test_project.id,
            version_id=version.id,
            category_name="关联测试系统",
            category_code="RELATION_TEST"
        )
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        
        item = ContractItem(
            project_id=self.test_project.id,
            version_id=version.id,
            category_id=category.id,
            item_name="关联测试设备",
            quantity=5,
            unit_price=1000.00
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        
        # 测试关联查询
        # 通过版本查找分类
        categories = version.system_categories
        assert len(categories) == 1
        assert categories[0].category_name == "关联测试系统"
        
        # 通过版本查找明细项
        items = version.contract_items
        assert len(items) == 1
        assert items[0].item_name == "关联测试设备"
        
        # 通过分类查找明细项
        category_items = category.contract_items
        assert len(category_items) == 1
        assert category_items[0].item_name == "关联测试设备"
        
        print("   ✅ 关联关系测试通过")
    
    def test_to_dict_conversion(self):
        """测试数据字典转换"""
        print("\n📊 测试数据字典转换...")
        
        # 创建测试数据
        version = ContractFileVersion(
            project_id=self.test_project.id,
            version_number=1,
            upload_user_name="测试用户",
            original_filename="test.xlsx",
            stored_filename="stored_test.xlsx"
        )
        self.db.add(version)
        self.db.commit()
        self.db.refresh(version)
        
        item = ContractItem(
            project_id=self.test_project.id,
            version_id=version.id,
            item_name="字典转换测试设备",
            brand_model="TEST-DICT-001",
            unit="台",
            quantity=3,
            unit_price=2000.00,
            item_type="主材"
        )
        item.calculate_total_price()
        
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        
        # 测试字典转换
        item_dict = item.to_dict()
        
        # 验证字典内容
        assert item_dict["item_name"] == "字典转换测试设备"
        assert item_dict["brand_model"] == "TEST-DICT-001"
        assert item_dict["quantity"] == 3.0
        assert item_dict["unit_price"] == 2000.0
        assert item_dict["total_price"] == 6000.0  # 3 * 2000
        assert item_dict["item_type"] == "主材"
        assert "created_at" in item_dict
        assert "updated_at" in item_dict
        
        print("   ✅ 字典转换测试通过")
    
    def test_multiple_versions(self):
        """测试多版本管理"""
        print("\n📚 测试多版本管理...")
        
        # 创建第一个版本
        version1 = ContractFileVersion(
            project_id=self.test_project.id,
            version_number=1,
            upload_user_name="测试用户",
            original_filename="v1.xlsx",
            stored_filename="stored_v1.xlsx",
            is_current=True,
            upload_reason="初始版本"
        )
        self.db.add(version1)
        self.db.commit()
        
        # 创建第二个版本
        version2 = ContractFileVersion(
            project_id=self.test_project.id,
            version_number=2,
            upload_user_name="测试用户",
            original_filename="v2.xlsx",
            stored_filename="stored_v2.xlsx",
            is_current=False,  # 不是当前版本
            upload_reason="优化版本"
        )
        self.db.add(version2)
        self.db.commit()
        
        # 验证版本查询
        all_versions = self.db.query(ContractFileVersion).filter(
            ContractFileVersion.project_id == self.test_project.id
        ).all()
        
        current_version = self.db.query(ContractFileVersion).filter(
            ContractFileVersion.project_id == self.test_project.id,
            ContractFileVersion.is_current == True
        ).first()
        
        assert len(all_versions) == 2
        assert current_version.version_number == 1
        assert current_version.upload_reason == "初始版本"
        
        print("   ✅ 多版本管理测试通过")


def run_tests():
    """运行所有测试"""
    print("🧪 开始运行合同清单模型单元测试...")
    
    # 创建测试实例
    test_instance = TestContractModels()
    test_instance.setup_class()
    
    try:
        # 运行所有测试方法
        test_methods = [
            test_instance.test_contract_file_version_creation,
            test_instance.test_system_category_creation,
            test_instance.test_contract_item_creation_and_calculation,
            test_instance.test_relationships,
            test_instance.test_to_dict_conversion,
            test_instance.test_multiple_versions
        ]
        
        passed = 0
        failed = 0
        
        for test_method in test_methods:
            try:
                test_instance.setup_method()
                test_method()
                test_instance.teardown_method()
                passed += 1
            except Exception as e:
                print(f"❌ 测试失败：{test_method.__name__} - {str(e)}")
                failed += 1
                test_instance.teardown_method()
        
        print(f"\n📊 测试结果：")
        print(f"   ✅ 通过：{passed} 个")
        print(f"   ❌ 失败：{failed} 个")
        
        if failed == 0:
            print("🎉 所有测试通过！合同清单模型工作正常！")
        else:
            print("⚠️ 部分测试失败，请检查代码")
            
    except Exception as e:
        print(f"❌ 测试运行时出现错误：{str(e)}")


if __name__ == "__main__":
    run_tests()