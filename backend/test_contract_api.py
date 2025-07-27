# backend/test_contract_api.py
"""
合同清单API接口测试

测试合同清单相关的所有API接口是否正常工作
这是一个完整的集成测试，验证从数据库到API的整个流程
"""

import requests
import json
from sqlalchemy.orm import sessionmaker
from app.core.database import engine
from app.models.project import Project

# 测试配置
BASE_URL = "http://localhost:8000/api/v1"
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_test_project():
    """创建测试项目，返回项目ID"""
    db = SessionLocal()
    try:
        test_project = Project(
            project_code="API_TEST_001",
            project_name="API测试项目",
            contract_amount=2000000.00,
            project_manager="API测试工程师",
            description="用于测试合同清单API的项目"
        )
        db.add(test_project)
        db.commit()
        db.refresh(test_project)
        return test_project.id
    finally:
        db.close()

def cleanup_test_project(project_id):
    """清理测试项目"""
    db = SessionLocal()
    try:
        # 删除测试数据（按照外键约束的顺序）
        from app.models.contract import ContractItem, SystemCategory, ContractFileVersion
        db.query(ContractItem).filter(ContractItem.project_id == project_id).delete()
        db.query(SystemCategory).filter(SystemCategory.project_id == project_id).delete()
        db.query(ContractFileVersion).filter(ContractFileVersion.project_id == project_id).delete()
        db.query(Project).filter(Project.id == project_id).delete()
        db.commit()
        print(f"   测试项目 {project_id} 清理完成")
    except Exception as e:
        print(f"   清理测试项目失败: {str(e)}")
        db.rollback()
    finally:
        db.close()

def test_contract_apis():
    """测试合同清单API接口"""
    print("开始测试合同清单API接口...")
    
    # 创建测试项目
    project_id = create_test_project()
    print(f"创建测试项目，ID: {project_id}")
    
    try:
        # 测试数据
        version_data = {
            "project_id": project_id,
            "upload_user_name": "API测试用户",
            "original_filename": "api_test.xlsx",
            "upload_reason": "API接口测试",
            "change_description": "测试合同清单版本创建"
        }
        
        category_data = {
            "project_id": project_id,
            "version_id": 0,  # 将在创建版本后更新
            "category_name": "API测试系统",
            "category_code": "API_TEST",
            "excel_sheet_name": "API测试",
            "budget_amount": 500000.00,
            "description": "用于API测试的系统分类"
        }
        
        item_data = {
            "project_id": project_id,
            "version_id": 0,  # 将在创建版本后更新
            "category_id": 0,  # 将在创建分类后更新
            "serial_number": "API001",
            "item_name": "API测试设备",
            "brand_model": "测试品牌 API-001",
            "specification": "API测试规格",
            "unit": "台",
            "quantity": 10,
            "unit_price": 2500.00,
            "origin_place": "中国",
            "item_type": "主材"
        }
        
        print("\n=== 测试步骤 ===")
        
        # 1. 测试创建合同清单版本
        print("\n1. 测试创建合同清单版本...")
        response = requests.post(f"{BASE_URL}/contracts/projects/{project_id}/contract-versions", 
                               json=version_data)
        
        if response.status_code == 200:
            version_result = response.json()
            version_id = version_result["id"]
            print(f"   版本创建成功，ID: {version_id}")
            
            # 更新测试数据中的版本ID
            category_data["version_id"] = version_id
            item_data["version_id"] = version_id
        else:
            print(f"   版本创建失败: {response.status_code} - {response.text}")
            return
        
        # 2. 测试获取项目的合同清单版本列表
        print("\n2. 测试获取项目的合同清单版本列表...")
        response = requests.get(f"{BASE_URL}/contracts/projects/{project_id}/contract-versions")
        
        if response.status_code == 200:
            versions = response.json()
            print(f"   获取版本列表成功，共 {len(versions)} 个版本")
        else:
            print(f"   获取版本列表失败: {response.status_code} - {response.text}")
        
        # 3. 测试获取当前版本
        print("\n3. 测试获取当前版本...")
        response = requests.get(f"{BASE_URL}/contracts/projects/{project_id}/contract-versions/current")
        
        if response.status_code == 200:
            current_version = response.json()
            print(f"   获取当前版本成功，版本号: {current_version['version_number']}")
        else:
            print(f"   获取当前版本失败: {response.status_code} - {response.text}")
        
        # 4. 测试创建系统分类
        print("\n4. 测试创建系统分类...")
        response = requests.post(f"{BASE_URL}/contracts/projects/{project_id}/versions/{version_id}/categories",
                               json=category_data)
        
        if response.status_code == 200:
            category_result = response.json()
            category_id = category_result["id"]
            print(f"   系统分类创建成功，ID: {category_id}")
            
            # 更新测试数据中的分类ID
            item_data["category_id"] = category_id
        else:
            print(f"   系统分类创建失败: {response.status_code} - {response.text}")
            return
        
        # 5. 测试获取系统分类列表
        print("\n5. 测试获取系统分类列表...")
        response = requests.get(f"{BASE_URL}/contracts/projects/{project_id}/versions/{version_id}/categories")
        
        if response.status_code == 200:
            categories = response.json()
            print(f"   获取系统分类列表成功，共 {len(categories)} 个分类")
        else:
            print(f"   获取系统分类列表失败: {response.status_code} - {response.text}")
        
        # 6. 测试创建合同清单明细
        print("\n6. 测试创建合同清单明细...")
        response = requests.post(f"{BASE_URL}/contracts/projects/{project_id}/versions/{version_id}/items",
                               json=item_data)
        
        if response.status_code == 200:
            item_result = response.json()
            item_id = item_result["id"]
            print(f"   合同清单明细创建成功，ID: {item_id}")
            print(f"   设备名称: {item_result['item_name']}")
            print(f"   数量: {item_result['quantity']}")
            print(f"   单价: {item_result['unit_price']}")
            print(f"   总价: {item_result['total_price']}")
        else:
            print(f"   合同清单明细创建失败: {response.status_code} - {response.text}")
            return
        
        # 7. 测试获取合同清单明细列表
        print("\n7. 测试获取合同清单明细列表...")
        response = requests.get(f"{BASE_URL}/contracts/projects/{project_id}/versions/{version_id}/items")
        
        if response.status_code == 200:
            items_result = response.json()
            print(f"   获取明细列表成功，共 {items_result['total']} 个明细")
        else:
            print(f"   获取明细列表失败: {response.status_code} - {response.text}")
        
        # 8. 测试获取单个明细
        print("\n8. 测试获取单个明细...")
        response = requests.get(f"{BASE_URL}/contracts/projects/{project_id}/versions/{version_id}/items/{item_id}")
        
        if response.status_code == 200:
            item_detail = response.json()
            print(f"   获取明细详情成功: {item_detail['item_name']}")
        else:
            print(f"   获取明细详情失败: {response.status_code} - {response.text}")
        
        # 9. 测试更新明细
        print("\n9. 测试更新明细...")
        update_data = {
            "quantity": 15,
            "unit_price": 3000.00,
            "remarks": "API测试更新"
        }
        response = requests.put(f"{BASE_URL}/contracts/projects/{project_id}/versions/{version_id}/items/{item_id}",
                              json=update_data)
        
        if response.status_code == 200:
            updated_item = response.json()
            print(f"   明细更新成功，新数量: {updated_item['quantity']}")
            print(f"   新单价: {updated_item['unit_price']}")
            print(f"   新总价: {updated_item['total_price']}")
        else:
            print(f"   明细更新失败: {response.status_code} - {response.text}")
        
        # 10. 测试获取项目汇总信息
        print("\n10. 测试获取项目汇总信息...")
        response = requests.get(f"{BASE_URL}/contracts/projects/{project_id}/contract-summary")
        
        if response.status_code == 200:
            summary = response.json()
            print(f"   汇总信息获取成功:")
            print(f"   总版本数: {summary['total_versions']}")
            print(f"   总分类数: {summary['total_categories']}")
            print(f"   总明细数: {summary['total_items']}")
            print(f"   总金额: {summary['total_amount']}")
        else:
            print(f"   汇总信息获取失败: {response.status_code} - {response.text}")
        
        print("\n所有API测试完成！")
        
    except Exception as e:
        print(f"\nAPI测试过程中出错: {str(e)}")
    
    finally:
        # 清理测试数据
        print("\n清理测试数据...")
        cleanup_test_project(project_id)

def test_server_connection():
    """测试服务器连接"""
    try:
        response = requests.get(f"{BASE_URL}/projects/")
        if response.status_code == 200:
            print("服务器连接正常")
            return True
        else:
            print(f"服务器响应异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"服务器连接失败: {str(e)}")
        print("请确保后端服务器正在运行 (python -m uvicorn app.main:app --reload)")
        return False

if __name__ == "__main__":
    print("合同清单API接口测试")
    print("===================")
    
    # 检查服务器连接
    if test_server_connection():
        test_contract_apis()
    else:
        print("请启动后端服务器后再运行测试")