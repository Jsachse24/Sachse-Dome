# Sachse-Dome

NBA Playoff Fantasy Draft cheat sheet and draft assistant.

## Features

- **Smart Recommendations** - AI-powered pick suggestions factoring in positional scarcity, team exposure risk, and value cliffs
- **Live Draft Board** - Sortable, filterable player rankings with tier separators
- **Playoff Projection Model** - Season stats x playoff adjustment factor x expected games (from championship odds)
- **Injury Impact** - Questionable/Doubtful/Out players auto-penalized in projections
- **Team Exposure Tracking** - Warns when you're over-concentrated on one NBA team
- **Draft Persistence** - Auto-saves to localStorage, survives page refresh
- **Position & Conference Filters** - Filter by G/F/C and East/West
- **Export** - Copy draft results to clipboard

## Quick Start

```bash
pip install -r requirements.txt

# Fetch live data (~8 min first run, cached after)
python main.py fetch

# Generate the draft board HTML
python main.py html --pos 3    # set your draft position (1-10)

# Open draft_board.html in your browser
```

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| M | Draft selected player (My Pick) |
| X | Mark selected player as taken |
| U | Undo last pick |
| / | Focus search |
| Esc | Clear search/close modals |
| Arrow Up/Down | Navigate player list |
| Enter | Draft selected player |
| 1/2/3 | Switch tabs (My Team / Draft Log / Player Info) |

## Scoring

Fantasy points = PTS + REB + AST per game, multiplied by playoff adjustment factor and expected total games.

## Data Sources

- **NBA API** (`nba_api`) - Season stats, rosters, standings, career playoff stats
- **The Odds API** - Championship futures, series odds (optional, uses defaults if no key)
