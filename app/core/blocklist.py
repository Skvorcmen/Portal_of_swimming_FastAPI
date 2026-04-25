import redis.asyncio as redis
from app.core.config import settings

class BlocklistService:
    def __init__(self):
        self.redis_client = None
    
    async def get_redis(self):
        if self.redis_client is None:
            self.redis_client = await redis.from_url(settings.REDIS_URL, decode_responses=True)
        return self.redis_client
    
    async def is_ip_blocked(self, ip: str) -> bool:
        r = await self.get_redis()
        blocked = await r.get(f"blocked:{ip}")
        return blocked is not None
    
    async def record_failed_attempt(self, ip: str) -> bool:
        r = await self.get_redis()
        key = f"failed:{ip}"
        attempts = await r.incr(key)
        await r.expire(key, 900)
        if attempts >= 10:
            await r.setex(f"blocked:{ip}", 900, "1")
            return True
        return False
    
    async def reset_attempts(self, ip: str) -> None:
        r = await self.get_redis()
        await r.delete(f"failed:{ip}")

blocklist_service = BlocklistService()

async def is_ip_blocked(ip: str) -> bool:
    return await blocklist_service.is_ip_blocked(ip)

async def record_failed_attempt(ip: str) -> bool:
    return await blocklist_service.record_failed_attempt(ip)

async def reset_attempts(ip: str) -> None:
    await blocklist_service.reset_attempts(ip)
