#!/usr/bin/env python3
"""NBA Playoff Fantasy Draft Tool.

Usage:
    python main.py fetch        - Fetch and cache all player/odds data (~8 min first run)
    python main.py html         - Generate draft_board.html (open in browser)
    python main.py html --pos N - Set your draft position in the HTML (1-10)
    python main.py draft        - Launch terminal draft UI
    python main.py rankings     - Print ranked player board to terminal
    python main.py clear-cache  - Wipe cached data
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def fetch_all():
    """Fetch and cache all data from NBA API and odds providers."""
    from data.nba_stats import (
        get_playoff_eligible_teams,
        get_rosters,
        get_season_averages,
        get_usage_rates,
        get_career_playoff_stats,
    )
    from data.odds import get_championship_futures, get_series_odds
    from data.injuries import get_injury_report

    print("=" * 60)
    print("NBA Playoff Fantasy Draft - Data Fetch")
    print("=" * 60)

    # Step 1: Get eligible teams
    teams = get_playoff_eligible_teams()
    print(f"\nEligible teams ({len(teams)}):")
    for t in teams:
        print(f"  {t['seed']}. {t['team_abbr']} ({t['conference']})")

    # Step 2: Get rosters
    rosters = get_rosters(teams)

    # Step 3: Season averages (bulk call)
    season_avgs = get_season_averages()

    # Step 4: Usage rates (bulk call)
    usage_rates = get_usage_rates()

    # Step 5: Career playoff stats (SLOW - one call per player)
    # Only fetch for players with 10+ min and 20+ games to cut fetch time in half
    relevant_ids = []
    for r in rosters:
        pid = r["player_id"]
        s = season_avgs.get(pid)
        if s and s["min"] >= 10 and s["gp"] >= 20:
            relevant_ids.append(pid)
    print(f"\nFetching career stats for {len(relevant_ids)} relevant players "
          f"(filtered from {len(rosters)} total)...")
    career_playoff = get_career_playoff_stats(relevant_ids)

    # Step 6: Odds
    futures = get_championship_futures()
    series = get_series_odds()

    # Step 7: Injuries
    injuries = get_injury_report()

    print("\n" + "=" * 60)
    print("Data fetch complete! All cached.")
    print("Run 'python main.py draft' to start drafting.")
    print("=" * 60)


def build_pool():
    """Load cached data and build the player pool."""
    from data.nba_stats import (
        get_playoff_eligible_teams,
        get_rosters,
        get_season_averages,
        get_usage_rates,
        get_career_playoff_stats,
    )
    from data.odds import get_championship_futures, get_series_odds
    from data.injuries import get_injury_report
    from model.players import build_player_pool

    teams = get_playoff_eligible_teams()
    rosters = get_rosters(teams)
    season_avgs = get_season_averages()
    usage_rates = get_usage_rates()

    player_ids = [r["player_id"] for r in rosters]
    career_playoff = get_career_playoff_stats(player_ids)

    futures = get_championship_futures()
    series = get_series_odds()
    injuries = get_injury_report()

    players = build_player_pool(
        rosters=rosters,
        season_avgs=season_avgs,
        usage_rates=usage_rates,
        career_playoff=career_playoff,
        championship_futures=futures,
        series_odds=series,
        injuries=injuries,
        eligible_teams=teams,
    )

    return players


def print_rankings():
    """Print ranked player board to terminal."""
    from rich.console import Console
    from rich.table import Table

    players = build_pool()
    console = Console()

    table = Table(title="NBA Playoff Fantasy Rankings", show_lines=False)
    table.add_column("Rank", justify="right", width=5)
    table.add_column("Player", width=22)
    table.add_column("Team", width=5)
    table.add_column("Proj Pts", justify="right", width=8)
    table.add_column("Avg/G", justify="right", width=7)
    table.add_column("Exp Games", justify="right", width=9)
    table.add_column("Adj", justify="right", width=6)
    table.add_column("Tier", width=7)
    table.add_column("Injury", width=10)

    tier_colors = {
        "Elite": "bold green",
        "Strong": "bold cyan",
        "Solid": "bold yellow",
        "Value": "bold #ff9900",
        "Depth": "dim",
    }

    for p in players[:100]:  # Top 100
        style = tier_colors.get(p.tier, "")
        injury = "OK" if p.injury_status == "Healthy" else p.injury_status
        table.add_row(
            str(p.rank),
            p.name,
            p.team,
            f"{p.projected_fantasy_pts:.0f}",
            f"{p.season_fantasy_avg:.1f}",
            f"{p.expected_games:.1f}",
            f"{p.playoff_adj_factor:.2f}",
            p.tier,
            injury,
            style=style,
        )

    console.print(table)
    console.print(f"\nTotal players: {len(players)}")
    console.print("Run 'python main.py draft' to start the interactive draft.")


def generate_html(draft_position: int = 1):
    """Generate a standalone HTML draft board."""
    import json
    from pathlib import Path
    from data.nba_stats import get_playoff_eligible_teams
    from data.odds import get_championship_futures

    players = build_pool()
    teams = get_playoff_eligible_teams()
    futures = get_championship_futures()

    # Serialize players for JS
    player_data = []
    for p in players:
        player_data.append({
            "id": p.player_id,
            "name": p.name,
            "team": p.team,
            "position": p.position,
            "conference": p.conference,
            "seed": p.seed,
            "pts": round(p.pts, 1),
            "reb": round(p.reb, 1),
            "ast": round(p.ast, 1),
            "min": round(p.min, 1),
            "games_played": p.games_played,
            "usg_pct": round(p.usg_pct, 3),
            "fantasy_avg": round(p.season_fantasy_avg, 1),
            "adj": round(p.playoff_adj_factor, 3),
            "has_playoff_history": p.has_playoff_history,
            "adj_details": p.adj_details,
            "expected_games": round(p.expected_games, 2),
            "games_breakdown": {k: round(v, 2) for k, v in p.games_breakdown.items()},
            "projected": round(p.projected_fantasy_pts, 1),
            "tier": p.tier,
            "injury_status": p.injury_status,
            "injury_note": p.injury_note,
        })

    # Serialize team data
    team_data = []
    for t in teams:
        team_data.append({
            "team_abbr": t["team_abbr"],
            "team_name": t.get("team_city", "") + " " + t.get("team_name", ""),
            "conference": t["conference"],
            "seed": t["seed"],
            "wins": t.get("wins", 0),
            "losses": t.get("losses", 0),
            "champ_prob": round(futures.get(t["team_abbr"], 0.01), 4),
        })

    config_data = {
        "num_teams": 10,
        "roster_size": 10,
        "your_draft_position": draft_position,
    }

    # Read template and inject data
    template_path = Path(__file__).parent / "template.html"
    html = template_path.read_text()
    html = html.replace("__PLAYER_DATA__", json.dumps(player_data))
    html = html.replace("__TEAM_DATA__", json.dumps(team_data))
    html = html.replace("__CONFIG__", json.dumps(config_data))

    out_path = Path(__file__).parent / "draft_board.html"
    out_path.write_text(html)

    print(f"Generated: {out_path}")
    print(f"Players: {len(player_data)}")
    print(f"Your draft position: {draft_position}")
    print(f"\nOpen {out_path} in your browser to start drafting!")


def run_draft(draft_position: int = 1):
    """Launch the interactive draft UI."""
    import config
    config.YOUR_DRAFT_POSITION = draft_position

    players = build_pool()
    print(f"Loaded {len(players)} players. Launching draft UI...")
    print(f"Your draft position: {draft_position}")

    from ui.app import DraftApp
    app = DraftApp(players=players)
    app.draft_position = draft_position
    app.run()


def main():
    args = sys.argv[1:]
    cmd = args[0] if args else "help"

    # Parse --pos flag
    draft_pos = 1
    if "--pos" in args:
        idx = args.index("--pos")
        if idx + 1 < len(args):
            draft_pos = int(args[idx + 1])
            draft_pos = max(1, min(10, draft_pos))

    if cmd == "fetch":
        fetch_all()
    elif cmd == "html":
        generate_html(draft_pos)
    elif cmd == "rankings":
        print_rankings()
    elif cmd == "draft":
        run_draft(draft_pos)
    elif cmd == "clear-cache":
        from data.cache import invalidate_all
        invalidate_all()
        print("Cache cleared.")
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
