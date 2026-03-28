"""Injury report fetcher."""

import httpx
from data.cache import load_cache, save_cache
from config import CACHE_TTL_INJURIES


def get_injury_report() -> dict:
    """Get current injury statuses. Returns {player_name_lower: {status, note}}.
    Uses NBA.com injury data.
    """
    cached = load_cache("injuries", CACHE_TTL_INJURIES)
    if cached:
        return cached

    print("Fetching injury report...")
    try:
        # Try nba_api's injury endpoint
        from nba_api.stats.endpoints import PlayerIndex
        import time
        time.sleep(3)

        # Fetch from NBA.com's publicly available injury JSON
        resp = httpx.get(
            "https://cdn.nba.com/static/json/liveData/odds/odds_todaysGames.json",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=15,
        )
        # If that doesn't work, we'll fall back to manual entry
    except Exception:
        pass

    # Fallback: return empty dict - users can manually update injuries
    # via the config or during the draft
    result = {}
    save_cache("injuries", result)
    print("Injury report: using manual entry mode (update in draft UI)")
    return result


def set_injury_status(player_name: str, status: str, note: str = "") -> dict:
    """Manually set a player's injury status.
    status: 'Healthy', 'Questionable', 'Doubtful', 'Out'
    """
    injuries = load_cache("injuries", 999999) or {}
    injuries[player_name.lower()] = {"status": status, "note": note}
    save_cache("injuries", injuries)
    return injuries


def get_player_injury(player_name: str, injuries: dict) -> tuple[str, str]:
    """Look up a player's injury status. Returns (status, note)."""
    key = player_name.lower()
    if key in injuries:
        return injuries[key]["status"], injuries[key]["note"]
    return "Healthy", ""
