from tortoise import Tortoise
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

async def init_db():
    """初始化数据库连接"""
    logger.info("正在初始化数据库连接...")
    
    # 使用最简单的连接配置，避免所有复杂参数
    db_url = f"mysql://{settings.DB_USER}:{settings.DB_PWD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_DATABASE}"
    
    # 初始化Tortoise ORM
    await Tortoise.init(
        db_url=db_url,
        modules={
            "models": [
                "app.models.user", 
                "app.models.role", 
                "app.models.permission",
            ]
        }
    )
    # 生成表结构
    await Tortoise.generate_schemas()
    logger.info("数据库连接初始化完成")

async def close_db():
    """关闭数据库连接"""
    logger.info("正在关闭数据库连接...")
    await Tortoise.close_connections()
    logger.info("数据库连接已关闭") 
