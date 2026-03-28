"""BBall Index LEBRON ratings fetcher."""

import re
import time
import httpx
from data.analytics_cache import get_cached, set_cached, TTL_PLAYER_STATS

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
_last_request = 0.0


def _rate_limit():
    global _last_request
    elapsed = time.time() - _last_request
    if elapsed < 3.0:
        time.sleep(3.0 - elapsed)
    _last_request = time.time()


def _search_duckduckgo(query: str) -> str:
    """Search DuckDuckGo HTML version and return page text."""
    try:
        resp = httpx.get(
            "https://html.duckduckgo.com/html/",
            params={"q": query},
            headers=HEADERS,
            timeout=15,
            follow_redirects=True,
        )
        return resp.text if resp.status_code == 200 else ""
    except Exception:
        return ""


def _extract_float(text: str, pattern: str) -> float | None:
    """Extract a float value near a label in text."""
    m = re.search(pattern, text, re.IGNORECASE)
    if m:
        try:
            return float(m.group(1))
        except (ValueError, IndexError):
            pass
    return None


def get_lebron_ratings(player_name: str, player_id: int) -> dict:
    """Fetch LEBRON ratings from BBall Index."""
    cached = get_cached(str(player_id), "bball_index", TTL_PLAYER_STATS)
    if cached:
        return cached

    empty = {
        "lebron": None, "o_lebron": None, "d_lebron": None,
        "defensive_playmaking": None, "shot_making": None, "shooting_talent": None,
    }

    try:
        # Try fetching the ratings page directly
        _rate_limit()
        resp = httpx.get(
            "https://www.bball-index.com/nba-player-ratings/",
            headers=HEADERS,
            timeout=15,
            follow_redirects=True,
        )
        if resp.status_code == 200 and player_name.split()[-1].lower() in resp.text.lower():
            # Try to parse from the page
            text = resp.text
            # Look for player's row in any table
            name_pattern = re.escape(player_name.split()[-1])
            # This is JS-rendered so likely won't work, fall through to search
    except Exception:
        pass

    # Fallback: web search for the player's LEBRON rating
    try:
        _rate_limit()
        query = f"{player_name} LEBRON rating bball-index 2025-26"
        html = _search_duckduckgo(query)
        if html:
            result = dict(empty)
            # Try to extract numbers from search snippets
            result["lebron"] = _extract_float(html, r"LEBRON[:\s]+([+-]?\d+\.?\d*)")
            result["o_lebron"] = _extract_float(html, r"O-LEBRON[:\s]+([+-]?\d+\.?\d*)")
            result["d_lebron"] = _extract_float(html, r"D-LEBRON[:\s]+([+-]?\d+\.?\d*)")
            result["shot_making"] = _extract_float(html, r"[Ss]hot\s*[Mm]aking[:\s]+([+-]?\d+\.?\d*)")
            set_cached(str(player_id), "bball_index", result)
            return result
    except Exception as e:
        print(f"WARNING: bball-index fetch failed for {player_name}: {e}")

    set_cached(str(player_id), "bball_index", empty)
    return empty


def get_lebron_ratings_bulk(players: list[dict]) -> dict[str, dict]:
    results = {}
    for p in players:
        name = p.get("name") or p.get("player_name", "")
        pid = p.get("id") or p.get("player_id", 0)
        results[name] = get_lebron_ratings(name, pid)
    return results
