# backend/run_tests.py
"""
测试运行脚本
设置正确的Python路径，然后运行测试
"""

import sys
import os

# 添加当前目录到Python路径，让模块能够正确导入
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_contract_model_tests():
    """运行合同清单模型测试"""
    print("开始运行合同清单模型测试...")
    
    try:
        # 导入测试模块
        from tests.unit.models.test_contract import run_tests
        
        # 运行测试
        run_tests()
        
    except Exception as e:
        print(f"❌ 测试运行失败：{str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_contract_model_tests()