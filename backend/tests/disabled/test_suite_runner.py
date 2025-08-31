#!/usr/bin/env python3
"""
申购单功能测试套件运行器

综合运行最近开发功能的单元测试和集成测试，提供：
1. 分类测试运行（单元测试、集成测试、全部测试）
2. 详细测试报告生成
3. 测试覆盖统计
4. 失败测试的详细分析

使用方法：
    python test_suite_runner.py --type unit          # 只运行单元测试
    python test_suite_runner.py --type integration   # 只运行集成测试  
    python test_suite_runner.py --type all           # 运行所有测试
    python test_suite_runner.py --verbose            # 详细输出模式
    python test_suite_runner.py --report             # 生成测试报告

作者: Claude Code
创建时间: 2025-01-28
"""

import os
import sys
import argparse
import subprocess
import json
from datetime import datetime
from pathlib import Path


class PurchaseTestSuiteRunner:
    """申购单测试套件运行器"""
    
    def __init__(self):
        self.test_root = Path(__file__).parent
        self.unit_tests = [
            'unit/test_purchase_validation.py',
            'unit/test_system_category_intelligence.py', 
            'unit/test_remaining_quantity_calculation.py',
            'unit/test_batch_operations.py',
            'unit/test_workflow_approval.py'
        ]
        self.integration_tests = [
            'integration/test_purchase_workflow_integration.py',
            'integration/test_purchase_ui_backend_integration.py'
        ]
        
    def run_tests(self, test_type='all', verbose=False, generate_report=False):
        """运行测试套件"""
        print(f"\n{'='*60}")
        print(f"申购单功能测试套件 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        results = {
            'start_time': datetime.now(),
            'test_type': test_type,
            'unit_results': None,
            'integration_results': None,
            'summary': {}
        }
        
        if test_type in ['unit', 'all']:
            print(f"\n🔧 运行单元测试...")
            results['unit_results'] = self._run_test_category('unit', self.unit_tests, verbose)
            
        if test_type in ['integration', 'all']:
            print(f"\n🔗 运行集成测试...")
            results['integration_results'] = self._run_test_category('integration', self.integration_tests, verbose)
        
        results['end_time'] = datetime.now()
        results['duration'] = (results['end_time'] - results['start_time']).total_seconds()
        
        # 生成汇总
        self._generate_summary(results)
        
        # 显示结果
        self._display_results(results)
        
        if generate_report:
            self._generate_report(results)
            
        return results
    
    def _run_test_category(self, category_name, test_files, verbose):
        """运行特定类别的测试"""
        category_results = {
            'category': category_name,
            'total_files': len(test_files),
            'passed_files': 0,
            'failed_files': 0,
            'test_details': []
        }
        
        for test_file in test_files:
            test_path = self.test_root / test_file
            
            if not test_path.exists():
                print(f"  ⚠️  测试文件不存在: {test_file}")
                continue
                
            print(f"  🔍 运行: {test_file}")
            
            # 运行pytest
            cmd = [
                sys.executable, '-m', 'pytest', 
                str(test_path),
                '-v' if verbose else '-q',
                '--tb=short',
                '--no-header'
            ]
            
            try:
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True,
                    cwd=str(self.test_root.parent)
                )
                
                test_result = {
                    'file': test_file,
                    'return_code': result.returncode,
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'passed': result.returncode == 0
                }
                
                if test_result['passed']:
                    category_results['passed_files'] += 1
                    print(f"    ✅ 通过")
                else:
                    category_results['failed_files'] += 1
                    print(f"    ❌ 失败")
                    if verbose:
                        print(f"    错误信息: {result.stderr}")
                
                category_results['test_details'].append(test_result)
                
            except Exception as e:
                print(f"    💥 运行异常: {str(e)}")
                category_results['failed_files'] += 1
                category_results['test_details'].append({
                    'file': test_file,
                    'return_code': -1,
                    'error': str(e),
                    'passed': False
                })
        
        return category_results
    
    def _generate_summary(self, results):
        """生成测试汇总"""
        summary = {
            'total_test_files': 0,
            'total_passed': 0,
            'total_failed': 0,
            'success_rate': 0.0,
            'categories': []
        }
        
        for category_key in ['unit_results', 'integration_results']:
            if results[category_key]:
                cat_result = results[category_key]
                summary['total_test_files'] += cat_result['total_files']
                summary['total_passed'] += cat_result['passed_files']
                summary['total_failed'] += cat_result['failed_files']
                
                summary['categories'].append({
                    'name': cat_result['category'],
                    'total': cat_result['total_files'],
                    'passed': cat_result['passed_files'],
                    'failed': cat_result['failed_files'],
                    'success_rate': (cat_result['passed_files'] / cat_result['total_files'] * 100) if cat_result['total_files'] > 0 else 0
                })
        
        if summary['total_test_files'] > 0:
            summary['success_rate'] = summary['total_passed'] / summary['total_test_files'] * 100
            
        results['summary'] = summary
    
    def _display_results(self, results):
        """显示测试结果"""
        print(f"\n{'='*60}")
        print("测试结果汇总")
        print(f"{'='*60}")
        
        summary = results['summary']
        
        print(f"总测试文件: {summary['total_test_files']}")
        print(f"通过文件: {summary['total_passed']}")
        print(f"失败文件: {summary['total_failed']}")
        print(f"成功率: {summary['success_rate']:.1f}%")
        print(f"运行时间: {results['duration']:.2f}秒")
        
        # 分类详情
        if summary['categories']:
            print(f"\n分类详情:")
            for cat in summary['categories']:
                status = "✅" if cat['failed'] == 0 else "❌"
                print(f"  {status} {cat['name']}: {cat['passed']}/{cat['total']} ({cat['success_rate']:.1f}%)")
        
        # 失败详情
        failed_files = []
        for category_key in ['unit_results', 'integration_results']:
            if results[category_key]:
                for detail in results[category_key]['test_details']:
                    if not detail['passed']:
                        failed_files.append(detail)
        
        if failed_files:
            print(f"\n❌ 失败的测试文件:")
            for failed in failed_files:
                print(f"  • {failed['file']}")
                if 'stderr' in failed and failed['stderr']:
                    # 提取关键错误信息
                    error_lines = failed['stderr'].split('\n')[:3]
                    for line in error_lines:
                        if line.strip():
                            print(f"    {line.strip()}")
        else:
            print(f"\n🎉 所有测试通过！")
    
    def _generate_report(self, results):
        """生成详细测试报告"""
        report_file = self.test_root / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # 准备报告数据
        report_data = {
            'test_run_info': {
                'start_time': results['start_time'].isoformat(),
                'end_time': results['end_time'].isoformat(),
                'duration_seconds': results['duration'],
                'test_type': results['test_type']
            },
            'summary': results['summary'],
            'unit_test_details': results.get('unit_results'),
            'integration_test_details': results.get('integration_results'),
            'environment_info': {
                'python_version': sys.version,
                'working_directory': str(self.test_root),
                'test_files_found': {
                    'unit': len(self.unit_tests),
                    'integration': len(self.integration_tests)
                }
            }
        }
        
        # 保存报告
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
            
        print(f"\n📊 详细测试报告已生成: {report_file}")
    
    def list_tests(self):
        """列出所有测试文件"""
        print(f"\n📋 申购单功能测试文件列表:")
        print(f"{'='*50}")
        
        print(f"\n🔧 单元测试 ({len(self.unit_tests)}个文件):")
        for i, test_file in enumerate(self.unit_tests, 1):
            test_path = self.test_root / test_file
            status = "✅" if test_path.exists() else "❌"
            print(f"  {i}. {status} {test_file}")
            
        print(f"\n🔗 集成测试 ({len(self.integration_tests)}个文件):")
        for i, test_file in enumerate(self.integration_tests, 1):
            test_path = self.test_root / test_file
            status = "✅" if test_path.exists() else "❌"
            print(f"  {i}. {status} {test_file}")
            
        total_tests = len(self.unit_tests) + len(self.integration_tests)
        print(f"\n📊 总计: {total_tests} 个测试文件")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='申购单功能测试套件运行器')
    parser.add_argument(
        '--type', 
        choices=['unit', 'integration', 'all'], 
        default='all',
        help='测试类型: unit(单元测试), integration(集成测试), all(全部测试)'
    )
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出模式')
    parser.add_argument('--report', '-r', action='store_true', help='生成详细测试报告')
    parser.add_argument('--list', '-l', action='store_true', help='列出所有测试文件')
    
    args = parser.parse_args()
    
    runner = PurchaseTestSuiteRunner()
    
    if args.list:
        runner.list_tests()
        return
    
    # 运行测试
    results = runner.run_tests(
        test_type=args.type,
        verbose=args.verbose,
        generate_report=args.report
    )
    
    # 设置退出码
    exit_code = 0 if results['summary']['total_failed'] == 0 else 1
    sys.exit(exit_code)


if __name__ == '__main__':
    main()