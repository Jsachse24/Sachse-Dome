"""Basketball Reference advanced stats scraper."""

import re
import time
import unicodedata
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


def _player_slug(name: str) -> str:
    """Convert player name to bbref slug. E.g. 'LeBron James' -> 'jamesle01'."""
    # Normalize unicode (accents etc)
    name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    parts = name.strip().split()
    if len(parts) < 2:
        return name.lower()[:7] + "01"
    first = parts[0].lower().replace("'", "").replace(".", "")
    # Handle multi-word last names (e.g. Gilgeous-Alexander)
    last = "".join(parts[1:]).lower().replace("'", "").replace(".", "").replace("-", "")
    slug = (last[:5] + first[:2]).ljust(7, "x") + "01"
    return slug


def _extract_table(html: str, table_id: str) -> str | None:
    """Extract a table from bbref HTML, checking inside comments too."""
    # Direct search
    pattern = f'id="{table_id}"'
    if pattern in html:
        start = html.find(pattern)
        table_start = html.rfind("<table", max(0, start - 200), start)
        table_end = html.find("</table>", start)
        if table_start != -1 and table_end != -1:
            return html[table_start:table_end + 8]
    # Search inside comments (bbref hides many tables in comments)
    for m in re.finditer(r"<!--(.*?)-->", html, re.DOTALL):
        comment = m.group(1)
        if pattern in comment:
            start = comment.find(pattern)
            table_start = comment.rfind("<table", max(0, start - 200), start)
            table_end = comment.find("</table>", start)
            if table_start != -1 and table_end != -1:
                return comment[table_start:table_end + 8]
    return None


def _parse_row_values(table_html: str, season: str = "2025-26") -> dict:
    """Parse a season row from an advanced stats table."""
    result = {}
    # Find the row for the target season
    rows = re.findall(r"<tr[^>]*>(.*?)</tr>", table_html, re.DOTALL)
    target_row = None
    for row in rows:
        if season in row:
            target_row = row
            break
    if not target_row:
        # Try last data row
        data_rows = [r for r in rows if "<td" in r and "<th" not in r.replace("<thead", "")]
        if data_rows:
            target_row = data_rows[-1]
    if not target_row:
        return result

    cells = re.findall(r'data-stat="([^"]+)"[^>]*>([^<]*)<', target_row)
    for stat_name, value in cells:
        try:
            result[stat_name] = float(value) if value and value != "" else None
        except ValueError:
            result[stat_name] = value if value else None
    return result


def get_advanced_stats(player_name: str, player_id: int) -> dict:
    """Fetch BPM, VORP, TS%, USG%, and playoff splits from Basketball Reference."""
    cached = get_cached(str(player_id), "bbref", TTL_PLAYER_STATS)
    if cached:
        return cached

    slug = _player_slug(player_name)
    first_letter = slug[0] if slug else "a"
    url = f"https://www.basketball-reference.com/players/{first_letter}/{slug}.html"

    empty = {
        "bpm": None, "vorp": None, "ts_pct": None, "usg_pct": None,
        "ows": None, "dws": None, "ws": None,
        "playoff_bpm": None, "playoff_ts_pct": None,
        "bpm_delta": None, "ts_delta": None,
    }

    try:
        _rate_limit()
        resp = httpx.get(url, headers=HEADERS, timeout=15, follow_redirects=True)
        if resp.status_code != 200:
            print(f"WARNING: bbref returned {resp.status_code} for {player_name}")
            set_cached(str(player_id), "bbref", empty)
            return empty

        html = resp.text
        result = dict(empty)

        # Parse advanced table
        adv_table = _extract_table(html, "advanced")
        if adv_table:
            vals = _parse_row_values(adv_table)
            result["bpm"] = vals.get("bpm")
            result["vorp"] = vals.get("vorp")
            result["ts_pct"] = vals.get("ts_pct")
            result["usg_pct"] = vals.get("usg_pct")
            result["ows"] = vals.get("ows")
            result["dws"] = vals.get("dws")
            result["ws"] = vals.get("ws")

        # Parse playoff advanced table
        po_table = _extract_table(html, "playoffs_advanced")
        if po_table:
            # Average last 3 playoff seasons
            rows = re.findall(r"<tr[^>]*>(.*?)</tr>", po_table, re.DOTALL)
            po_bpms = []
            po_ts = []
            for row in rows[-5:]:  # check last 5 rows to find up to 3 seasons
                cells = dict(re.findall(r'data-stat="([^"]+)"[^>]*>([^<]*)<', row))
                try:
                    if cells.get("bpm"):
                        po_bpms.append(float(cells["bpm"]))
                    if cells.get("ts_pct"):
                        po_ts.append(float(cells["ts_pct"]))
                except (ValueError, KeyError):
                    pass

            if po_bpms:
                result["playoff_bpm"] = round(sum(po_bpms[-3:]) / len(po_bpms[-3:]), 1)
            if po_ts:
                result["playoff_ts_pct"] = round(sum(po_ts[-3:]) / len(po_ts[-3:]), 3)

        # Calculate deltas
        if result["bpm"] is not None and result["playoff_bpm"] is not None:
            result["bpm_delta"] = round(result["playoff_bpm"] - result["bpm"], 1)
        if result["ts_pct"] is not None and result["playoff_ts_pct"] is not None:
            result["ts_delta"] = round(result["playoff_ts_pct"] - result["ts_pct"], 3)

        set_cached(str(player_id), "bbref", result)
        return result

    except Exception as e:
        print(f"WARNING: bbref fetch failed for {player_name}: {e}")
        set_cached(str(player_id), "bbref", empty)
        return empty


def get_advanced_stats_bulk(players: list[dict]) -> dict[str, dict]:
    """Fetch advanced stats for multiple players."""
    results = {}
    for p in players:
        name = p.get("name") or p.get("player_name", "")
        pid = p.get("id") or p.get("player_id", 0)
        results[name] = get_advanced_stats(name, pid)
    return results
