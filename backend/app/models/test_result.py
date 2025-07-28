"""
测试结果数据模型
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean, JSON
from app.core.database import Base
from datetime import datetime


class TestResult(Base):
    """测试结果记录表"""
    __tablename__ = "test_results"
    
    id = Column(Integer, primary_key=True, index=True)
    test_run_id = Column(String(50), nullable=False, index=True, comment="测试运行ID")
    test_type = Column(String(20), nullable=False, comment="测试类型: unit/integration")
    test_suite = Column(String(100), nullable=False, comment="测试套件名称")
    test_name = Column(String(200), nullable=False, comment="测试名称")
    status = Column(String(20), nullable=False, comment="测试状态: passed/failed/skipped/error")
    duration = Column(Float, comment="测试执行时间(秒)")
    error_message = Column(Text, comment="错误信息")
    stack_trace = Column(Text, comment="堆栈跟踪")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "test_run_id": self.test_run_id,
            "test_type": self.test_type,
            "test_suite": self.test_suite,
            "test_name": self.test_name,
            "status": self.status,
            "duration": self.duration,
            "error_message": self.error_message,
            "stack_trace": self.stack_trace,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class TestRun(Base):
    """测试运行记录表"""
    __tablename__ = "test_runs"
    
    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String(50), unique=True, nullable=False, index=True, comment="运行ID")
    run_type = Column(String(20), nullable=False, comment="运行类型: scheduled/manual")
    start_time = Column(DateTime, nullable=False, comment="开始时间")
    end_time = Column(DateTime, comment="结束时间")
    total_tests = Column(Integer, default=0, comment="总测试数")
    passed_tests = Column(Integer, default=0, comment="通过测试数")
    failed_tests = Column(Integer, default=0, comment="失败测试数")
    skipped_tests = Column(Integer, default=0, comment="跳过测试数")
    error_tests = Column(Integer, default=0, comment="错误测试数")
    duration = Column(Float, comment="总执行时间(秒)")
    status = Column(String(20), nullable=False, comment="运行状态: running/completed/failed")
    trigger_user = Column(String(50), comment="触发用户")
    environment = Column(JSON, comment="环境信息")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "run_id": self.run_id,
            "run_type": self.run_type,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "total_tests": self.total_tests,
            "passed_tests": self.passed_tests,
            "failed_tests": self.failed_tests,
            "skipped_tests": self.skipped_tests,
            "error_tests": self.error_tests,
            "duration": self.duration,
            "status": self.status,
            "trigger_user": self.trigger_user,
            "environment": self.environment,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "success_rate": round((self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0, 2)
        }