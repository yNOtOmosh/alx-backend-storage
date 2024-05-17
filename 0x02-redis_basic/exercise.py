#!/usr/bin/env python3
"""Writing strings to Redis."""
import uuid
import redis
from functools import wraps


def count_calls(method: Callable) -> Callable:
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        key = self.__class__.__name__ + "." + method.__qualname__
        self._redis.incr(key)
        return method(self, *args, **kwargs)
    return wrapper

@count_calls
def call_history(method: Callable) -> Callable:
    """store the history of inputs and outputs for a particular function"""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        key_in = self.__class__.__name__ + "." + method.__qualname__ + ":inputs"
        key_out = self.__class__.__name__ + "." + method.__qualname__ + ":outputs"
        self._redis.rpush(key_in, str(args))
        output = method(self, *args, **kwargs)
        self._redis.rpush(key_out, str(output))
        return output
    return wrapper

def replay(method: Callable) -> None:
    """Display the history of calls of a particular function."""
    key_in = method.__qualname__ + ":inputs"
    key_out = method.__qualname__ + ":outputs"
    inputs = cache._redis.lrange(key_in, 0, -1)
    outputs = cache._redis.lrange(key_out, 0, -1)
    print(f"{method.__qualname__} was called {len(inputs)} times:")
    for input, output in zip(inputs, outputs):
        print(f"{method.__qualname__}(*{input}) -> {output}")

class Cache:
    """Is the object storing data in redis data storage."""
    def __init__(self) -> None:
        self._redis = redis.Redis()
        self._redis.flushdb()

    def store(self, data: Union[str, bytes, int, float]) -> str:
        """stores value in redis data storage and return key"""
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(self, key: str, fn: Callable[[bytes], Any] = None) -> Any:
        """Get the data from redis data storage.

        Args:
            key: The key to get the data.
            fn: The callable to convert the data to the desired format.

        Returns:
            The data or None if the key does not exist.
        """
        data = self._redis.get(key)
        if data is None:
            return None
        if fn is not None:
            return fn(data)
        return data

    def get_str(self, key: str) -> str:
        """Get the data from redis data storage and convert it to a string.

        Args:
            key: The key to get the data.

        Returns:
            The data as a string or None if the key does not exist.
        """
        return self.get(key, lambda d: d.decode("utf-8"))

    def get_int(self, key: str) -> int:
        """Get the data from redis data storage and convert it to an integer.

        Args:
            key: The key to get the data.

        Returns:
            The data as an integer or None if the key does not exist.
        """
        return self.get(key, int)
