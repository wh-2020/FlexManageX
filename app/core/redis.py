import redis.asyncio as redis
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class RedisClient:
    def __init__(self):
        self.redis_url = settings.REDIS_URL
        self.client = None
    
    async def connect(self):
        """连接到Redis"""
        try:
            self.client = await redis.from_url(self.redis_url)
            logger.info("Redis连接成功")
        except Exception as e:
            logger.error(f"Redis连接失败: {e}")
            raise
    
    async def disconnect(self):
        """断开Redis连接"""
        if self.client:
            await self.client.close()
            logger.info("Redis连接已关闭")
    
    async def set(self, key: str, value: str, expire: int = None):
        """设置键值对"""
        await self.client.set(key, value)
        if expire:
            await self.client.expire(key, expire)
    
    async def get(self, key: str):
        """获取值"""
        return await self.client.get(key)
    
    async def delete(self, key: str):
        """删除键"""
        await self.client.delete(key)
    
    async def exists(self, key: str):
        """检查键是否存在"""
        return await self.client.exists(key)

# 创建Redis客户端实例
redis_client = RedisClient() 