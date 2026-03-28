"""Playoff adjustment factor engine."""

from config import (
    STAR_THRESHOLD_MINUTES,
    STAR_PLAYOFF_BUMP,
    ROLE_PLAYER_PLAYOFF_DIP,
    MIN_PLAYOFF_GAMES_FOR_ADJUSTMENT,
    ADJUSTMENT_CLAMP_LOW,
    ADJUSTMENT_CLAMP_HIGH,
)


def calc_playoff_adjustment(
    season_min: float,
    career_data: dict | None,
) -> tuple[float, bool, dict]:
    """Calculate playoff adjustment factor for a player.

    Args:
        season_min: Current season minutes per game
        career_data: From get_career_playoff_stats(), has 'regular_season' and 'playoffs' keys

    Returns:
        (adjustment_factor, has_playoff_history, details_dict)
    """
    details = {
        "method": "archetype",
        "playoff_games": 0,
        "reg_fantasy": None,
        "playoff_fantasy": None,
        "min_diff": None,
    }

    if career_data is None:
        return _archetype_fallback(season_min), False, details

    reg = career_data.get("regular_season")
    playoffs = career_data.get("playoffs")

    if not reg or not playoffs:
        return _archetype_fallback(season_min), False, details

    playoff_gp = playoffs.get("gp", 0)
    details["playoff_games"] = playoff_gp

    if playoff_gp < MIN_PLAYOFF_GAMES_FOR_ADJUSTMENT:
        return _archetype_fallback(season_min), False, details

    # Calculate fantasy averages
    reg_fantasy = reg["pts"] + reg["reb"] + reg["ast"]
    playoff_fantasy = playoffs["pts"] + playoffs["reb"] + playoffs["ast"]

    details["method"] = "player_specific"
    details["reg_fantasy"] = round(reg_fantasy, 1)
    details["playoff_fantasy"] = round(playoff_fantasy, 1)
    details["min_diff"] = round(playoffs["min"] - reg["min"], 1)

    if reg_fantasy <= 0:
        return _archetype_fallback(season_min), False, details

    # Raw adjustment ratio
    raw_adj = playoff_fantasy / reg_fantasy

    # Weight toward 1.0 for smaller samples
    # At 40+ playoff games, full weight. At 10 games, half weight.
    sample_weight = min(playoff_gp / 40, 1.0)
    adj = 1.0 + (raw_adj - 1.0) * sample_weight

    # Clamp to avoid outliers
    adj = max(ADJUSTMENT_CLAMP_LOW, min(ADJUSTMENT_CLAMP_HIGH, adj))

    return round(adj, 3), True, details


def _archetype_fallback(minutes: float) -> float:
    """Fallback adjustment based on player role (star vs role player)."""
    if minutes >= STAR_THRESHOLD_MINUTES:
        return STAR_PLAYOFF_BUMP
    return ROLE_PLAYER_PLAYOFF_DIP
