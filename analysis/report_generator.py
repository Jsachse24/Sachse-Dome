"""On-demand player report generator using Claude API.

Compiles data from all sources and sends to claude-sonnet-4-20250514
to produce a structured analyst report.
"""

import json
import os
import time
from data.analytics_cache import get_cached, set_cached

REPORT_CACHE_TTL = 86400  # 24 hours


def generate_report(player: dict, advanced: dict | None, analyst_content: dict | None) -> dict:
    """Generate a full analyst report for a player.

    Returns {"html": str, "generated_at": float, "error": str | None}
    """
    player_id = str(player.get("id", player.get("player_id", "")))

    cached = get_cached(player_id, "report", REPORT_CACHE_TTL)
    if cached:
        return cached

    prompt = _build_prompt(player, advanced, analyst_content)

    try:
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            return {
                "html": _fallback_report(player, advanced, analyst_content),
                "generated_at": time.time(),
                "error": "No ANTHROPIC_API_KEY set - showing raw data report",
            }

        from anthropic import Anthropic
        client = Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}],
        )

        report_html = response.content[0].text
        result = {"html": report_html, "generated_at": time.time(), "error": None}
        set_cached(player_id, "report", result)
        return result

    except Exception as e:
        print(f"WARNING: Claude API call failed for {player.get('name', '?')}: {e}")
        return {
            "html": _fallback_report(player, advanced, analyst_content),
            "generated_at": time.time(),
            "error": str(e),
        }


def _build_prompt(player: dict, advanced: dict | None, analyst_content: dict | None) -> str:
    name = player.get("name", "Unknown")
    team = player.get("team", "???")
    pos = player.get("position", "?")
    age = player.get("adj_details", {}).get("age", "?")

    stats_block = f"""SEASON STATS (2025-26):
  PTS: {player.get('pts', '?')}  REB: {player.get('reb', '?')}  AST: {player.get('ast', '?')}
  STL: {player.get('stl', '?')}  BLK: {player.get('blk', '?')}  3PM: {player.get('threes', '?')}
  MIN: {player.get('min', '?')}  GP: {player.get('games_played', '?')}  USG: {player.get('usg_pct', '?')}
  Fantasy Avg (PTS+REB+AST): {player.get('fantasy_avg', '?')}
  Projected Total Fantasy Pts: {player.get('projected', '?')}
  Expected Playoff Games: {player.get('expected_games', '?')}
  Playoff Adj Factor: {player.get('adj', '?')}
  Injury: {player.get('injury_status', 'Healthy')} {player.get('injury_note', '')}"""

    adv_block = "ADVANCED METRICS:\n"
    if advanced:
        bbref = advanced.get("bbref") or {}
        bi = advanced.get("bball_index") or {}
        dt = advanced.get("dunks_threes") or {}

        if any(v is not None for v in bbref.values()):
            adv_block += f"""  Basketball Reference:
    BPM: {bbref.get('bpm', 'N/A')}  VORP: {bbref.get('vorp', 'N/A')}  TS%: {bbref.get('ts_pct', 'N/A')}
    Playoff BPM: {bbref.get('playoff_bpm', 'N/A')}  Playoff TS%: {bbref.get('playoff_ts_pct', 'N/A')}
    BPM Delta (PO-RS): {bbref.get('bpm_delta', 'N/A')}  TS% Delta: {bbref.get('ts_delta', 'N/A')}
"""
        if any(v is not None for v in bi.values()):
            adv_block += f"""  BBall Index:
    LEBRON: {bi.get('lebron', 'N/A')}  O-LEBRON: {bi.get('o_lebron', 'N/A')}  D-LEBRON: {bi.get('d_lebron', 'N/A')}
    Shot Making: {bi.get('shot_making', 'N/A')}
"""
        if any(v is not None for v in dt.values()):
            adv_block += f"""  Dunks & Threes:
    EPM: {dt.get('epm', 'N/A')}  O-EPM: {dt.get('o_epm', 'N/A')}  D-EPM: {dt.get('d_epm', 'N/A')}
    Wins Added: {dt.get('wins_added', 'N/A')}
"""
    else:
        adv_block += "  No advanced metrics available.\n"

    analyst_block = "RECENT ANALYST COMMENTARY:\n"
    if analyst_content:
        for key in ["thinking_basketball", "duncd_on", "cleaning_the_glass", "dunks_and_threes"]:
            source = analyst_content.get(key, {})
            source_name = source.get("name", key)
            results = source.get("results", [])
            most_recent = source.get("most_recent_date", "unknown")
            analyst_block += f"\n  {source_name} (most recent: {most_recent}):\n"
            if results:
                for r in results[:2]:
                    analyst_block += f"    - {r.get('title', 'Untitled')}\n"
                    snippet = r.get("snippet", "")
                    if snippet:
                        analyst_block += f"      {snippet[:200]}\n"
            else:
                analyst_block += "    No recent content found.\n"
    else:
        analyst_block += "  No analyst content available.\n"

    return f"""You are generating a fantasy basketball playoff draft analyst report. Output ONLY HTML (no markdown, no code fences). Use inline styles for a dark theme (bg: #0d1117, text: #e6edf3).

PLAYER: {name} | {team} | {pos} | Age {age}

{stats_block}

{adv_block}

{analyst_block}

Generate a structured report with these sections:

1. **Metrics Snapshot** - HTML table: Regular Season vs Playoffs side by side. BPM, TS%, USG%, fantasy avg.

2. **Usage Sustainability Analysis** - Is this player's role stable or at risk? 2-3 sentences.

3. **Regular Season to Playoff Delta** - Where do numbers move and why? 2-3 sentences.

4. **Analyst-Lens Synthesis** - One paragraph per voice:
   - *Ben Taylor (Thinking Basketball):* historical context, usage vs efficiency, playoff applicability
   - *Nate Duncan (Dunc'd On):* rotation implications, minutes risk, role fit
   - *Ben Falk (Cleaning the Glass):* contextual efficiency, playoff defensive intensity
   - *Andrew Patton (Dunks & Threes):* EPM-based impact, team win probability

5. **Overall Verdict** - 3-5 sentences, plain language, fantasy-relevant conclusion.

Inline styles:
- Headers: font-size:14px;font-weight:700;color:#58a6ff;text-transform:uppercase;letter-spacing:0.5px;margin:16px 0 8px;border-bottom:1px solid #30363d;padding-bottom:4px;
- Body: font-size:13px;line-height:1.6;color:#e6edf3;
- Tables: border-collapse:collapse;width:100%;font-size:12px;
- TH: background:#1c2333;color:#8b949e;padding:6px 8px;text-align:left;border-bottom:1px solid #30363d;
- TD: padding:5px 8px;border-bottom:1px solid #30363d;color:#e6edf3;
- Analyst names: color:#bc8cff;font-weight:600;
- Positive: color:#3fb950; Negative: color:#f85149; Neutral: color:#d29922;"""


def _fallback_report(player: dict, advanced: dict | None, analyst_content: dict | None) -> str:
    """Simple HTML report without Claude API."""
    name = player.get("name", "Unknown")
    team = player.get("team", "???")

    rows = []
    if advanced:
        for source_key, metrics in [
            ("bbref", [("bpm", "BPM"), ("vorp", "VORP"), ("ts_pct", "TS%"), ("usg_pct", "USG%"),
                       ("bpm_delta", "BPM Delta (PO-RS)"), ("ts_delta", "TS% Delta (PO-RS)")]),
            ("bball_index", [("lebron", "LEBRON"), ("o_lebron", "O-LEBRON"), ("d_lebron", "D-LEBRON"),
                            ("shot_making", "Shot Making")]),
            ("dunks_threes", [("epm", "EPM"), ("o_epm", "O-EPM"), ("d_epm", "D-EPM"),
                             ("wins_added", "Wins Added")]),
        ]:
            data = advanced.get(source_key) or {}
            for key, label in metrics:
                val = data.get(key)
                if val is not None:
                    rows.append(
                        f"<tr><td style='padding:4px 8px;border-bottom:1px solid #30363d;color:#8b949e'>{label}</td>"
                        f"<td style='padding:4px 8px;border-bottom:1px solid #30363d;color:#e6edf3'>{val}</td></tr>"
                    )

    table = ""
    if rows:
        table = f"""<table style="border-collapse:collapse;width:100%;font-size:12px;margin:8px 0">
            <tr><th style="background:#1c2333;color:#8b949e;padding:6px 8px;text-align:left;border-bottom:1px solid #30363d">Metric</th>
            <th style="background:#1c2333;color:#8b949e;padding:6px 8px;text-align:left;border-bottom:1px solid #30363d">Value</th></tr>
            {''.join(rows)}</table>"""

    analyst_html = ""
    if analyst_content:
        for key in ["thinking_basketball", "duncd_on", "cleaning_the_glass", "dunks_and_threes"]:
            source = analyst_content.get(key, {})
            source_name = source.get("name", key)
            results = source.get("results", [])
            if results:
                links = "".join(
                    f"<div style='margin:2px 0'><a href='{r.get('url', '#')}' target='_blank' "
                    f"style='color:#58a6ff;text-decoration:none;font-size:12px'>{r.get('title', 'Link')}</a>"
                    f"<span style='color:#8b949e;font-size:10px;margin-left:6px'>{r.get('date', '')}</span></div>"
                    for r in results[:2]
                )
                analyst_html += f"<div style='margin:8px 0'><div style='color:#bc8cff;font-weight:600;font-size:12px'>{source_name}</div>{links}</div>"

    return f"""<div style="font-size:13px;line-height:1.6;color:#e6edf3">
        <div style="font-size:14px;font-weight:700;color:#58a6ff;margin:8px 0;border-bottom:1px solid #30363d;padding-bottom:4px">
            ADVANCED METRICS — {name} ({team})</div>
        {table if table else '<div style="color:#8b949e;font-size:12px">No advanced metrics fetched yet. Click "Fetch Data" first, or set ANTHROPIC_API_KEY for full AI reports.</div>'}
        {f'<div style="font-size:14px;font-weight:700;color:#58a6ff;margin:16px 0 8px;border-bottom:1px solid #30363d;padding-bottom:4px">ANALYST CONTENT</div>{analyst_html}' if analyst_html else ''}
    </div>"""
