"""NBA stats fetcher using nba_api."""

import time
from nba_api.stats.endpoints import (
    LeagueStandings,
    CommonTeamRoster,
    LeagueDashPlayerStats,
    PlayerCareerStats,
)
from nba_api.stats.static import teams as nba_teams
from data.cache import load_cache, save_cache
from config import (
    SEASON_ID,
    CACHE_TTL_STATS,
    CACHE_TTL_PLAYOFF,
    NBA_API_DELAY,
)


# 2025-26 play-in eligible: top 10 in each conference
PLAY_IN_SEEDS = 10


def get_playoff_eligible_teams() -> list[dict]:
    """Get teams eligible for playoffs/play-in (top 10 each conference)."""
    cached = load_cache("eligible_teams", CACHE_TTL_STATS)
    if cached:
        return cached

    print("Fetching standings...")
    time.sleep(NBA_API_DELAY)
    standings = LeagueStandings(
        season=SEASON_ID,
        season_type="Regular Season",
    )
    df = standings.get_data_frames()[0]

    eligible = []
    for conf in ["East", "West"]:
        conf_teams = df[df["Conference"] == conf].head(PLAY_IN_SEEDS)
        for _, row in conf_teams.iterrows():
            eligible.append({
                "team_id": int(row["TeamID"]),
                "team_name": row["TeamName"],
                "team_city": row["TeamCity"],
                "team_abbr": _get_team_abbr(int(row["TeamID"])),
                "conference": conf,
                "seed": int(row["PlayoffRank"]),
                "wins": int(row["WINS"]),
                "losses": int(row["LOSSES"]),
            })

    save_cache("eligible_teams", eligible)
    print(f"Found {len(eligible)} playoff-eligible teams")
    return eligible


def _get_team_abbr(team_id: int) -> str:
    for t in nba_teams.get_teams():
        if t["id"] == team_id:
            return t["abbreviation"]
    return "???"


def get_rosters(teams: list[dict]) -> list[dict]:
    """Get rosters for all eligible teams."""
    cached = load_cache("rosters", CACHE_TTL_STATS)
    if cached:
        return cached

    players = []
    for i, team in enumerate(teams):
        print(f"Fetching roster {i+1}/{len(teams)}: {team['team_abbr']}...")
        time.sleep(NBA_API_DELAY)
        roster = CommonTeamRoster(
            team_id=team["team_id"],
            season=SEASON_ID,
        )
        df = roster.get_data_frames()[0]
        for _, row in df.iterrows():
            players.append({
                "player_id": int(row["PLAYER_ID"]),
                "player_name": row["PLAYER"],
                "team_id": team["team_id"],
                "team_abbr": team["team_abbr"],
                "team_seed": team["seed"],
                "conference": team["conference"],
                "position": row.get("POSITION", ""),
            })

    save_cache("rosters", players)
    print(f"Found {len(players)} players on eligible teams")
    return players


def get_season_averages() -> dict:
    """Get current season per-game averages for all players. Returns {player_id: stats}."""
    cached = load_cache("season_averages", CACHE_TTL_STATS)
    if cached:
        return cached

    print("Fetching season averages (bulk)...")
    time.sleep(NBA_API_DELAY)
    stats = LeagueDashPlayerStats(
        season=SEASON_ID,
        season_type_all_star="Regular Season",
        per_mode_detailed="PerGame",
    )
    df = stats.get_data_frames()[0]

    result = {}
    for _, row in df.iterrows():
        pid = int(row["PLAYER_ID"])
        result[pid] = {
            "pts": float(row["PTS"]),
            "reb": float(row["REB"]),
            "ast": float(row["AST"]),
            "min": float(row["MIN"]),
            "gp": int(row["GP"]),
            "fga": float(row["FGA"]),
            "fta": float(row["FTA"]),
            "tov": float(row["TOV"]),
        }

    save_cache("season_averages", result)
    print(f"Got season averages for {len(result)} players")
    return result


def get_usage_rates() -> dict:
    """Get usage rates for all players. Returns {player_id: usg_pct}."""
    cached = load_cache("usage_rates", CACHE_TTL_STATS)
    if cached:
        return cached

    print("Fetching usage rates (bulk)...")
    time.sleep(NBA_API_DELAY)
    stats = LeagueDashPlayerStats(
        season=SEASON_ID,
        season_type_all_star="Regular Season",
        per_mode_detailed="PerGame",
        measure_type_detailed_defense="Advanced",
    )
    df = stats.get_data_frames()[0]

    result = {}
    for _, row in df.iterrows():
        pid = int(row["PLAYER_ID"])
        result[pid] = {
            "usg_pct": float(row.get("USG_PCT", 0)),
        }

    save_cache("usage_rates", result)
    print(f"Got usage rates for {len(result)} players")
    return result


def get_career_playoff_stats(player_ids: list[int]) -> dict:
    """Get career playoff stats for each player. Returns {player_id: stats_dict | None}.
    This is the SLOW call - one API request per player.
    """
    cached = load_cache("career_playoff", CACHE_TTL_PLAYOFF)
    if cached:
        return cached

    result = {}
    total = len(player_ids)
    for i, pid in enumerate(player_ids):
        if (i + 1) % 10 == 0 or i == 0:
            print(f"Fetching career stats {i+1}/{total}...")
        time.sleep(NBA_API_DELAY)
        try:
            career = PlayerCareerStats(
                player_id=pid,
                per_mode36="PerGame",
            )
            dfs = career.get_data_frames()

            # Regular season career totals (last row of SeasonTotalsRegularSeason)
            reg_df = dfs[0]  # SeasonTotalsRegularSeason
            playoff_df = dfs[2] if len(dfs) > 2 else None  # SeasonTotalsPostSeason

            reg_stats = None
            if not reg_df.empty:
                # Get career averages by averaging across seasons weighted by GP
                total_gp = reg_df["GP"].sum()
                if total_gp > 0:
                    reg_stats = {
                        "pts": float((reg_df["PTS"] * reg_df["GP"]).sum() / total_gp),
                        "reb": float((reg_df["REB"] * reg_df["GP"]).sum() / total_gp),
                        "ast": float((reg_df["AST"] * reg_df["GP"]).sum() / total_gp),
                        "min": float((reg_df["MIN"] * reg_df["GP"]).sum() / total_gp),
                        "gp": int(total_gp),
                    }

            playoff_stats = None
            if playoff_df is not None and not playoff_df.empty:
                total_gp = playoff_df["GP"].sum()
                if total_gp > 0:
                    playoff_stats = {
                        "pts": float((playoff_df["PTS"] * playoff_df["GP"]).sum() / total_gp),
                        "reb": float((playoff_df["REB"] * playoff_df["GP"]).sum() / total_gp),
                        "ast": float((playoff_df["AST"] * playoff_df["GP"]).sum() / total_gp),
                        "min": float((playoff_df["MIN"] * playoff_df["GP"]).sum() / total_gp),
                        "gp": int(total_gp),
                    }

            result[str(pid)] = {
                "regular_season": reg_stats,
                "playoffs": playoff_stats,
            }

        except Exception as e:
            print(f"  Error fetching player {pid}: {e}")
            result[str(pid)] = {"regular_season": None, "playoffs": None}

    save_cache("career_playoff", result)
    print(f"Got career playoff stats for {len(result)} players")
    return result
