"""Analyst content search module.

Searches for recent commentary from 4 analyst sources:
- Thinking Basketball (Ben Taylor)
- Dunc'd On (Nate Duncan / Danny Leroux)
- Cleaning the Glass (Ben Falk)
- Dunks & Threes (Andrew Patton)
"""

import re
import time
import html as html_lib
import httpx
from data.analytics_cache import get_cached, set_cached, TTL_ANALYST_CONTENT

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

ANALYST_SOURCES = [
    {
        "key": "thinking_basketball",
        "name": "Ben Taylor (Thinking Basketball)",
        "search_suffix": 'site:youtube.com "thinking basketball" OR site:thinkingbasketball.net',
    },
    {
        "key": "duncd_on",
        "name": "Nate Duncan (Dunc'd On)",
        "search_suffix": '"dunc\'d on" OR "nate duncan" NBA podcast',
    },
    {
        "key": "cleaning_the_glass",
        "name": "Ben Falk (Cleaning the Glass)",
        "search_suffix": 'site:cleaningtheglass.com OR "cleaning the glass" OR "ben falk"',
    },
    {
        "key": "dunks_and_threes",
        "name": "Andrew Patton (Dunks & Threes)",
        "search_suffix": 'site:dunksandthrees.com OR "dunks and threes" OR "andrew patton" EPM',
    },
]


def _search_ddg(query: str) -> list[dict]:
    """Search DuckDuckGo HTML and parse results."""
    try:
        resp = httpx.get(
            "https://html.duckduckgo.com/html/",
            params={"q": query},
            headers=HEADERS,
            timeout=15,
            follow_redirects=True,
        )
        if resp.status_code != 200:
            return []

        text = resp.text
        results = []

        # Parse result blocks
        blocks = re.findall(
            r'class="result[^"]*"[^>]*>(.*?)</div>\s*</div>',
            text, re.DOTALL
        )
        if not blocks:
            # Fallback: find links
            blocks = re.findall(r'<a[^>]*class="result__a"[^>]*>(.*?)</a>', text, re.DOTALL)

        for block in blocks[:5]:
            # Extract URL
            url_match = re.search(r'href="([^"]+)"', block)
            url = url_match.group(1) if url_match else ""
            if url.startswith("//duckduckgo.com/l/"):
                ud_match = re.search(r'uddg=([^&]+)', url)
                if ud_match:
                    from urllib.parse import unquote
                    url = unquote(ud_match.group(1))

            # Extract title
            title_match = re.search(r'class="result__a"[^>]*>(.*?)</a>', block, re.DOTALL)
            title = re.sub(r'<[^>]+>', '', title_match.group(1)).strip() if title_match else ""

            # Extract snippet
            snippet_match = re.search(r'class="result__snippet"[^>]*>(.*?)</[^>]+>', block, re.DOTALL)
            snippet = re.sub(r'<[^>]+>', '', snippet_match.group(1)).strip() if snippet_match else ""

            # Extract date
            date = None
            date_match = re.search(r'(\d{4}-\d{2}-\d{2}|\w+ \d{1,2},? \d{4})', block)
            if date_match:
                date = date_match.group(1)

            if title or url:
                results.append({
                    "title": html_lib.unescape(title)[:200],
                    "snippet": html_lib.unescape(snippet)[:300],
                    "url": url,
                    "date": date,
                })

        return results[:3]
    except Exception as e:
        print(f"WARNING: DDG search failed: {e}")
        return []


def search_analyst_content(player_name: str, player_id: int, team: str = "") -> dict:
    """Search for recent analyst content about a player."""
    cached = get_cached(str(player_id), "analyst_content", TTL_ANALYST_CONTENT)
    if cached:
        return cached

    result = {"fetched_at": time.time()}

    for source in ANALYST_SOURCES:
        key = source["key"]
        try:
            query = f"{player_name} {team} NBA 2026 {source['search_suffix']}"
            time.sleep(2)  # Rate limit between searches
            search_results = _search_ddg(query)

            most_recent = None
            for r in search_results:
                if r.get("date") and (most_recent is None or r["date"] > most_recent):
                    most_recent = r["date"]

            result[key] = {
                "name": source["name"],
                "results": search_results,
                "most_recent_date": most_recent or "unknown",
            }
        except Exception as e:
            print(f"WARNING: Analyst search failed for {source['name']}: {e}")
            result[key] = {
                "name": source["name"],
                "results": [],
                "most_recent_date": "unknown",
            }

    set_cached(str(player_id), "analyst_content", result)
    return result


def search_analyst_content_bulk(players: list[dict]) -> dict[str, dict]:
    results = {}
    for p in players:
        name = p.get("name") or p.get("player_name", "")
        pid = p.get("id") or p.get("player_id", 0)
        team = p.get("team", "")
        try:
            results[str(pid)] = search_analyst_content(name, pid, team)
        except Exception:
            results[str(pid)] = {}
    return results
