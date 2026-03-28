"""Player dataclass and player pool builder."""

from dataclasses import dataclass, field


@dataclass
class Player:
    player_id: int
    name: str
    team: str
    position: str
    conference: str
    seed: int

    # Season averages
    pts: float = 0.0
    reb: float = 0.0
    ast: float = 0.0
    min: float = 0.0
    games_played: int = 0
    usg_pct: float = 0.0

    # Derived
    season_fantasy_avg: float = 0.0  # pts + reb + ast per game

    # Playoff adjustment
    playoff_adj_factor: float = 1.0
    has_playoff_history: bool = False
    adj_details: dict = field(default_factory=dict)

    # Games estimation
    expected_games: float = 0.0
    games_breakdown: dict = field(default_factory=dict)

    # Final projection
    projected_fantasy_pts: float = 0.0
    rank: int = 0
    tier: str = ""

    # Injury
    injury_status: str = "Healthy"
    injury_note: str = ""

    # Draft state
    is_drafted: bool = False
    drafted_by: int | None = None  # team number 1-10
    draft_pick: int | None = None


def build_player_pool(
    rosters: list[dict],
    season_avgs: dict,
    usage_rates: dict,
    career_playoff: dict,
    championship_futures: dict,
    series_odds: list[dict],
    injuries: dict,
    eligible_teams: list[dict],
) -> list[Player]:
    """Build the complete player pool with all projections."""
    from model.games import calc_expected_total_games
    from model.adjustment import calc_playoff_adjustment
    from model.projections import project_all, get_value_tiers
    from data.injuries import get_player_injury

    # Build team lookup
    team_info = {t["team_abbr"]: t for t in eligible_teams}

    # Calculate expected games per team (cache to avoid recalculating)
    team_games = {}
    for team in eligible_teams:
        abbr = team["team_abbr"]
        champ_prob = championship_futures.get(abbr, 0.01)
        total_games, breakdown = calc_expected_total_games(
            abbr, team["seed"], team["conference"],
            champ_prob, series_odds,
        )
        team_games[abbr] = (total_games, breakdown)

    players = []
    for roster_entry in rosters:
        pid = roster_entry["player_id"]
        pid_str = str(pid)
        team_abbr = roster_entry["team_abbr"]

        # Get season averages
        s = season_avgs.get(pid) or season_avgs.get(pid_str)
        if not s:
            continue  # Skip players with no stats this season

        # Skip very low-minute players (unlikely to contribute)
        if s["min"] < 10 or s["gp"] < 20:
            continue

        # Usage rate
        u = usage_rates.get(pid) or usage_rates.get(pid_str) or {}

        # Career playoff data
        career = career_playoff.get(pid_str) or career_playoff.get(pid)

        # Playoff adjustment
        adj_factor, has_history, adj_details = calc_playoff_adjustment(
            s["min"], career
        )

        # Expected games
        team_total, team_breakdown = team_games.get(team_abbr, (12.0, {}))

        # Injury
        inj_status, inj_note = get_player_injury(
            roster_entry["player_name"], injuries
        )

        fantasy_avg = s["pts"] + s["reb"] + s["ast"]

        p = Player(
            player_id=pid,
            name=roster_entry["player_name"],
            team=team_abbr,
            position=roster_entry.get("position", ""),
            conference=roster_entry.get("conference", ""),
            seed=roster_entry.get("team_seed", 0),
            pts=s["pts"],
            reb=s["reb"],
            ast=s["ast"],
            min=s["min"],
            games_played=s["gp"],
            usg_pct=u.get("usg_pct", 0),
            season_fantasy_avg=fantasy_avg,
            playoff_adj_factor=adj_factor,
            has_playoff_history=has_history,
            adj_details=adj_details,
            expected_games=team_total,
            games_breakdown=team_breakdown,
            injury_status=inj_status,
            injury_note=inj_note,
        )
        players.append(p)

    # Project and rank
    players = project_all(players)
    get_value_tiers(players)

    return players
