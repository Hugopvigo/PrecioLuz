import time

_cache: dict[str, tuple[float, object]] = {}
_DEFAULT_TTL = 600


def get_cached(key: str) -> object | None:
    if key in _cache:
        ts, value = _cache[key]
        if time.monotonic() - ts < _DEFAULT_TTL:
            return value
        del _cache[key]
    return None


def set_cached(key: str, value: object) -> None:
    _cache[key] = (time.monotonic(), value)


def clear_cache() -> None:
    _cache.clear()
