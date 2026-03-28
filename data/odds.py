"""Betting odds fetcher using The Odds API."""

import httpx
from data.cache import load_cache, save_cache, invalidate
from config import ODDS_API_KEY, CACHE_TTL_ODDS

BASE_URL = "https://api.the-odds-api.com/v4"

# NBA team name mapping (Odds API uses full names, we use abbreviations)
TEAM_NAME_TO_ABBR = {
    "Atlanta Hawks": "ATL", "Boston Celtics": "BOS", "Brooklyn Nets": "BKN",
    "Charlotte Hornets": "CHA", "Chicago Bulls": "CHI", "Cleveland Cavaliers": "CLE",
    "Dallas Mavericks": "DAL", "Denver Nuggets": "DEN", "Detroit Pistons": "DET",
    "Golden State Warriors": "GSW", "Houston Rockets": "HOU", "Indiana Pacers": "IND",
    "Los Angeles Clippers": "LAC", "Los Angeles Lakers": "LAL", "Memphis Grizzlies": "MEM",
    "Miami Heat": "MIA", "Milwaukee Bucks": "MIL", "Minnesota Timberwolves": "MIN",
    "New Orleans Pelicans": "NOP", "New York Knicks": "NYK", "Oklahoma City Thunder": "OKC",
    "Orlando Magic": "ORL", "Philadelphia 76ers": "PHI", "Phoenix Suns": "PHX",
    "Portland Trail Blazers": "POR", "Sacramento Kings": "SAC", "San Antonio Spurs": "SAS",
    "Toronto Raptors": "TOR", "Utah Jazz": "UTA", "Washington Wizards": "WAS",
}

ABBR_TO_TEAM_NAME = {v: k for k, v in TEAM_NAME_TO_ABBR.items()}


def moneyline_to_prob(american_odds: int) -> float:
    """Convert American odds to implied probability."""
    if american_odds > 0:
        return 100 / (american_odds + 100)
    else:
        return abs(american_odds) / (abs(american_odds) + 100)


def _normalize_probs(probs: dict[str, float]) -> dict[str, float]:
    """Remove vig by normalizing probabilities to sum to 1."""
    total = sum(probs.values())
    if total == 0:
        return probs
    return {k: v / total for k, v in probs.items()}


def get_championship_futures() -> dict[str, float]:
    """Get championship win probabilities for each team.
    Returns {team_abbr: probability}.
    """
    cached = load_cache("championship_futures", CACHE_TTL_ODDS)
    if cached:
        return cached

    if not ODDS_API_KEY:
        print("WARNING: No ODDS_API_KEY set. Using default probabilities.")
        return _default_championship_probs()

    print("Fetching championship futures...")
    try:
        resp = httpx.get(
            f"{BASE_URL}/sports/basketball_nba_championship/odds",
            params={
                "apiKey": ODDS_API_KEY,
                "regions": "us",
                "markets": "outrights",
                "oddsFormat": "american",
            },
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()

        # Aggregate across bookmakers
        team_odds = {}
        count = {}
        for event in data:
            for bookmaker in event.get("bookmakers", []):
                for market in bookmaker.get("markets", []):
                    if market["key"] == "outrights":
                        for outcome in market["outcomes"]:
                            name = outcome["name"]
                            abbr = TEAM_NAME_TO_ABBR.get(name)
                            if abbr:
                                prob = moneyline_to_prob(int(outcome["price"]))
                                team_odds[abbr] = team_odds.get(abbr, 0) + prob
                                count[abbr] = count.get(abbr, 0) + 1

        # Average across bookmakers
        result = {}
        for abbr in team_odds:
            result[abbr] = team_odds[abbr] / count[abbr]

        result = _normalize_probs(result)
        save_cache("championship_futures", result)
        print(f"Got championship futures for {len(result)} teams")
        return result

    except Exception as e:
        print(f"Error fetching odds: {e}. Using defaults.")
        return _default_championship_probs()


def get_series_odds() -> list[dict]:
    """Get head-to-head series odds for active playoff matchups.
    Returns [{home_team, away_team, home_prob, away_prob}].
    Only available once playoff matchups are set.
    """
    cached = load_cache("series_odds", CACHE_TTL_ODDS)
    if cached:
        return cached

    if not ODDS_API_KEY:
        print("WARNING: No ODDS_API_KEY set. No series odds available.")
        return []

    print("Fetching series odds...")
    try:
        resp = httpx.get(
            f"{BASE_URL}/sports/basketball_nba/odds",
            params={
                "apiKey": ODDS_API_KEY,
                "regions": "us",
                "markets": "h2h",
                "oddsFormat": "american",
            },
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()

        series = []
        for event in data:
            home = TEAM_NAME_TO_ABBR.get(event.get("home_team", ""))
            away = TEAM_NAME_TO_ABBR.get(event.get("away_team", ""))
            if not home or not away:
                continue

            for bookmaker in event.get("bookmakers", []):
                for market in bookmaker.get("markets", []):
                    if market["key"] == "h2h":
                        probs = {}
                        for outcome in market["outcomes"]:
                            abbr = TEAM_NAME_TO_ABBR.get(outcome["name"])
                            if abbr:
                                probs[abbr] = moneyline_to_prob(int(outcome["price"]))
                        probs = _normalize_probs(probs)
                        if home in probs and away in probs:
                            series.append({
                                "home_team": home,
                                "away_team": away,
                                "home_prob": probs[home],
                                "away_prob": probs[away],
                            })
                        break
                break  # Use first bookmaker

        save_cache("series_odds", series)
        return series

    except Exception as e:
        print(f"Error fetching series odds: {e}")
        return []


def refresh_odds():
    """Invalidate odds cache and re-fetch."""
    invalidate("championship_futures")
    invalidate("series_odds")
    futures = get_championship_futures()
    series = get_series_odds()
    return futures, series


def _default_championship_probs() -> dict[str, float]:
    """Fallback championship probabilities based on typical seed-based expectations.
    These should be manually updated with real odds before draft.
    """
    # Rough defaults - update these with actual odds
    defaults = {
        # East
        "DET": 0.02, "BOS": 0.15, "NYK": 0.10, "CLE": 0.12,
        "ATL": 0.03, "TOR": 0.02, "PHI": 0.02, "ORL": 0.02,
        "CHA": 0.01, "MIA": 0.01,
        # West
        "OKC": 0.18, "SAS": 0.04, "LAL": 0.06, "DEN": 0.08,
        "MIN": 0.05, "HOU": 0.03, "PHX": 0.02, "LAC": 0.01,
        "POR": 0.01, "GSW": 0.02,
    }
    return _normalize_probs(defaults)
