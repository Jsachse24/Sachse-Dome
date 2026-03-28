"""Advanced scoring adjustments based on multi-source analytics data.

Adjustments applied multiplicatively to projected fantasy points:
1. BPM/EPM playoff delta: penalize decliners, reward improvers
2. Usage sustainability: high usage + low efficiency = penalty
3. Defensive LEBRON: top defenders get a small multiplier
"""


def calc_advanced_adjustment(advanced: dict | None) -> tuple[float, dict]:
    """Calculate combined advanced adjustment factor.

    Returns (adjustment_factor, details_dict)
    """
    if not advanced:
        return 1.0, {"method": "none", "components": {}}

    components = {}
    total_adj = 1.0

    playoff_delta_adj = _calc_playoff_delta_adj(advanced)
    components["playoff_delta"] = playoff_delta_adj
    total_adj *= playoff_delta_adj["factor"]

    usage_adj = _calc_usage_sustainability(advanced)
    components["usage_sustainability"] = usage_adj
    total_adj *= usage_adj["factor"]

    defense_adj = _calc_defensive_adj(advanced)
    components["defense"] = defense_adj
    total_adj *= defense_adj["factor"]

    total_adj = max(0.85, min(1.15, total_adj))

    return round(total_adj, 4), {
        "method": "advanced_multi_source",
        "components": components,
        "total_factor": round(total_adj, 4),
    }


def _calc_playoff_delta_adj(advanced: dict) -> dict:
    bbref = advanced.get("bbref") or {}
    bpm_delta = bbref.get("bpm_delta")
    ts_delta = bbref.get("ts_delta")

    factor = 1.0
    signal = "neutral"

    if bpm_delta is not None:
        if bpm_delta <= -2.0:
            factor *= 0.96
            signal = "significant_decline"
        elif bpm_delta <= -1.0:
            factor *= 0.98
            signal = "moderate_decline"
        elif bpm_delta >= 1.0:
            factor *= 1.03
            signal = "playoff_riser"
        elif bpm_delta >= 0.5:
            factor *= 1.01
            signal = "slight_improvement"

    if ts_delta is not None:
        if ts_delta <= -0.04:
            factor *= 0.98
        elif ts_delta >= 0.02:
            factor *= 1.01

    return {"factor": round(factor, 4), "signal": signal, "bpm_delta": bpm_delta, "ts_delta": ts_delta}


def _calc_usage_sustainability(advanced: dict) -> dict:
    bbref = advanced.get("bbref") or {}
    usg = bbref.get("usg_pct")
    ts = bbref.get("ts_pct")

    if usg is None or ts is None:
        return {"factor": 1.0, "signal": "no_data", "usg": usg, "ts": ts}

    factor = 1.0
    signal = "neutral"
    avg_ts = 0.575

    if usg >= 0.28:
        if ts < avg_ts - 0.02:
            factor = 0.97
            signal = "high_usage_low_efficiency"
        elif ts >= avg_ts + 0.03:
            factor = 1.03
            signal = "high_usage_elite_efficiency"
        elif ts >= avg_ts:
            factor = 1.01
            signal = "high_usage_solid_efficiency"

    return {"factor": round(factor, 4), "signal": signal, "usg": usg, "ts": ts}


def _calc_defensive_adj(advanced: dict) -> dict:
    bi = advanced.get("bball_index") or {}
    d_lebron = bi.get("d_lebron")

    if d_lebron is None:
        return {"factor": 1.0, "signal": "no_data", "d_lebron": d_lebron}

    factor = 1.0
    signal = "neutral"

    if d_lebron >= 2.5:
        factor = 1.03
        signal = "elite_defender"
    elif d_lebron >= 1.5:
        factor = 1.01
        signal = "strong_defender"
    elif d_lebron <= -1.5:
        factor = 0.99
        signal = "weak_defender"

    return {"factor": round(factor, 4), "signal": signal, "d_lebron": d_lebron}


def merge_advanced_data(bbref=None, bball_index=None, dunks_threes=None) -> dict:
    return {"bbref": bbref, "bball_index": bball_index, "dunks_threes": dunks_threes}
