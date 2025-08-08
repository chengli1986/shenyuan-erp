"""
最小化测试API - 直接运行pytest
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid
import asyncio
import sys
import os

from app.core.database import get_db
from app.models.test_result import TestResult, TestRun
from app.api.deps import get_current_user

router = APIRouter()

@router.post("/runs/minimal-trigger")
async def minimal_trigger_test_run(
    test_type: str = Query(..., regex="^(all|unit|integration)$"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """最小化测试触发 - 直接在API中运行pytest"""
    
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
    
    # 检查运行中的测试
    running_tests = db.query(TestRun).filter(TestRun.status == "running").count()
    if running_tests > 0:
        raise HTTPException(status_code=400, detail="已有测试正在运行中")
    
    # 创建测试记录
    run_id = f"MIN_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
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
        # 直接运行pytest（最简单的方式）
        # 修正路径: __file__ 是 /home/ubuntu/shenyuan-erp/backend/app/api/v1/test_minimal.py
        # 需要获取到 /home/ubuntu/shenyuan-erp/backend
        backend_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        
        # 处理测试路径
        if test_type == "all":
            test_path = "tests"  # 运行所有测试
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
        test_run.status = "failed"
        test_run.end_time = datetime.now()
        test_run.duration = (test_run.end_time - test_run.start_time).total_seconds()
        db.commit()
        
        return {
            "message": "测试执行超时",
            "run_id": run_id,
            "status": "failed",
            "error": "timeout"
        }
        
    except Exception as e:
        test_run.status = "failed"
        test_run.end_time = datetime.now()
        test_run.duration = (test_run.end_time - test_run.start_time).total_seconds()
        db.commit()
        
        return {
            "message": f"测试执行异常: {str(e)}",
            "run_id": run_id,
            "status": "failed",
            "error": str(e)
        }