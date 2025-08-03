"""
测试调度器 - 定时执行测试任务
"""

import asyncio
import subprocess
import os
import sys
import json
import uuid
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging

from app.core.database import get_db, engine
from app.models.test_result import TestResult, TestRun

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestScheduler:
    """测试调度器"""
    
    def __init__(self):
        self.is_running = False
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    def get_db_session(self) -> Session:
        """获取数据库会话"""
        return self.SessionLocal()
    
    async def run_tests(self, test_type: str = "all", db_session: Session = None, existing_run_id: str = None) -> str:
        """运行测试并记录结果"""
        # 运行环境检查
        backend_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        env_check_script = os.path.join(backend_path, "tools", "check_test_environment.py")
        
        try:
            env_check_result = subprocess.run(
                [sys.executable, env_check_script],
                cwd=backend_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if env_check_result.returncode != 0:
                logger.error(f"环境检查失败: {env_check_result.stdout + env_check_result.stderr}")
                raise Exception("Environment check failed")
        except Exception as e:
            logger.error(f"环境检查异常: {str(e)}")
            raise Exception(f"Environment check error: {str(e)}")
        
        # 使用外部会话或创建新会话
        db = db_session if db_session else self.get_db_session()
        should_close_db = db_session is None  # 只有自己创建的会话才需要关闭
        
        try:
            if existing_run_id:
                # 使用现有的测试运行记录
                test_run = db.query(TestRun).filter(TestRun.run_id == existing_run_id).first()
                if not test_run:
                    raise ValueError(f"Test run {existing_run_id} not found")
                run_id = existing_run_id
            else:
                # 创建新的测试运行记录
                run_id = f"SCHED_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
                test_run = TestRun(
                    run_id=run_id,
                    run_type="scheduled",
                    start_time=datetime.now(),
                    status="running",
                    trigger_user="system",
                    environment={
                        "test_type": test_type,
                        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}",
                        "platform": os.name,
                        "scheduled": True
                    }
                )
                db.add(test_run)
                db.commit()
                db.refresh(test_run)
            
            logger.info(f"开始执行测试运行: {run_id}")
            
            # 运行测试
            results = await self._execute_tests(test_type, run_id, db)
            
            # 更新测试运行记录
            end_time = datetime.now()
            duration = (end_time - test_run.start_time).total_seconds()
            
            test_run.end_time = end_time
            test_run.duration = duration
            test_run.total_tests = results['total']
            test_run.passed_tests = results['passed']
            test_run.failed_tests = results['failed']
            test_run.skipped_tests = results['skipped']
            test_run.error_tests = results['error']
            test_run.status = "completed" if results['failed'] == 0 and results['error'] == 0 else "failed"
            
            db.commit()
            
            logger.info(f"测试运行完成: {run_id}, 结果: {results}")
            return run_id
            
        except Exception as e:
            logger.error(f"测试运行失败: {run_id}, 错误: {str(e)}")
            # 更新失败状态
            test_run.status = "failed"
            test_run.end_time = datetime.now()
            db.commit()
            raise
        finally:
            if should_close_db:
                db.close()
    
    async def _execute_tests(self, test_type: str, run_id: str, db: Session) -> dict:
        """执行具体的测试"""
        # 修复路径：从app/core到backend目录需要向上2级
        backend_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        
        results = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'error': 0
        }
        
        # 运行单元测试
        if test_type in ['all', 'unit']:
            unit_results = await self._run_unit_tests(backend_path, run_id, db)
            for key in results:
                results[key] += unit_results[key]
        
        # 运行集成测试
        if test_type in ['all', 'integration']:
            integration_results = await self._run_integration_tests(backend_path, run_id, db)
            for key in results:
                results[key] += integration_results[key]
        
        return results
    
    async def _run_unit_tests(self, backend_path: str, run_id: str, db: Session) -> dict:
        """运行单元测试"""
        logger.info("运行单元测试...")
        
        try:
            # 运行pytest单元测试 - 使用与手动测试相同的方式
            cmd = [
                sys.executable, '-m', 'pytest', 
                'tests/unit', 
                '-v', 
                '--tb=short'
            ]
            
            # 使用异步subprocess避免阻塞事件循环
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=backend_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=300)
            
            # 解析文本输出
            output = stdout.decode('utf-8') if stdout else ''
            
            # 使用与手动测试相同的解析逻辑
            return self._parse_text_output(output, 'unit', run_id, db)
            
        except subprocess.TimeoutExpired:
            logger.error("单元测试执行超时")
            return {'total': 0, 'passed': 0, 'failed': 1, 'skipped': 0, 'error': 0}
        except Exception as e:
            logger.error(f"单元测试执行异常: {str(e)}")
            return {'total': 0, 'passed': 0, 'failed': 0, 'skipped': 0, 'error': 1}
    
    async def _run_integration_tests(self, backend_path: str, run_id: str, db: Session) -> dict:
        """运行集成测试"""
        logger.info("运行集成测试...")
        
        try:
            # 运行pytest集成测试 - 使用与手动测试相同的方式
            cmd = [
                sys.executable, '-m', 'pytest', 
                'tests/integration', 
                '-v', 
                '--tb=short'
            ]
            
            # 使用异步subprocess避免阻塞事件循环
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=backend_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=300)
            
            # 解析文本输出
            output = stdout.decode('utf-8') if stdout else ''
            
            # 使用与手动测试相同的解析逻辑
            return self._parse_text_output(output, 'integration', run_id, db)
            
        except subprocess.TimeoutExpired:
            logger.error("集成测试执行超时")
            return {'total': 0, 'passed': 0, 'failed': 1, 'skipped': 0, 'error': 0}
        except Exception as e:
            logger.error(f"集成测试执行异常: {str(e)}")
            return {'total': 0, 'passed': 0, 'failed': 0, 'skipped': 0, 'error': 1}
    
    async def _parse_pytest_results(self, backend_path: str, json_file: str, test_type: str, run_id: str, db: Session) -> dict:
        """解析pytest JSON结果"""
        json_path = os.path.join(backend_path, json_file)
        
        results = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'error': 0
        }
        
        try:
            if not os.path.exists(json_path):
                logger.warning(f"测试结果文件不存在: {json_path}")
                return results
            
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 解析测试结果
            for test in data.get('tests', []):
                test_suite = test.get('nodeid', '').split('::')[0].replace('/', '.').replace('.py', '')
                test_name = test.get('nodeid', '').split('::')[-1]
                outcome = test.get('outcome', 'unknown')
                duration = test.get('duration', 0)
                
                # 映射状态
                if outcome == 'passed':
                    status = 'passed'
                    results['passed'] += 1
                elif outcome == 'failed':
                    status = 'failed' 
                    results['failed'] += 1
                elif outcome == 'skipped':
                    status = 'skipped'
                    results['skipped'] += 1
                else:
                    status = 'error'
                    results['error'] += 1
                
                results['total'] += 1
                
                # 获取错误信息
                error_message = None
                stack_trace = None
                if outcome == 'failed' and 'call' in test:
                    call_info = test['call']
                    if 'longrepr' in call_info:
                        error_message = str(call_info['longrepr'])[:500]  # 限制长度
                        stack_trace = str(call_info['longrepr'])
                
                # 保存测试结果
                test_result = TestResult(
                    test_run_id=run_id,
                    test_type=test_type,
                    test_suite=test_suite,
                    test_name=test_name,
                    status=status,
                    duration=duration,
                    error_message=error_message,
                    stack_trace=stack_trace
                )
                db.add(test_result)
            
            db.commit()
            
            # 清理临时文件
            try:
                os.remove(json_path)
            except:
                pass
                
        except Exception as e:
            logger.error(f"解析测试结果失败: {str(e)}")
            results['error'] += 1
        
        return results
    
    def _parse_text_output(self, output: str, test_type: str, run_id: str, db: Session) -> dict:
        """解析pytest文本输出 - 与手动测试使用相同的解析逻辑"""
        results = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'error': 0
        }
        
        if not output:
            return results
        
        # 简单解析输出行
        output_lines = output.split('\n')
        
        for line in output_lines:
            if " PASSED " in line:
                results['passed'] += 1
            elif " FAILED " in line:
                results['failed'] += 1
            elif " SKIPPED " in line:
                results['skipped'] += 1
            elif " ERROR " in line:
                results['error'] += 1
        
        results['total'] = results['passed'] + results['failed'] + results['skipped'] + results['error']
        
        logger.info(f"解析{test_type}测试结果: 总计{results['total']}个, 通过{results['passed']}个, 失败{results['failed']}个")
        
        return results
    
    async def schedule_daily_tests(self):
        """每日定时测试调度"""
        logger.info("启动每日测试调度器...")
        self.is_running = True
        
        while self.is_running:
            try:
                now = datetime.now()
                # 每天UTC 13:00执行测试（北京时间晚上9点）
                target_time = now.replace(hour=13, minute=0, second=0, microsecond=0)
                
                # 如果已经过了今天的执行时间，则安排明天的
                if now >= target_time:
                    target_time += timedelta(days=1)
                
                # 计算等待时间
                wait_seconds = (target_time - now).total_seconds()
                logger.info(f"下次测试时间: {target_time}, 等待 {wait_seconds/3600:.1f} 小时")
                
                # 等待到指定时间
                await asyncio.sleep(wait_seconds)
                
                if self.is_running:
                    # 执行测试
                    await self.run_tests("all")
                    
            except Exception as e:
                logger.error(f"调度器运行异常: {str(e)}")
                # 等待1小时后重试
                await asyncio.sleep(3600)
    
    def stop_scheduler(self):
        """停止调度器"""
        logger.info("停止测试调度器...")
        self.is_running = False


# 全局调度器实例
test_scheduler = TestScheduler()


async def start_test_scheduler():
    """启动测试调度器"""
    await test_scheduler.schedule_daily_tests()


def stop_test_scheduler():
    """停止测试调度器"""
    test_scheduler.stop_scheduler()