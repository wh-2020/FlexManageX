from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

class Settings(BaseSettings):
    # 应用配置
    APP_PORT: int = int(os.getenv("APP_PORT", 8099))

    # 数据库配置
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", 3306))
    DB_USER: str = os.getenv("DB_USER", "init")
    DB_PWD: str = os.getenv("DB_PWD", "")
    DB_DATABASE: str = os.getenv("DB_DATABASE", "")
    
    # Redis配置
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://default:zCWMTGs7Wmzp4B3Z@localhost:20112")
    
    # JWT配置
    JWT_SECRET: str = os.getenv("JWT_SECRET", "d0!doc15415B0*4G0`")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 1440))
    
    # 是否预览环境
    # IS_PREVIEW: bool = os.getenv("IS_PREVIEW", "false").lower() == "true"
    IS_PREVIEW: bool = "true"
    
    # 数据库连接URL
    @property
    def DATABASE_URL(self) -> str:
        return f"mysql://{self.DB_USER}:{self.DB_PWD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_DATABASE}"

# 创建设置实例
settings = Settings() 
