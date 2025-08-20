#!/usr/bin/env python3
"""
申购单测试套件独立运行器
不依赖复杂的数据库模型，专注于业务逻辑和权限测试
"""

import sys
import os
import subprocess
import datetime
import json

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

def run_standalone_test(test_file, description):
    """运行独立测试文件"""
    print(f"\n{'=' * 70}")
    print(f"🚀 运行{description}...")
    print(f"文件: {test_file}")
    print('=' * 70)
    
    try:
        result = subprocess.run(
            [sys.executable, test_file], 
            capture_output=True, 
            text=True, 
            cwd=os.path.dirname(os.path.dirname(__file__))
        )
        
        if result.returncode == 0:
            print(result.stdout)
            return True, "测试通过", result.stdout
        else:
            print(result.stdout)
            if result.stderr:
                print(result.stderr)
            return False, "测试失败", result.stderr
            
    except Exception as e:
        error_msg = f"运行测试时出错: {str(e)}"
        print(error_msg)
        return False, "运行错误", error_msg

def generate_test_report(test_results, output_file):
    """生成测试报告"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    report_content = f"""
申购单测试套件报告 (独立版本)
================================
生成时间: {timestamp}
测试环境: 开发环境
测试方式: 独立Python脚本运行

测试结果汇总:
"""
    
    total_tests = len(test_results)
    passed_tests = sum(1 for result in test_results if result['success'])
    failed_tests = total_tests - passed_tests
    
    report_content += f"""
- 总测试模块: {total_tests}
- 通过模块: {passed_tests}  
- 失败模块: {failed_tests}
- 成功率: {(passed_tests/total_tests*100):.1f}%

详细结果:
"""
    
    for i, result in enumerate(test_results, 1):
        status_emoji = "✅" if result['success'] else "❌"
        report_content += f"""
{i}. {status_emoji} {result['description']}
   文件: {result['test_file']}
   状态: {result['status']}
   时间: {result['timestamp']}
"""
        if not result['success']:
            error_preview = result['error'][:300] if result['error'] else "未知错误"
            report_content += f"   错误: {error_preview}...\n"
    
    # 写入报告文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    return report_content

def run_purchase_test_suite():
    """运行申购单测试套件"""
    print("🚀 开始运行申购单独立测试套件...")
    print(f"时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # 定义测试文件列表
    test_files = [
        {
            'file': 'tests/test_purchase_rules.py',
            'description': '申购单智能规则测试',
            'category': 'business_rules'
        },
        {
            'file': 'tests/unit/test_purchase_permissions.py', 
            'description': '权限系统测试',
            'category': 'permissions'
        },
        {
            'file': 'tests/integration/test_purchase_edit_page.py',
            'description': '编辑页面集成测试', 
            'category': 'edit_page'
        }
    ]
    
    # 运行所有测试
    test_results = []
    
    for test_config in test_files:
        test_file = test_config['file']
        description = test_config['description']
        
        # 检查测试文件是否存在
        full_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), test_file)
        if not os.path.exists(full_path):
            print(f"⚠️  警告: 测试文件不存在: {full_path}")
            test_results.append({
                'test_file': test_file,
                'description': description, 
                'success': False,
                'status': '文件不存在',
                'error': f'测试文件不存在: {full_path}',
                'timestamp': datetime.datetime.now().strftime('%H:%M:%S'),
                'category': test_config['category']
            })
            continue
        
        # 运行测试
        success, status, output = run_standalone_test(full_path, description)
        
        test_results.append({
            'test_file': test_file,
            'description': description,
            'success': success,
            'status': status, 
            'error': output if not success else '',
            'timestamp': datetime.datetime.now().strftime('%H:%M:%S'),
            'category': test_config['category']
        })
    
    # 生成测试报告
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'test_reports')
    os.makedirs(report_dir, exist_ok=True)
    
    report_file = os.path.join(report_dir, f'purchase_test_report_standalone_{timestamp}.txt')
    report_content = generate_test_report(test_results, report_file)
    
    # 输出汇总结果
    print("\n" + "=" * 80)
    print("📊 测试套件执行完成")
    print("=" * 80)
    
    total_tests = len(test_results)
    passed_tests = sum(1 for result in test_results if result['success'])
    failed_tests = total_tests - passed_tests
    
    print(f"总测试模块: {total_tests}")
    print(f"通过模块: {passed_tests}")
    print(f"失败模块: {failed_tests}")
    print(f"成功率: {(passed_tests/total_tests*100):.1f}%")
    
    # 按类别显示结果
    categories = {}
    for result in test_results:
        category = result['category']
        if category not in categories:
            categories[category] = {'passed': 0, 'failed': 0}
        
        if result['success']:
            categories[category]['passed'] += 1
        else:
            categories[category]['failed'] += 1
    
    print("\n📈 分类测试结果:")
    for category, stats in categories.items():
        total = stats['passed'] + stats['failed']
        success_rate = (stats['passed'] / total * 100) if total > 0 else 0
        status_emoji = "✅" if stats['failed'] == 0 else "⚠️" if success_rate >= 50 else "❌"
        print(f"  {status_emoji} {category}: {stats['passed']}/{total} 通过 ({success_rate:.1f}%)")
    
    if failed_tests > 0:
        print(f"\n❌ 失败的测试模块:")
        for result in test_results:
            if not result['success']:
                print(f"  - {result['description']}: {result['status']}")
    else:
        print(f"\n🎉 所有测试模块通过！申购单系统功能完整且稳定。")
    
    print(f"\n📄 详细测试报告: {report_file}")
    
    # 返回测试结果
    return failed_tests == 0, test_results

def integrate_with_daily_tests():
    """集成到每日测试套件"""
    print("\n🔗 集成申购单测试到每日回归测试套件...")
    
    # 创建集成配置文件
    config = {
        "purchase_tests_standalone": {
            "enabled": True,
            "script": __file__,
            "description": "申购单独立测试套件",
            "schedule": "daily",
            "timeout": 600,  # 10分钟超时
            "categories": [
                "business_rules",
                "permissions", 
                "edit_page"
            ],
            "coverage": {
                "intelligent_rules": "申购业务规则验证",
                "permission_system": "多角色权限控制",
                "edit_functionality": "历史数据编辑支持"
            }
        }
    }
    
    config_file = os.path.join(os.path.dirname(__file__), 'purchase_test_config_standalone.json')
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 创建独立测试配置文件: {config_file}")
    
    # 创建daily runner集成示例
    integration_example = f"""
# 在每日测试脚本中添加以下代码:

import subprocess
import datetime

def run_purchase_tests():
    \"\"\"运行申购单测试套件\"\"\"
    print("🛒 运行申购单模块测试...")
    
    result = subprocess.run([
        'python3', '{__file__}'
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ 申购单测试套件通过")
        return True
    else:
        print("❌ 申购单测试套件失败")
        print(result.stdout)
        print(result.stderr)
        return False

# 在主测试流程中调用:
if __name__ == "__main__":
    tests_passed = []
    tests_passed.append(run_purchase_tests())
    # ... 其他模块测试
    
    all_passed = all(tests_passed)
    print(f"每日测试结果: {'通过' if all_passed else '失败'}")
"""
    
    integration_file = os.path.join(os.path.dirname(__file__), 'daily_test_integration_example.py')
    with open(integration_file, 'w', encoding='utf-8') as f:
        f.write(integration_example)
    
    print(f"✅ 创建集成示例文件: {integration_file}")
    
    return config_file

def main():
    """主函数"""
    if len(sys.argv) > 1 and sys.argv[1] == '--integrate':
        # 集成到每日测试
        integrate_with_daily_tests()
        return 0
    else:
        # 运行完整测试套件
        success, results = run_purchase_test_suite()
        
        # 如果需要，创建集成配置
        if '--auto-integrate' in sys.argv:
            integrate_with_daily_tests()
        
        return 0 if success else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)