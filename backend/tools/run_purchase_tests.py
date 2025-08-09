#!/usr/bin/env python
"""
申购模块测试运行器
运行申购模块的单元测试和集成测试，并生成测试报告
"""

import sys
import os
import subprocess
import json
from datetime import datetime
import uuid

# 添加项目根目录到Python路径
backend_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_path)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import engine
from app.models.test_result import TestResult, TestRun


def run_purchase_unit_tests():
    """运行申购模块单元测试"""
    print("\n" + "="*50)
    print("运行申购模块单元测试")
    print("="*50)
    
    cmd = [
        sys.executable, '-m', 'pytest',
        'tests/unit/test_purchase_functional.py',
        '-v',
        '--tb=short',
        '--color=yes'
    ]
    
    try:
        result = subprocess.run(
            cmd,
            cwd=backend_path,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        print(result.stdout)
        if result.stderr:
            print("错误输出:", result.stderr)
        
        return result.returncode == 0, result.stdout
    except Exception as e:
        print(f"单元测试执行失败: {str(e)}")
        return False, str(e)


def run_purchase_integration_tests():
    """运行申购模块集成测试"""
    print("\n" + "="*50)
    print("运行申购模块集成测试")
    print("="*50)
    
    cmd = [
        sys.executable, '-m', 'pytest',
        'tests/integration/test_purchase_integration.py',
        '-v',
        '--tb=short',
        '--color=yes'
    ]
    
    try:
        result = subprocess.run(
            cmd,
            cwd=backend_path,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        print(result.stdout)
        if result.stderr:
            print("错误输出:", result.stderr)
        
        return result.returncode == 0, result.stdout
    except Exception as e:
        print(f"集成测试执行失败: {str(e)}")
        return False, str(e)


def save_test_results(test_type, success, output):
    """保存测试结果到数据库"""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # 创建测试运行记录
        run_id = f"PURCHASE_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        test_run = TestRun(
            run_id=run_id,
            run_type="manual",
            start_time=datetime.now(),
            end_time=datetime.now(),
            status="completed" if success else "failed",
            trigger_user="test_runner",
            environment={
                "test_type": test_type,
                "module": "purchase",
                "python_version": f"{sys.version_info.major}.{sys.version_info.minor}"
            }
        )
        
        # 解析输出获取测试统计
        lines = output.split('\n')
        for line in lines:
            if 'passed' in line.lower() and 'failed' in line.lower():
                # 解析pytest的summary行
                parts = line.split()
                for i, part in enumerate(parts):
                    if 'passed' in part:
                        try:
                            test_run.passed_tests = int(parts[i-1])
                        except:
                            pass
                    if 'failed' in part:
                        try:
                            test_run.failed_tests = int(parts[i-1])
                        except:
                            pass
        
        test_run.total_tests = test_run.passed_tests + test_run.failed_tests
        
        db.add(test_run)
        db.commit()
        
        print(f"\n测试结果已保存到数据库 (run_id: {run_id})")
        return run_id
        
    except Exception as e:
        print(f"保存测试结果失败: {str(e)}")
        db.rollback()
        return None
    finally:
        db.close()


def generate_test_report(unit_success, integration_success, unit_output, integration_output):
    """生成测试报告"""
    print("\n" + "="*50)
    print("申购模块测试报告")
    print("="*50)
    print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-"*50)
    
    # 单元测试结果
    print("\n单元测试结果:")
    if unit_success:
        print("  ✅ 通过")
    else:
        print("  ❌ 失败")
    
    # 集成测试结果
    print("\n集成测试结果:")
    if integration_success:
        print("  ✅ 通过")
    else:
        print("  ❌ 失败")
    
    # 总体结果
    print("\n" + "-"*50)
    if unit_success and integration_success:
        print("总体结果: ✅ 所有测试通过")
    else:
        print("总体结果: ❌ 存在失败的测试")
    
    print("="*50)
    
    # 保存报告到文件
    report_dir = os.path.join(backend_path, "test_reports")
    os.makedirs(report_dir, exist_ok=True)
    
    report_file = os.path.join(
        report_dir,
        f"purchase_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    )
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("申购模块测试报告\n")
        f.write("="*50 + "\n")
        f.write(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("-"*50 + "\n\n")
        
        f.write("单元测试输出:\n")
        f.write(unit_output + "\n\n")
        
        f.write("集成测试输出:\n")
        f.write(integration_output + "\n\n")
        
        f.write("-"*50 + "\n")
        f.write(f"单元测试: {'通过' if unit_success else '失败'}\n")
        f.write(f"集成测试: {'通过' if integration_success else '失败'}\n")
        f.write(f"总体结果: {'所有测试通过' if unit_success and integration_success else '存在失败的测试'}\n")
    
    print(f"\n报告已保存至: {report_file}")
    return report_file


def run_smart_purchase_validation_test():
    """运行智能申购规则验证测试"""
    print("\n" + "="*50)
    print("智能申购规则验证测试")
    print("="*50)
    
    test_scenarios = [
        {
            "name": "主材必须来自合同清单",
            "description": "验证主材物料名称只能从合同清单选择",
            "expected": "只允许选择合同清单中的主材"
        },
        {
            "name": "规格自动填充",
            "description": "选择物料名称后自动显示可选规格",
            "expected": "正确显示所有可选规格选项"
        },
        {
            "name": "品牌单位自动填充",
            "description": "选择规格后自动填充品牌和单位",
            "expected": "品牌和单位自动填充且不可修改"
        },
        {
            "name": "数量限制验证",
            "description": "申购数量不能超过合同剩余数量",
            "expected": "超出数量时显示警告并限制"
        },
        {
            "name": "分批采购支持",
            "description": "支持同一物料多次分批申购",
            "expected": "正确计算剩余可申购数量"
        },
        {
            "name": "备注自由输入",
            "description": "备注字段支持自由文本输入",
            "expected": "备注内容无限制"
        }
    ]
    
    print("\n验证场景:")
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n{i}. {scenario['name']}")
        print(f"   描述: {scenario['description']}")
        print(f"   预期: {scenario['expected']}")
    
    return True


def main():
    """主函数"""
    print("开始执行申购模块测试套件...")
    
    # 运行单元测试
    unit_success, unit_output = run_purchase_unit_tests()
    
    # 运行集成测试
    integration_success, integration_output = run_purchase_integration_tests()
    
    # 运行智能申购验证
    validation_success = run_smart_purchase_validation_test()
    
    # 保存测试结果
    if unit_success or integration_success:
        save_test_results("unit", unit_success, unit_output)
        save_test_results("integration", integration_success, integration_output)
    
    # 生成测试报告
    report_file = generate_test_report(
        unit_success,
        integration_success,
        unit_output,
        integration_output
    )
    
    # 返回总体结果
    overall_success = unit_success and integration_success and validation_success
    
    if overall_success:
        print("\n✅ 申购模块所有测试通过！")
        sys.exit(0)
    else:
        print("\n❌ 申购模块存在测试失败，请查看报告了解详情。")
        sys.exit(1)


if __name__ == "__main__":
    main()