"""SQLite-backed analytics cache with TTL support."""

import json
import time
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "cache" / "analytics.db"

TTL_PLAYER_STATS = 86400      # 24 hours
TTL_ANALYST_CONTENT = 172800   # 48 hours
TTL_ADVANCED_METRICS = 86400   # 24 hours


def _get_conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS analytics_cache (
            player_id TEXT NOT NULL,
            source TEXT NOT NULL,
            data_json TEXT NOT NULL,
            fetched_at REAL NOT NULL,
            PRIMARY KEY (player_id, source)
        )
    """)
    conn.commit()
    return conn


def get_cached(player_id: str, source: str, ttl: int = TTL_PLAYER_STATS) -> dict | None:
    conn = _get_conn()
    try:
        row = conn.execute(
            "SELECT data_json, fetched_at FROM analytics_cache WHERE player_id = ? AND source = ?",
            (str(player_id), source),
        ).fetchone()
        if row is None:
            return None
        data_json, fetched_at = row
        if time.time() - fetched_at > ttl:
            return None
        return json.loads(data_json)
    finally:
        conn.close()


def set_cached(player_id: str, source: str, data: dict) -> None:
    conn = _get_conn()
    try:
        conn.execute(
            """INSERT OR REPLACE INTO analytics_cache (player_id, source, data_json, fetched_at)
               VALUES (?, ?, ?, ?)""",
            (str(player_id), source, json.dumps(data, default=str), time.time()),
        )
        conn.commit()
    finally:
        conn.close()


def get_all_for_player(player_id: str) -> dict[str, dict]:
    conn = _get_conn()
    try:
        rows = conn.execute(
            "SELECT source, data_json, fetched_at FROM analytics_cache WHERE player_id = ?",
            (str(player_id),),
        ).fetchall()
        result = {}
        for source, data_json, fetched_at in rows:
            result[source] = {"data": json.loads(data_json), "fetched_at": fetched_at}
        return result
    finally:
        conn.close()


def clear_all() -> None:
    conn = _get_conn()
    try:
        conn.execute("DELETE FROM analytics_cache")
        conn.commit()
    finally:
        conn.close()
