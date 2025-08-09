from pydantic_settings import BaseSettings
import secrets

class Settings(BaseSettings):
    app_name: str = "弱电工程ERP系统"
    version: str = "1.0.0"
    debug: bool = True
    
    # 数据库配置（暂时用SQLite）
    database_url: str = "sqlite:///./erp.db"
    
    # 安全配置
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8天
    ALGORITHM: str = "HS256"
    
    # CORS配置
    backend_cors_origins: list = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://18.219.25.24:3000",
        "http://18.219.25.24:8080"
    ]
    
    class Config:
        env_file = ".env"

settings = Settings()