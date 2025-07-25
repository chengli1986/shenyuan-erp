# backend/app/core/database.py
"""
数据库配置文件
负责连接和管理数据库
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# 数据库连接URL - 暂时使用SQLite进行开发测试
# SQLite是一个文件数据库，不需要安装PostgreSQL
DATABASE_URL = "sqlite:///./erp_test.db"

# 创建数据库引擎
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False}  # SQLite需要这个参数
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基础模型类
Base = declarative_base()

def get_db():
    """
    获取数据库会话
    这是一个依赖注入函数，FastAPI会自动调用
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()