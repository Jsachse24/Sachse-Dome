"""Expected games played calculator using betting odds and binomial series math."""

from math import comb


def expected_games_in_series(win_prob: float) -> float:
    """Calculate expected number of games in a best-of-7 series.

    Uses binomial distribution. For team with win probability p:
    P(series ends in N games) considers both teams potentially winning.

    At p=0.50: ~5.81 games. At p=0.75: ~5.16 games.
    """
    p = win_prob
    q = 1 - p

    expected = 0.0
    for n in range(4, 8):  # Series can be 4, 5, 6, or 7 games
        # Probability that the favored team wins in exactly n games:
        # They must win 3 of the first n-1, then win game n
        p_win_in_n = comb(n - 1, 3) * (p ** 4) * (q ** (n - 4))
        # Same for the underdog
        p_lose_in_n = comb(n - 1, 3) * (q ** 4) * (p ** (n - 4))
        # Total probability series ends in n games
        p_ends_in_n = p_win_in_n + p_lose_in_n
        expected += n * p_ends_in_n

    return expected


def series_win_prob_from_futures(
    team_champ_prob: float,
    opponent_champ_prob: float,
) -> float:
    """Estimate series win probability from championship futures.

    Simple approach: relative strength between the two teams.
    More sophisticated: could account for bracket path, but this is a
    reasonable approximation when series odds aren't available.
    """
    total = team_champ_prob + opponent_champ_prob
    if total == 0:
        return 0.5
    return team_champ_prob / total


def calc_round_advance_probs(
    team_abbr: str,
    seed: int,
    conference: str,
    championship_prob: float,
) -> dict[str, float]:
    """Estimate probability of advancing to each round based on championship odds.

    Uses championship probability to back out round-by-round advance probs.
    Assumes roughly equal conditional probabilities per round (adjusted by seed).

    Returns: {round_name: cumulative_probability_of_reaching_that_round}
    """
    # Play-in teams (seeds 7-10) must survive play-in first
    is_playin = seed >= 7

    if championship_prob <= 0:
        championship_prob = 0.001

    # Back out per-round win probability from championship prob
    # P(champ) = P(R1) * P(R2|R1) * P(CF|R2) * P(Finals|CF)
    # For simplicity, assume each round has same conditional win prob
    # P(champ) = p^4 for 4 rounds -> p = champ_prob^0.25
    num_rounds = 4
    per_round_win = championship_prob ** (1 / num_rounds)

    # Clamp to reasonable range
    per_round_win = max(0.15, min(0.95, per_round_win))

    # Adjust: higher seeds more likely in early rounds, less certain later
    # Seeds 1-2 get a bump in R1, taper off
    seed_r1_bonus = max(0, (6 - seed) * 0.03) if seed <= 6 else -0.05
    seed_r1_bonus = max(-0.15, min(0.15, seed_r1_bonus))

    probs = {}

    if is_playin:
        # Play-in probability
        if seed <= 8:
            playin_survive = 0.70  # 7/8 seeds get two chances
        else:
            playin_survive = 0.35  # 9/10 seeds need to win twice
        probs["play_in"] = playin_survive
        probs["r1"] = playin_survive
        probs["r2"] = playin_survive * per_round_win
        probs["cf"] = playin_survive * per_round_win ** 2
        probs["finals"] = playin_survive * per_round_win ** 3
    else:
        probs["play_in"] = 1.0  # Auto-qualify
        r1_prob = min(0.95, per_round_win + seed_r1_bonus)
        probs["r1"] = 1.0  # They're in R1
        probs["r2"] = r1_prob
        probs["cf"] = r1_prob * per_round_win
        probs["finals"] = r1_prob * per_round_win ** 2

    return probs


def calc_expected_total_games(
    team_abbr: str,
    seed: int,
    conference: str,
    championship_prob: float,
    series_odds: list[dict] | None = None,
) -> tuple[float, dict]:
    """Calculate total expected games for a team across entire playoffs.

    Returns (total_expected_games, {round: expected_games_in_round}).
    """
    round_probs = calc_round_advance_probs(
        team_abbr, seed, conference, championship_prob
    )

    # If we have actual series odds, use them for current round
    team_series_prob = None
    if series_odds:
        for s in series_odds:
            if s["home_team"] == team_abbr:
                team_series_prob = s["home_prob"]
                break
            elif s["away_team"] == team_abbr:
                team_series_prob = s["away_prob"]
                break

    games = {}
    is_playin = seed >= 7

    # Play-in games
    if is_playin:
        if seed <= 8:
            games["play_in"] = 1.0 + 0.30  # 1 guaranteed + 30% chance of 2nd game
        else:
            games["play_in"] = 1.0 + round_probs.get("play_in", 0.35) * 1.0
    else:
        games["play_in"] = 0.0

    # For each playoff round, expected games = P(reach round) * E(games in series)
    # Use a default per-round win prob or actual series odds if available
    per_round_win = championship_prob ** 0.25 if championship_prob > 0 else 0.5
    per_round_win = max(0.25, min(0.85, per_round_win))

    rounds = ["r1", "r2", "cf", "finals"]
    for i, rnd in enumerate(rounds):
        if rnd == "r1" and is_playin:
            p_reach = round_probs.get("play_in", 0)
        elif rnd == "r1":
            p_reach = 1.0
        else:
            prev_rnd = rounds[i - 1]
            p_reach = round_probs.get(rnd, 0)

        if p_reach <= 0.001:
            games[rnd] = 0.0
            continue

        # Use actual series odds for R1 if available, else estimate
        if rnd == "r1" and team_series_prob is not None:
            win_p = team_series_prob
        else:
            win_p = per_round_win

        e_games = expected_games_in_series(win_p)
        games[rnd] = p_reach * e_games

    total = sum(games.values())

    return total, games
