#!/usr/bin/env python3
"""
每日回归测试套件示例
集成了申购单测试套件和其他模块测试
"""

import subprocess
import datetime
import sys
import os

def log_with_timestamp(message):
    """带时间戳的日志输出"""
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")

def run_purchase_tests():
    """运行申购单测试套件"""
    log_with_timestamp("🛒 开始运行申购单模块测试...")
    
    script_path = "/home/ubuntu/shenyuan-erp/backend/tools/run_purchase_tests_standalone.py"
    
    try:
        result = subprocess.run([
            'python3', script_path
        ], capture_output=True, text=True, timeout=600)
        
        if result.returncode == 0:
            log_with_timestamp("✅ 申购单测试套件通过")
            # 输出关键统计信息
            if "成功率: 100.0%" in result.stdout:
                log_with_timestamp("   📊 所有申购单测试模块通过 (100% 成功率)")
            return True
        else:
            log_with_timestamp("❌ 申购单测试套件失败")
            log_with_timestamp("   错误输出:")
            for line in result.stdout.split('\n')[-10:]:  # 显示最后10行
                if line.strip():
                    log_with_timestamp(f"     {line}")
            return False
            
    except subprocess.TimeoutExpired:
        log_with_timestamp("⏰ 申购单测试超时")
        return False
    except Exception as e:
        log_with_timestamp(f"💥 申购单测试执行异常: {e}")
        return False

def run_contract_tests():
    """运行合同模块测试 (示例)"""
    log_with_timestamp("📋 开始运行合同模块测试...")
    # 这里是示例，实际项目中替换为真实的合同模块测试
    log_with_timestamp("✅ 合同模块测试通过 (示例)")
    return True

def run_system_tests():
    """运行系统测试 (示例)"""
    log_with_timestamp("🔧 开始运行系统测试...")
    # 这里是示例，实际项目中替换为真实的系统测试
    log_with_timestamp("✅ 系统测试通过 (示例)")
    return True

def run_integration_tests():
    """运行集成测试 (示例)"""
    log_with_timestamp("🔗 开始运行集成测试...")
    # 这里是示例，实际项目中替换为真实的集成测试
    log_with_timestamp("✅ 集成测试通过 (示例)")
    return True

def generate_daily_report(test_results):
    """生成每日测试报告"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_date = datetime.datetime.now().strftime("%Y%m%d")
    
    total_tests = len(test_results)
    passed_tests = sum(1 for result in test_results if result['passed'])
    failed_tests = total_tests - passed_tests
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    report_content = f"""
深源ERP系统每日回归测试报告
============================
生成时间: {timestamp}
测试日期: {report_date}

总体结果汇总:
- 总测试模块: {total_tests}
- 通过模块: {passed_tests}
- 失败模块: {failed_tests}
- 整体成功率: {success_rate:.1f}%

详细测试结果:
"""
    
    for i, result in enumerate(test_results, 1):
        status_emoji = "✅" if result['passed'] else "❌"
        report_content += f"""
{i}. {status_emoji} {result['module']}
   描述: {result['description']}
   状态: {'通过' if result['passed'] else '失败'}
   执行时间: {result['timestamp']}
"""
        if not result['passed'] and 'error' in result:
            report_content += f"   错误信息: {result['error']}\n"
    
    # 保存报告
    report_dir = "/home/ubuntu/shenyuan-erp/backend/test_reports"
    os.makedirs(report_dir, exist_ok=True)
    
    report_file = os.path.join(report_dir, f"daily_test_report_{report_date}.txt")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    log_with_timestamp(f"📄 每日测试报告已生成: {report_file}")
    return report_file

def main():
    """主测试流程"""
    log_with_timestamp("🚀 开始每日回归测试套件...")
    log_with_timestamp("=" * 60)
    
    # 定义测试模块
    test_modules = [
        {
            'name': 'purchase_tests',
            'description': '申购单模块测试套件',
            'function': run_purchase_tests
        },
        {
            'name': 'contract_tests', 
            'description': '合同模块测试套件',
            'function': run_contract_tests
        },
        {
            'name': 'system_tests',
            'description': '系统模块测试套件', 
            'function': run_system_tests
        },
        {
            'name': 'integration_tests',
            'description': '集成测试套件',
            'function': run_integration_tests
        }
    ]
    
    # 执行所有测试
    test_results = []
    
    for module in test_modules:
        start_time = datetime.datetime.now()
        
        try:
            passed = module['function']()
            test_results.append({
                'module': module['name'],
                'description': module['description'],
                'passed': passed,
                'timestamp': start_time.strftime('%H:%M:%S')
            })
        except Exception as e:
            log_with_timestamp(f"💥 {module['name']} 执行异常: {e}")
            test_results.append({
                'module': module['name'],
                'description': module['description'],
                'passed': False,
                'timestamp': start_time.strftime('%H:%M:%S'),
                'error': str(e)
            })
    
    # 生成测试报告
    log_with_timestamp("=" * 60)
    log_with_timestamp("📊 测试套件执行完成")
    
    total_tests = len(test_results)
    passed_tests = sum(1 for result in test_results if result['passed'])
    failed_tests = total_tests - passed_tests
    
    log_with_timestamp(f"总测试模块: {total_tests}")
    log_with_timestamp(f"通过模块: {passed_tests}")
    log_with_timestamp(f"失败模块: {failed_tests}")
    
    if failed_tests == 0:
        log_with_timestamp("🎉 所有测试模块通过！系统状态良好。")
        overall_status = "PASS"
    else:
        log_with_timestamp("⚠️ 有测试模块失败，需要检查。")
        for result in test_results:
            if not result['passed']:
                log_with_timestamp(f"   ❌ {result['description']}")
        overall_status = "FAIL"
    
    # 生成报告
    report_file = generate_daily_report(test_results)
    
    log_with_timestamp("=" * 60)
    log_with_timestamp(f"🏁 每日回归测试完成，整体状态: {overall_status}")
    
    return failed_tests == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)