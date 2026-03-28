"""Dunks & Threes EPM data fetcher."""

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


def get_epm_data(player_name: str, player_id: int) -> dict:
    """Fetch EPM data from Dunks & Threes."""
    cached = get_cached(str(player_id), "dunks_threes", TTL_PLAYER_STATS)
    if cached:
        return cached

    empty = {"epm": None, "o_epm": None, "d_epm": None, "wins_added": None}

    try:
        _rate_limit()
        resp = httpx.get(
            "https://dunksandthrees.com/epm",
            headers=HEADERS,
            timeout=15,
            follow_redirects=True,
        )
        if resp.status_code != 200:
            print(f"WARNING: dunksandthrees returned {resp.status_code}")
            set_cached(str(player_id), "dunks_threes", empty)
            return empty

        html = resp.text
        last_name = player_name.split()[-1].lower()

        # Try to find embedded JSON data
        json_match = re.search(r'data\s*=\s*(\[.*?\]);', html, re.DOTALL)
        if json_match:
            import json
            try:
                data = json.loads(json_match.group(1))
                for row in data:
                    name = row.get("name", "").lower()
                    if last_name in name and player_name.split()[0].lower() in name:
                        result = {
                            "epm": row.get("epm"),
                            "o_epm": row.get("o_epm") or row.get("oepm"),
                            "d_epm": row.get("d_epm") or row.get("depm"),
                            "wins_added": row.get("wins_added") or row.get("wa"),
                        }
                        set_cached(str(player_id), "dunks_threes", result)
                        return result
            except Exception:
                pass

        # Try HTML table parsing
        rows = re.findall(r'<tr[^>]*>(.*?)</tr>', html, re.DOTALL)
        for row in rows:
            if last_name in row.lower() and player_name.split()[0].lower()[:3] in row.lower():
                cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
                cells = [re.sub(r'<[^>]+>', '', c).strip() for c in cells]
                if len(cells) >= 4:
                    result = dict(empty)
                    for i, cell in enumerate(cells):
                        try:
                            val = float(cell)
                            if result["epm"] is None:
                                result["epm"] = val
                            elif result["o_epm"] is None:
                                result["o_epm"] = val
                            elif result["d_epm"] is None:
                                result["d_epm"] = val
                            elif result["wins_added"] is None:
                                result["wins_added"] = val
                        except ValueError:
                            continue
                    set_cached(str(player_id), "dunks_threes", result)
                    return result

    except Exception as e:
        print(f"WARNING: dunksandthrees fetch failed for {player_name}: {e}")

    # Fallback: search
    try:
        _rate_limit()
        resp = httpx.get(
            "https://html.duckduckgo.com/html/",
            params={"q": f"{player_name} EPM dunksandthrees 2025-26"},
            headers=HEADERS, timeout=15, follow_redirects=True,
        )
        if resp.status_code == 200:
            m = re.search(r'EPM[:\s]+([+-]?\d+\.?\d*)', resp.text)
            if m:
                result = dict(empty)
                result["epm"] = float(m.group(1))
                set_cached(str(player_id), "dunks_threes", result)
                return result
    except Exception:
        pass

    set_cached(str(player_id), "dunks_threes", empty)
    return empty


def get_epm_data_bulk(players: list[dict]) -> dict[str, dict]:
    results = {}
    for p in players:
        name = p.get("name") or p.get("player_name", "")
        pid = p.get("id") or p.get("player_id", 0)
        results[name] = get_epm_data(name, pid)
    return results
