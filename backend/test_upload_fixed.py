# 测试修复后的Excel上传功能
import requests
import os

def test_upload_fixed():
    """测试修复后的Excel上传功能"""
    print("=== 测试修复后的Excel上传 ===")
    
    # API地址
    project_id = 3
    upload_url = f"http://localhost:8001/api/v1/upload/projects/{project_id}/upload-contract-excel"
    
    # 测试文件路径
    file_path = "../docs/【体育局】供应商询价清单（含价格）.xlsx"
    
    if not os.path.exists(file_path):
        print(f"测试文件不存在: {file_path}")
        return
    
    
    try:
        print(f"准备上传文件: {file_path}")
        print(f"项目ID: {project_id}")
        
        # 准备文件上传
        with open(file_path, 'rb') as f:
            files = {
                'file': ('供应商询价清单.xlsx', f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            }
            
            data = {
                'project_id': project_id,
                'description': '测试修复后的Excel解析器',
                'upload_user_name': '测试用户'
            }
            
            print("开始上传...")
            response = requests.post(upload_url, files=files, data=data, timeout=60)
            
            print(f"响应状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"上传成功!")
                print(f"版本ID: {result.get('version_id')}")
                print(f"解析统计: {result.get('parse_summary')}")
                
                # 等待几秒让数据处理完成
                import time
                time.sleep(3)
                
                # 检查数据库中的新数据
                print("\n检查数据库中的新数据...")
                check_data_url = f"http://localhost:8001/api/v1/contracts/{project_id}/items"
                items_response = requests.get(check_data_url)
                
                if items_response.status_code == 200:
                    items_data = items_response.json()
                    print(f"设备总数: {items_data.get('total', 0)}")
                    
                    if items_data.get('items'):
                        print(f"前3个设备:")
                        for i, item in enumerate(items_data['items'][:3], 1):
                            print(f"  {i}. {item.get('item_name')} - 数量: {item.get('quantity')}")
                else:
                    print(f"获取设备列表失败: {items_response.status_code}")
                
            else:
                print(f"上传失败: {response.status_code}")
                print(f"错误信息: {response.text}")
                
    except Exception as e:
        print(f"测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_upload_fixed()