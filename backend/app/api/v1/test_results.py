"""
测试结果API接口
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime, timedelta
import uuid
import asyncio
import sys
import os
import subprocess

from app.core.database import get_db
from app.models.test_result import TestResult, TestRun
from app.api.deps import get_current_user
from app.core.test_scheduler import TestScheduler


router = APIRouter()


@router.get("/runs")
def get_test_runs(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    run_type: Optional[str] = None,
    status: Optional[str] = None,
    days: int = Query(7, ge=1, le=90, description="查询最近N天的数据"),
    db: Session = Depends(get_db)
):
    """获取测试运行列表"""
    query = db.query(TestRun)
    
    # 时间过滤
    start_date = datetime.now() - timedelta(days=days)
    query = query.filter(TestRun.created_at >= start_date)
    
    # 条件过滤
    if run_type:
        query = query.filter(TestRun.run_type == run_type)
    if status:
        query = query.filter(TestRun.status == status)
    
    # 排序和分页
    total = query.count()
    items = query.order_by(desc(TestRun.created_at)).offset((page - 1) * size).limit(size).all()
    
    return {
        "items": [item.to_dict() for item in items],
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size
    }


@router.get("/runs/{run_id}")
def get_test_run_detail(
    run_id: str,
    db: Session = Depends(get_db)
):
    """获取测试运行详情"""
    test_run = db.query(TestRun).filter(TestRun.run_id == run_id).first()
    if not test_run:
        raise HTTPException(status_code=404, detail="测试运行记录不存在")
    
    # 获取该运行的所有测试结果
    test_results = db.query(TestResult).filter(
        TestResult.test_run_id == run_id
    ).order_by(TestResult.test_suite, TestResult.test_name).all()
    
    # 按测试套件分组
    results_by_suite = {}
    for result in test_results:
        if result.test_suite not in results_by_suite:
            results_by_suite[result.test_suite] = []
        results_by_suite[result.test_suite].append(result.to_dict())
    
    return {
        "run": test_run.to_dict(),
        "results": results_by_suite
    }


@router.post("/runs/trigger")
async def trigger_test_run(
    test_type: str = Query(..., regex="^(all|unit|integration)$"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """手动触发测试运行"""
    # 运行环境检查
    backend_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
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
            return {
                "message": "环境检查失败，请修复环境问题后重试",
                "status": "failed",
                "error": "environment_check_failed",
                "details": env_check_result.stdout + env_check_result.stderr
            }
    except Exception as e:
        return {
            "message": f"环境检查异常: {str(e)}",
            "status": "failed",
            "error": "environment_check_error"
        }
    
    # 检查并清理超时的测试（超过1分钟的running状态视为僵死）
    timeout_threshold = datetime.now() - timedelta(minutes=1)
    stuck_tests = db.query(TestRun).filter(
        TestRun.status == "running",
        TestRun.start_time < timeout_threshold
    ).all()
    
    # 将僵死的测试标记为失败
    for stuck_test in stuck_tests:
        stuck_test.status = "failed"
        stuck_test.end_time = datetime.now()
        stuck_test.duration = (stuck_test.end_time - stuck_test.start_time).total_seconds()
    
    if stuck_tests:
        db.commit()
        print(f"清理了 {len(stuck_tests)} 个僵死的测试运行")
    
    # 检查是否还有正在运行的测试
    running_tests = db.query(TestRun).filter(TestRun.status == "running").count()
    if running_tests > 0:
        raise HTTPException(status_code=400, detail="已有测试正在运行中")
    
    # 创建新的测试运行记录
    run_id = f"RUN_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
    test_run = TestRun(
        run_id=run_id,
        run_type="manual",
        start_time=datetime.now(),
        status="running",
        trigger_user=current_user.get("username", "unknown"),
        environment={
            "test_type": test_type,
            "python_version": "3.8",
            "os": "windows"
        }
    )
    
    db.add(test_run)
    db.commit()
    db.refresh(test_run)
    
    # 直接运行pytest（绕过TestScheduler避免挂死）
    try:
        # 修复路径计算：需要向上4级才能到backend目录
        # __file__ = /home/ubuntu/shenyuan-erp/backend/app/api/v1/test_results.py
        backend_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        
        # 处理测试路径
        if test_type == "all":
            test_path = "tests"
        else:
            test_path = f"tests/{test_type}"
        
        print(f"Running pytest in {backend_path}/{test_path}")
        
        # 使用异步subprocess
        process = await asyncio.create_subprocess_exec(
            sys.executable, '-m', 'pytest', test_path, '-v', '--tb=line',
            cwd=backend_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=60)
        
        # 简单解析输出
        output = stdout.decode('utf-8') if stdout else ''
        error_output = stderr.decode('utf-8') if stderr else ''
        
        # 计算通过/失败数量
        passed = output.count(' PASSED')
        failed = output.count(' FAILED')
        total = passed + failed
        
        # 更新记录
        test_run.end_time = datetime.now()
        test_run.duration = (test_run.end_time - test_run.start_time).total_seconds()
        test_run.total_tests = total
        test_run.passed_tests = passed
        test_run.failed_tests = failed
        test_run.status = "completed" if failed == 0 and process.returncode == 0 else "failed"
        
        db.commit()
        
        success_rate = (passed / total * 100) if total > 0 else 0
        
        return {
            "message": "测试执行完成",
            "run_id": run_id,
            "test_type": test_type,
            "status": test_run.status,
            "total_tests": total,
            "passed_tests": passed,
            "failed_tests": failed,
            "success_rate": success_rate,
            "duration": test_run.duration,
            "return_code": process.returncode,
            "output_preview": output[-300:] if output else error_output[-300:]
        }
    except asyncio.TimeoutError:
        # 超时处理
        test_run.status = "failed"
        test_run.end_time = datetime.now()
        test_run.duration = (test_run.end_time - test_run.start_time).total_seconds()
        db.commit()
        
        return {
            "message": "测试执行超时",
            "run_id": run_id,
            "test_type": test_type,
            "status": "failed",
            "error": "timeout"
        }
    except Exception as e:
        # 如果执行失败，更新测试状态
        test_run.status = "failed"
        test_run.end_time = datetime.now()
        test_run.duration = (test_run.end_time - test_run.start_time).total_seconds()
        db.commit()
        
        return {
            "message": f"测试执行失败: {str(e)}",
            "run_id": run_id,
            "test_type": test_type,
            "status": "failed"
        }
    
    return {
        "message": "测试已触发",
        "run_id": run_id,
        "test_type": test_type
    }


@router.get("/statistics")
def get_test_statistics(
    days: int = Query(30, ge=1, le=90),
    db: Session = Depends(get_db)
):
    """获取测试统计信息"""
    start_date = datetime.now() - timedelta(days=days)
    
    # 获取时间范围内的所有测试运行
    test_runs = db.query(TestRun).filter(
        TestRun.created_at >= start_date,
        TestRun.status == "completed"
    ).all()
    
    # 计算统计数据
    total_runs = len(test_runs)
    total_tests = sum(run.total_tests for run in test_runs)
    total_passed = sum(run.passed_tests for run in test_runs)
    total_failed = sum(run.failed_tests for run in test_runs)
    
    # 按天统计
    daily_stats = {}
    for run in test_runs:
        date_key = run.created_at.strftime("%Y-%m-%d")
        if date_key not in daily_stats:
            daily_stats[date_key] = {
                "date": date_key,
                "runs": 0,
                "tests": 0,
                "passed": 0,
                "failed": 0
            }
        daily_stats[date_key]["runs"] += 1
        daily_stats[date_key]["tests"] += run.total_tests
        daily_stats[date_key]["passed"] += run.passed_tests
        daily_stats[date_key]["failed"] += run.failed_tests
    
    return {
        "summary": {
            "total_runs": total_runs,
            "total_tests": total_tests,
            "total_passed": total_passed,
            "total_failed": total_failed,
            "success_rate": round((total_passed / total_tests * 100) if total_tests > 0 else 0, 2)
        },
        "daily_stats": list(daily_stats.values())
    }


@router.get("/latest")
def get_latest_test_status(db: Session = Depends(get_db)):
    """获取最新的测试状态"""
    latest_run = db.query(TestRun).order_by(desc(TestRun.created_at)).first()
    
    if not latest_run:
        return {
            "has_run": False,
            "message": "暂无测试运行记录"
        }
    
    # 获取失败的测试详情
    failed_tests = []
    if latest_run.failed_tests > 0:
        failed_results = db.query(TestResult).filter(
            TestResult.test_run_id == latest_run.run_id,
            TestResult.status == "failed"
        ).limit(10).all()
        failed_tests = [result.to_dict() for result in failed_results]
    
    return {
        "has_run": True,
        "latest_run": latest_run.to_dict(),
        "failed_tests": failed_tests
    }