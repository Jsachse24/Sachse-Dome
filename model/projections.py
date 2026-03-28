"""Projection formula and ranking."""

from model.players import Player


def project_all(players: list[Player]) -> list[Player]:
    """Calculate projected fantasy points for all players and sort."""
    for p in players:
        p.projected_fantasy_pts = (
            p.season_fantasy_avg * p.playoff_adj_factor * p.expected_games
        )
    players.sort(key=lambda p: p.projected_fantasy_pts, reverse=True)
    # Assign ranks
    for i, p in enumerate(players):
        p.rank = i + 1
    return players


def rerank(players: list[Player]) -> list[Player]:
    """Re-rank available (undrafted) players."""
    available = [p for p in players if not p.is_drafted]
    available.sort(key=lambda p: p.projected_fantasy_pts, reverse=True)
    for i, p in enumerate(available):
        p.rank = i + 1
    return available


def get_value_tiers(players: list[Player], num_tiers: int = 5) -> list[Player]:
    """Assign tier labels based on projected points."""
    available = [p for p in players if not p.is_drafted]
    if not available:
        return available

    max_pts = available[0].projected_fantasy_pts
    min_pts = available[-1].projected_fantasy_pts if available else 0
    spread = max_pts - min_pts if max_pts > min_pts else 1

    tier_names = ["Elite", "Strong", "Solid", "Value", "Depth"]
    for p in available:
        pct = (p.projected_fantasy_pts - min_pts) / spread
        tier_idx = min(int((1 - pct) * num_tiers), num_tiers - 1)
        p.tier = tier_names[tier_idx]

    return available
