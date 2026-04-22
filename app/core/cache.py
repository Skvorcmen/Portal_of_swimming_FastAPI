import redis.asyncio as redis
import json
from typing import Optional, Any
from functools import wraps

redis_client = None


async def get_redis():
    global redis_client
    if redis_client is None:
        redis_client = await redis.from_url("redis://localhost:6379/0", decode_responses=True)
    return redis_client


async def set_cache(key: str, value: Any, expire: int = 300) -> None:
    r = await get_redis()
    await r.setex(key, expire, json.dumps(value, default=str))


async def get_cache(key: str) -> Optional[Any]:
    r = await get_redis()
    data = await r.get(key)
    if data:
        return json.loads(data)
    return None


async def delete_cache(key: str) -> None:
    r = await get_redis()
    await r.delete(key)


async def clear_cache_pattern(pattern: str) -> None:
    r = await get_redis()
    keys = await r.keys(pattern)
    if keys:
        await r.delete(*keys)


def cached(expire: int = 300, key_prefix: str = ""):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Исключаем service из ключа кэша (все Depends объекты)
            filtered_kwargs = {k: v for k, v in kwargs.items() if k != "service"}
            
            cache_key = f"{key_prefix}:{func.__name__}:{str(args)}:{str(sorted(filtered_kwargs.items()))}"
            
            cached_data = await get_cache(cache_key)
            if cached_data is not None:
                return cached_data
            
            result = await func(*args, **kwargs)
            await set_cache(cache_key, result, expire)
            return result
        return wrapper
    return decorator
