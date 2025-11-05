from src.core.redis_core import get_redis_client
from fastapi import Depends
from redis.asyncio import Redis
from typing import Annotated

RedisClient = Annotated[
    Redis,
    Depends(get_redis_client)
]
