#!/usr/bin/env python3
"""Local API server for on-demand analytics and report generation.

Usage:
    python server.py              # Start on port 8000
    python main.py serve          # Same thing
"""

import sys
import os
import json
import argparse
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="NBA Playoff Fantasy Draft")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

_player_data: list[dict] = []


def _load_player_data():
    global _player_data
    draft_board = Path(__file__).parent / "draft_board.html"
    if not draft_board.exists():
        return
    html = draft_board.read_text()
    start = html.find("const PLAYER_DATA = ")
    if start == -1:
        return
    start += len("const PLAYER_DATA = ")
    end = html.find(";\nconst TEAM_DATA", start)
    if end == -1:
        return
    try:
        _player_data = json.loads(html[start:end])
    except json.JSONDecodeError:
        pass


@app.on_event("startup")
async def startup():
    _load_player_data()
    print(f"Loaded {len(_player_data)} players")


@app.get("/", response_class=HTMLResponse)
async def serve_draft_board():
    path = Path(__file__).parent / "draft_board.html"
    if not path.exists():
        raise HTTPException(404, "Run 'python main.py html' first")
    return HTMLResponse(path.read_text())


@app.get("/api/players")
async def get_players():
    return JSONResponse(_player_data)


def _find_player(player_id: int) -> dict | None:
    for p in _player_data:
        if p["id"] == player_id:
            return p
    return None


@app.post("/api/fetch-advanced/{player_id}")
async def fetch_advanced(player_id: int):
    """Fetch advanced stats from all sources for a player."""
    player = _find_player(player_id)
    if not player:
        raise HTTPException(404, "Player not found")

    results = {}
    errors = []

    try:
        from data.basketball_ref import get_advanced_stats
        results["bbref"] = get_advanced_stats(player["name"], player_id)
    except Exception as e:
        errors.append(f"bbref: {e}")
        results["bbref"] = None

    try:
        from data.bball_index import get_lebron_ratings
        results["bball_index"] = get_lebron_ratings(player["name"], player_id)
    except Exception as e:
        errors.append(f"bball_index: {e}")
        results["bball_index"] = None

    try:
        from data.dunks_threes import get_epm_data
        results["dunks_threes"] = get_epm_data(player["name"], player_id)
    except Exception as e:
        errors.append(f"dunks_threes: {e}")
        results["dunks_threes"] = None

    return JSONResponse({"player_id": player_id, "sources": results, "errors": errors})


@app.post("/api/report/{player_id}")
async def api_generate_report(player_id: int):
    """Generate a full analyst report for a player."""
    player = _find_player(player_id)
    if not player:
        raise HTTPException(404, "Player not found")

    from data.analytics_cache import get_cached, TTL_PLAYER_STATS, TTL_ANALYST_CONTENT
    from model.advanced_adjustment import merge_advanced_data
    from analysis.report_generator import generate_report

    # Gather cached data or fetch fresh
    bbref = get_cached(str(player_id), "bbref", TTL_PLAYER_STATS)
    bball_idx = get_cached(str(player_id), "bball_index", TTL_PLAYER_STATS)
    dunks_threes = get_cached(str(player_id), "dunks_threes", TTL_PLAYER_STATS)
    analyst = get_cached(str(player_id), "analyst_content", TTL_ANALYST_CONTENT)

    # Fetch missing data
    if not bbref:
        try:
            from data.basketball_ref import get_advanced_stats
            bbref = get_advanced_stats(player["name"], player_id)
        except Exception:
            pass
    if not bball_idx:
        try:
            from data.bball_index import get_lebron_ratings
            bball_idx = get_lebron_ratings(player["name"], player_id)
        except Exception:
            pass
    if not dunks_threes:
        try:
            from data.dunks_threes import get_epm_data
            dunks_threes = get_epm_data(player["name"], player_id)
        except Exception:
            pass
    if not analyst:
        try:
            from data.analyst_search import search_analyst_content
            analyst = search_analyst_content(player["name"], player_id, player.get("team", ""))
        except Exception:
            pass

    advanced = merge_advanced_data(bbref, bball_idx, dunks_threes)
    result = generate_report(player, advanced, analyst)
    return JSONResponse(result)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--host", default="127.0.0.1")
    args = parser.parse_args()

    print(f"\n{'='*60}")
    print(f"NBA Playoff Fantasy Draft Server")
    print(f"{'='*60}")
    print(f"Open: http://{args.host}:{args.port}")
    print(f"{'='*60}\n")

    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
