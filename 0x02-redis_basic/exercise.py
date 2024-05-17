#!/usr/bin/env python3
"""Writing strings to Redis."""
import uuid
import redis


class Cache:
    """Is the object storing data in redis data storage."""
    def __init__(self) -> None:
        self._redis = redis.Redis()
        self._redis.flushdb()

    def store(self, data: Union[str, bytes, int, float]) -> str:
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key
