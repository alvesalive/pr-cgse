import os
import redis
import json
import logging

logger = logging.getLogger("cache")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis-cache:6379/1")

redis_client = redis.from_url(REDIS_URL, decode_responses=True)

def set_cache(key: str, data: dict, ex: int = 300):
    try:
        redis_client.setex(key, ex, json.dumps(data))
    except Exception as e:
        logger.error(f"Redis Set Error: {e}")

def get_cache(key: str):
    try:
        val = redis_client.get(key)
        if val:
            return json.loads(val)
        return None
    except Exception as e:
        logger.error(f"Redis Get Error: {e}")
        return None
