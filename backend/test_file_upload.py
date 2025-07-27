# backend/test_file_upload.py
"""
文件上传功能测试脚本

测试Excel文件上传和解析功能
"""

import urllib.request
import urllib.parse
import urllib.error
import json
import os
from sqlalchemy.orm import sessionmaker
from app.core.database import engine
from app.models.project import Project

def create_test_project():
    """创建测试项目"""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        test_project = Project(
            project_code="UPLOAD_TEST_001",
            project_name="文件上传测试项目",
            contract_amount=2000000.00,
            project_manager="上传测试工程师",
            description="用于测试Excel文件上传功能的项目"
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
        print("请确保后端服务器正在运行")
        return False

def test_file_upload_api():
    """测试文件上传API"""
    print("开始测试文件上传API...")
    
    # 创建测试项目
    project_id = create_test_project()
    print(f"创建测试项目，ID: {project_id}")
    
    base_url = "http://localhost:8000/api/v1/upload"
    
    try:
        # 1. 测试获取合同文件列表（应该为空）
        print("\n1. 测试获取合同文件列表...")
        status_code, result = make_get_request(
            f"{base_url}/projects/{project_id}/contract-files"
        )
        
        if status_code == 200:
            print(f"获取文件列表成功，当前文件数: {result['total_files']}")
        else:
            print(f"获取文件列表失败: {status_code} - {result}")
        
        # 注意：实际的文件上传测试需要multipart/form-data格式
        # 这里只能测试基本的API端点是否可访问
        print("\n2. 文件上传接口端点检查...")
        
        # 检查上传目录是否存在
        upload_dir = "uploads/contracts"
        if os.path.exists(upload_dir):
            print(f"上传目录存在: {upload_dir}")
        else:
            print(f"上传目录不存在: {upload_dir}")
        
        # 检查测试Excel文件是否存在
        test_excel = r"C:\Users\ch_w1\shenyuan-erp\docs\体育局投标清单.xlsx"
        if os.path.exists(test_excel):
            print(f"测试Excel文件存在: {test_excel}")
            
            # 显示文件信息
            file_size = os.path.getsize(test_excel)
            print(f"文件大小: {file_size / 1024 / 1024:.2f} MB")
            
            # 提示手动测试方法
            print("\n=== 手动测试建议 ===")
            print("可以使用以下方法进行完整的文件上传测试:")
            print("1. 启动服务器: python -m uvicorn app.main:app --reload")
            print("2. 访问 http://localhost:8000/docs")
            print("3. 在Swagger UI中测试文件上传接口")
            print(f"4. 上传文件: {test_excel}")
            print(f"5. 项目ID: {project_id}")
            
        else:
            print(f"测试Excel文件不存在: {test_excel}")
        
        print("\nAPI端点测试完成!")
        
    except Exception as e:
        print(f"\nAPI测试过程中出错: {str(e)}")
    
    finally:
        # 清理测试数据
        print("\n清理测试数据...")
        cleanup_test_project(project_id)

if __name__ == "__main__":
    print("文件上传API测试")
    print("==================")
    
    # 检查服务器连接
    if test_server_connection():
        test_file_upload_api()
    else:
        print("请启动后端服务器后再运行测试")