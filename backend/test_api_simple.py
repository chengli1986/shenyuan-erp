# backend/test_api_simple.py
"""
简化的API测试脚本
使用urllib进行HTTP请求测试
"""

import urllib.request
import urllib.parse
import urllib.error
import json
from sqlalchemy.orm import sessionmaker
from app.core.database import engine
from app.models.project import Project

def test_server_connection():
    """测试服务器连接"""
    try:
        response = urllib.request.urlopen('http://localhost:8000/api/v1/projects/')
        if response.getcode() == 200:
            print("服务器连接正常")
            return True
        else:
            print(f"服务器响应异常: {response.getcode()}")
            return False
    except Exception as e:
        print(f"服务器连接失败: {str(e)}")
        print("请确保后端服务器正在运行 (python -m uvicorn app.main:app --reload)")
        return False

def make_post_request(url, data):
    """发送POST请求"""
    try:
        json_data = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(
            url, 
            data=json_data,
            headers={'Content-Type': 'application/json'}
        )
        response = urllib.request.urlopen(req)
        return response.getcode(), json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        error_content = e.read().decode('utf-8')
        return e.code, error_content
    except Exception as e:
        return 500, str(e)

def make_get_request(url):
    """发送GET请求"""
    try:
        response = urllib.request.urlopen(url)
        return response.getcode(), json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        error_content = e.read().decode('utf-8')
        return e.code, error_content
    except Exception as e:
        return 500, str(e)

def create_test_project():
    """创建测试项目"""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        test_project = Project(
            project_code="API_TEST_002",
            project_name="API简化测试项目",
            contract_amount=1500000.00,
            project_manager="测试工程师",
            description="用于测试合同清单API的简化项目"
        )
        db.add(test_project)
        db.commit()
        db.refresh(test_project)
        return test_project.id
    finally:
        db.close()

def cleanup_test_project(project_id):
    """清理测试项目"""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        from app.models.contract import ContractItem, SystemCategory, ContractFileVersion
        db.query(ContractItem).filter(ContractItem.project_id == project_id).delete()
        db.query(SystemCategory).filter(SystemCategory.project_id == project_id).delete()
        db.query(ContractFileVersion).filter(ContractFileVersion.project_id == project_id).delete()
        db.query(Project).filter(Project.id == project_id).delete()
        db.commit()
        print(f"测试项目 {project_id} 清理完成")
    except Exception as e:
        print(f"清理测试项目失败: {str(e)}")
        db.rollback()
    finally:
        db.close()

def test_contract_apis():
    """测试合同清单API接口"""
    print("开始测试合同清单API接口...")
    
    # 创建测试项目
    project_id = create_test_project()
    print(f"创建测试项目，ID: {project_id}")
    
    base_url = "http://localhost:8000/api/v1/contracts"
    
    try:
        # 1. 测试创建合同清单版本
        print("\n1. 测试创建合同清单版本...")
        version_data = {
            "project_id": project_id,
            "upload_user_name": "API测试用户",
            "original_filename": "api_test.xlsx",
            "upload_reason": "API接口测试",
            "change_description": "测试合同清单版本创建"
        }
        
        status_code, result = make_post_request(
            f"{base_url}/projects/{project_id}/contract-versions",
            version_data
        )
        
        if status_code == 200:
            version_id = result["id"]
            print(f"版本创建成功，ID: {version_id}")
        else:
            print(f"版本创建失败: {status_code} - {result}")
            return
        
        # 2. 测试获取项目的合同清单版本列表
        print("\n2. 测试获取合同清单版本列表...")
        status_code, result = make_get_request(
            f"{base_url}/projects/{project_id}/contract-versions"
        )
        
        if status_code == 200:
            print(f"获取版本列表成功，共 {len(result)} 个版本")
        else:
            print(f"获取版本列表失败: {status_code} - {result}")
        
        # 3. 测试获取当前版本
        print("\n3. 测试获取当前版本...")
        status_code, result = make_get_request(
            f"{base_url}/projects/{project_id}/contract-versions/current"
        )
        
        if status_code == 200:
            print(f"获取当前版本成功，版本号: {result['version_number']}")
        else:
            print(f"获取当前版本失败: {status_code} - {result}")
        
        # 4. 测试创建系统分类
        print("\n4. 测试创建系统分类...")
        category_data = {
            "project_id": project_id,
            "version_id": version_id,
            "category_name": "API测试系统",
            "category_code": "API_TEST",
            "excel_sheet_name": "API测试",
            "budget_amount": 300000.00,
            "description": "用于API测试的系统分类"
        }
        
        status_code, result = make_post_request(
            f"{base_url}/projects/{project_id}/versions/{version_id}/categories",
            category_data
        )
        
        if status_code == 200:
            category_id = result["id"]
            print(f"系统分类创建成功，ID: {category_id}")
        else:
            print(f"系统分类创建失败: {status_code} - {result}")
            return
        
        # 5. 测试创建合同清单明细
        print("\n5. 测试创建合同清单明细...")
        item_data = {
            "project_id": project_id,
            "version_id": version_id,
            "category_id": category_id,
            "serial_number": "API001",
            "item_name": "API测试设备",
            "brand_model": "测试品牌 API-001",
            "specification": "API测试规格",
            "unit": "台",
            "quantity": 8,
            "unit_price": 1800.00,
            "origin_place": "中国",
            "item_type": "主材"
        }
        
        status_code, result = make_post_request(
            f"{base_url}/projects/{project_id}/versions/{version_id}/items",
            item_data
        )
        
        if status_code == 200:
            item_id = result["id"]
            print(f"合同清单明细创建成功，ID: {item_id}")
            print(f"   设备名称: {result['item_name']}")
            print(f"   数量: {result['quantity']}")
            print(f"   单价: {result['unit_price']}")
            print(f"   总价: {result['total_price']}")
        else:
            print(f"合同清单明细创建失败: {status_code} - {result}")
            return
        
        # 6. 测试获取项目汇总信息
        print("\n6. 测试获取项目汇总信息...")
        status_code, result = make_get_request(
            f"{base_url}/projects/{project_id}/contract-summary"
        )
        
        if status_code == 200:
            print(f"汇总信息获取成功:")
            print(f"   总版本数: {result['total_versions']}")
            print(f"   总分类数: {result['total_categories']}")
            print(f"   总明细数: {result['total_items']}")
            print(f"   总金额: {result['total_amount']}")
        else:
            print(f"汇总信息获取失败: {status_code} - {result}")
        
        print("\n所有API测试完成!")
        
    except Exception as e:
        print(f"\nAPI测试过程中出错: {str(e)}")
    
    finally:
        # 清理测试数据
        print("\n清理测试数据...")
        cleanup_test_project(project_id)

if __name__ == "__main__":
    print("合同清单API接口测试")
    print("====================")
    
    # 检查服务器连接
    if test_server_connection():
        test_contract_apis()
    else:
        print("请启动后端服务器后再运行测试")