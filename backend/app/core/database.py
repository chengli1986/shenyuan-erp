# backend/app/core/database.py
"""
数据库配置文件
负责连接和管理数据库
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

# 从统一配置中读取数据库URL
DATABASE_URL = settings.database_url

# 创建数据库引擎
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False  # SQLite需要这个参数

engine = create_engine(DATABASE_URL, connect_args=connect_args)

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