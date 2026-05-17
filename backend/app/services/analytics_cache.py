"""
Simple in-memory analytics cache with TTL (10 minutes).
"""
import time
from typing import Any, Optional, Dict, Tuple

_cache: Dict[str, Tuple[Any, float]] = {}
TTL = 600  # 10 minutes


def cache_get(key: str) -> Optional[Any]:
    if key in _cache:
        value, ts = _cache[key]
        if time.time() - ts < TTL:
            return value
        del _cache[key]
    return None


def cache_set(key: str, value: Any):
    _cache[key] = (value, time.time())


def cache_invalidate(key: str):
    _cache.pop(key, None)


def cache_clear():
    _cache.clear()
