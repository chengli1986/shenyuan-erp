from pydantic_settings import BaseSettings
from pydantic import ConfigDict
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

    # 数据库驱动和PostgreSQL配置（可选）
    database_driver: str = "sqlite"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "erp_user"
    postgres_password: str = "erp_password_dev"
    postgres_db: str = "erp_dev"

    model_config = ConfigDict(extra="ignore", env_file=".env")

settings = Settings()