from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "弱电工程ERP系统"
    version: str = "1.0.0"
    debug: bool = True
    
    # 数据库配置（暂时用SQLite）
    database_url: str = "sqlite:///./erp.db"
    
    class Config:
        env_file = ".env"

settings = Settings()