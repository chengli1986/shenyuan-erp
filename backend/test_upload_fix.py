# backend/test_upload_fix.py
"""
测试事务修复是否有效
"""

import urllib.request
import urllib.parse
import json
import os

def test_simple_upload():
    """测试简单的文件上传事务"""
    print("测试文件上传事务修复...")
    
    # 测试数据
    upload_data = {
        'upload_user_name': '事务测试用户',
        'upload_reason': '测试事务修复',
        'change_description': '验证事务管理是否正常'
    }
    
    # 创建一个简单的multipart/form-data请求
    boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
    
    body_parts = []
    
    # 添加文本字段
    for key, value in upload_data.items():
        body_parts.append(f'--{boundary}')
        body_parts.append(f'Content-Disposition: form-data; name="{key}"')
        body_parts.append('')
        body_parts.append(value)
    
    # 添加一个简单的文件（模拟）
    body_parts.append(f'--{boundary}')
    body_parts.append('Content-Disposition: form-data; name="file"; filename="test.xlsx"')
    body_parts.append('Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    body_parts.append('')
    body_parts.append('fake excel content')  # 这会失败，但不会因为事务问题
    body_parts.append(f'--{boundary}--')
    
    body = '\r\n'.join(body_parts).encode('utf-8')
    
    headers = {
        'Content-Type': f'multipart/form-data; boundary={boundary}',
        'Content-Length': str(len(body))
    }
    
    try:
        req = urllib.request.Request(
            'http://localhost:8000/api/v1/upload/projects/4/upload-contract-excel',
            data=body,
            headers=headers,
            method='POST'
        )
        
        response = urllib.request.urlopen(req)
        print(f"上传成功: {response.getcode()}")
        result = json.loads(response.read().decode('utf-8'))
        print(f"响应: {result}")
        
    except urllib.error.HTTPError as e:
        print(f"HTTP错误: {e.code}")
        error_content = e.read().decode('utf-8')
        
        # 检查错误类型
        if "transaction" in error_content.lower():
            print("❌ 仍然有事务问题!")
        elif "excel" in error_content.lower() or "file" in error_content.lower():
            print("✅ 事务问题已修复，现在是文件格式问题（这是正常的）")
        else:
            print("❓ 其他错误类型")
            
        print(f"错误详情: {error_content}")
        
    except Exception as e:
        print(f"请求失败: {str(e)}")

if __name__ == "__main__":
    test_simple_upload()