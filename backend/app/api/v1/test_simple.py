"""
简化的测试触发API - 用于调试
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime, timedelta
import uuid
import subprocess
import sys
import os

from app.core.database import get_db
from app.models.test_result import TestResult, TestRun
from app.api.deps import get_current_user

router = APIRouter()

@router.post("/runs/simple-trigger")
async def simple_trigger_test_run(
    test_type: str = Query(..., regex="^(all|unit|integration)$"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """简化的测试触发 - 直接运行pytest"""
    
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
    
    # 清理僵死测试
    timeout_threshold = datetime.now() - timedelta(minutes=1)
    stuck_tests = db.query(TestRun).filter(
        TestRun.status == "running",
        TestRun.start_time < timeout_threshold
    ).all()
    
    for stuck_test in stuck_tests:
        stuck_test.status = "failed"
        stuck_test.end_time = datetime.now()
        stuck_test.duration = (stuck_test.end_time - stuck_test.start_time).total_seconds()
    
    if stuck_tests:
        db.commit()
    
    # 检查是否还有正在运行的测试
    running_tests = db.query(TestRun).filter(TestRun.status == "running").count()
    if running_tests > 0:
        raise HTTPException(status_code=400, detail="已有测试正在运行中")
    
    # 创建测试记录
    run_id = f"SIMPLE_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
    test_run = TestRun(
        run_id=run_id,
        run_type="manual",
        start_time=datetime.now(),
        status="running",
        trigger_user=getattr(current_user, "username", "unknown")
    )
    
    db.add(test_run)
    db.commit()
    db.refresh(test_run)
    
    try:
        # 确定测试路径 - 修复路径计算
        # __file__ = /home/ubuntu/shenyuan-erp/backend/app/api/v1/test_simple.py
        # 需要向上4级才能到backend目录
        backend_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        
        if test_type == "unit":
            test_path = os.path.join(backend_path, "tests", "unit")
        elif test_type == "integration":
            test_path = os.path.join(backend_path, "tests", "integration")
        else:  # all
            test_path = os.path.join(backend_path, "tests")
        
        # 调试：记录路径信息
        debug_info = f"Backend path: {backend_path}\nTest path: {test_path}\n"
        
        # 直接运行pytest - 确保在正确的虚拟环境中
        venv_python = os.path.join(backend_path, "venv", "bin", "python")
        result = subprocess.run(
            [venv_python, "-m", "pytest", test_path, "-v"],
            cwd=backend_path,
            capture_output=True,
            text=True,
            timeout=60  # 1分钟超时
        )
        
        # 简单解析结果
        output_lines = result.stdout.split('\n')
        passed = 0
        failed = 0
        
        for line in output_lines:
            if " PASSED " in line:
                passed += 1
            elif " FAILED " in line:
                failed += 1
        
        total = passed + failed
        
        # 更新测试记录
        test_run.end_time = datetime.now()
        test_run.duration = (test_run.end_time - test_run.start_time).total_seconds()
        test_run.total_tests = total
        test_run.passed_tests = passed
        test_run.failed_tests = failed
        test_run.status = "completed" if failed == 0 else "failed"
        
        db.commit()
        
        return {
            "message": "测试执行完成",
            "run_id": run_id,
            "test_type": test_type,
            "status": test_run.status,
            "total_tests": total,
            "passed_tests": passed,
            "failed_tests": failed,
            "success_rate": (passed / total * 100) if total > 0 else 0,
            "duration": test_run.duration,
            "return_code": result.returncode,
            "output_preview": result.stdout[-500:] if result.stdout else "",  # 最后500字符
            "debug_info": debug_info  # 临时添加调试信息
        }
        
    except subprocess.TimeoutExpired:
        test_run.status = "failed"
        test_run.end_time = datetime.now()
        test_run.duration = (test_run.end_time - test_run.start_time).total_seconds()
        db.commit()
        
        return {
            "message": "测试执行超时",
            "run_id": run_id,
            "status": "failed"
        }
        
    except Exception as e:
        test_run.status = "failed"
        test_run.end_time = datetime.now()
        test_run.duration = (test_run.end_time - test_run.start_time).total_seconds()
        db.commit()
        
        return {
            "message": f"测试执行失败: {str(e)}",
            "run_id": run_id,
            "status": "failed"
        }