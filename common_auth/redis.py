from redis.asyncio import Redis
from .config import settings
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from common_auth.config import redis_set

redis = Redis(
    host=redis_set.host,
    port=redis_set.port,
    decode_responses=redis_set.decode_responses
)

