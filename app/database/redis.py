import redis.asyncio as redis
from app.config import settings


client = redis.Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    db=0, decode_responses=True
    )


async def blacklist_jti(jti: str) -> None:
    await client.set(jti, "blackedlisted")


async def is_jti_blacklisted(jti: str) -> bool:
    result = await client.get(jti)
    return result is not None
