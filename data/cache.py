"""JSON file-based cache with TTL."""

import json
import time
from pathlib import Path
from config import CACHE_DIR


def _cache_path(key: str) -> Path:
    return CACHE_DIR / f"{key}.json"


def load_cache(key: str, ttl: int) -> dict | list | None:
    path = _cache_path(key)
    if not path.exists():
        return None
    try:
        raw = json.loads(path.read_text())
        if time.time() - raw.get("_timestamp", 0) > ttl:
            return None
        return raw["data"]
    except (json.JSONDecodeError, KeyError):
        return None


def save_cache(key: str, data) -> None:
    path = _cache_path(key)
    payload = {"_timestamp": time.time(), "data": data}
    path.write_text(json.dumps(payload, default=str))


def invalidate(key: str) -> None:
    path = _cache_path(key)
    if path.exists():
        path.unlink()


def invalidate_all() -> None:
    for f in CACHE_DIR.glob("*.json"):
        f.unlink()
