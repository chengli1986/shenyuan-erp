#!/usr/bin/env python3
"""
增强版申购单测试套件运行器
集成系统分类、编辑页面、权限系统等所有测试
用于每日回归测试
"""

import sys
import os
import subprocess
import datetime
import json

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

def run_test_module(module_path, description):
    """运行单个测试模块"""
    print(f"\n{'=' * 70}")
    print(f"🚀 运行{description}...")
    print(f"模块: {module_path}")
    print('=' * 70)
    
    try:
        # 导入并运行测试模块
        if module_path.endswith('.py'):
            # 直接运行Python文件
            result = subprocess.run([sys.executable, module_path], 
                                  capture_output=True, text=True, cwd=os.path.dirname(__file__))
            if result.returncode == 0:
                print(result.stdout)
                return True, "测试通过", result.stdout
            else:
                print(result.stdout)
                print(result.stderr)
                return False, "测试失败", result.stderr
        else:
            # 使用pytest运行
            result = subprocess.run(['python', '-m', 'pytest', module_path, '-v'], 
                                  capture_output=True, text=True, cwd=os.path.dirname(os.path.dirname(__file__)))
            if result.returncode == 0:
                print(result.stdout)
                return True, "测试通过", result.stdout
            else:
                print(result.stdout)
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
申购单增强测试套件报告
======================
生成时间: {timestamp}
测试环境: {'开发环境' if 'localhost' in str(os.environ.get('DATABASE_URL', '')) else '生产环境'}

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
   模块: {result['module']}
   状态: {result['status']}
   时间: {result['timestamp']}
"""
        if not result['success']:
            report_content += f"   错误: {result['error'][:200]}...\n"
    
    # 写入报告文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    return report_content

def run_enhanced_purchase_test_suite():
    """运行增强版申购单完整测试套件"""
    print("🚀 开始运行申购单增强测试套件...")
    print(f"时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # 定义测试模块列表
    test_modules = [
        {
            'module': 'tests/test_purchase_rules.py',
            'description': '申购单智能规则测试',
            'category': 'business_rules'
        },
        {
            'module': 'tests/unit/test_purchase_functional.py',
            'description': '申购单功能单元测试',
            'category': 'unit_tests'
        },
        {
            'module': 'tests/unit/test_purchase_system_categories.py',
            'description': '系统分类功能测试',
            'category': 'system_categories'
        },
        {
            'module': 'tests/unit/test_purchase_permissions.py',
            'description': '权限系统测试',
            'category': 'permissions'
        },
        {
            'module': 'tests/integration/test_purchase_integration.py',
            'description': '申购单集成测试',
            'category': 'integration'
        },
        {
            'module': 'tests/integration/test_purchase_edit_page.py',
            'description': '编辑页面集成测试',
            'category': 'edit_page'
        }
    ]
    
    # 运行所有测试
    test_results = []
    
    for test_config in test_modules:
        module_path = test_config['module']
        description = test_config['description']
        
        # 检查测试文件是否存在
        full_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), module_path)
        if not os.path.exists(full_path):
            print(f"⚠️  警告: 测试文件不存在: {full_path}")
            test_results.append({
                'module': module_path,
                'description': description,
                'success': False,
                'status': '文件不存在',
                'error': f'测试文件不存在: {full_path}',
                'timestamp': datetime.datetime.now().strftime('%H:%M:%S'),
                'category': test_config['category']
            })
            continue
        
        # 运行测试
        success, status, output = run_test_module(full_path, description)
        
        test_results.append({
            'module': module_path,
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
    
    report_file = os.path.join(report_dir, f'enhanced_purchase_test_report_{timestamp}.txt')
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
    
    print(f"\n📄 详细测试报告: {report_file}")
    
    # 返回测试结果
    return failed_tests == 0, test_results

def run_quick_smoke_tests():
    """运行快速冒烟测试"""
    print("🔥 运行申购单快速冒烟测试...")
    
    # 只运行核心测试
    core_tests = [
        'tests/test_purchase_rules.py',
        'tests/unit/test_purchase_system_categories.py'
    ]
    
    for test_path in core_tests:
        full_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), test_path)
        if os.path.exists(full_path):
            success, status, output = run_test_module(full_path, f"冒烟测试: {test_path}")
            if not success:
                print(f"❌ 冒烟测试失败: {test_path}")
                return False
        else:
            print(f"⚠️  冒烟测试文件不存在: {full_path}")
    
    print("✅ 申购单冒烟测试通过")
    return True

def integrate_with_daily_tests():
    """集成到每日测试套件"""
    print("🔗 集成申购单测试到每日回归测试套件...")
    
    # 检查现有的每日测试配置
    daily_test_script = os.path.join(os.path.dirname(__file__), 'run_tests.py')
    
    if os.path.exists(daily_test_script):
        print(f"✅ 找到每日测试脚本: {daily_test_script}")
        print("💡 建议在每日测试脚本中添加对本脚本的调用:")
        print(f"   python {__file__}")
    else:
        print("⚠️  未找到每日测试脚本，申购单测试将独立运行")
    
    # 创建集成配置文件
    config = {
        "purchase_tests": {
            "enabled": True,
            "script": __file__,
            "schedule": "daily",
            "timeout": 1800,  # 30分钟超时
            "categories": [
                "business_rules",
                "unit_tests", 
                "system_categories",
                "permissions",
                "integration",
                "edit_page"
            ]
        }
    }
    
    config_file = os.path.join(os.path.dirname(__file__), 'purchase_test_config.json')
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 创建测试配置文件: {config_file}")
    
    return config_file

def main():
    """主函数"""
    if len(sys.argv) > 1 and sys.argv[1] == '--smoke':
        # 运行冒烟测试
        success = run_quick_smoke_tests()
        return 0 if success else 1
    elif len(sys.argv) > 1 and sys.argv[1] == '--integrate':
        # 集成到每日测试
        integrate_with_daily_tests()
        return 0
    else:
        # 运行完整测试套件
        success, results = run_enhanced_purchase_test_suite()
        
        # 如果需要，集成到每日测试
        if '--auto-integrate' in sys.argv:
            integrate_with_daily_tests()
        
        return 0 if success else 1

if __name__ == "__main__":
    exit_code = main()