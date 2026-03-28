"""Configuration for NBA Playoff Fantasy Draft Tool."""

# League settings
NUM_TEAMS = 10
ROSTER_SIZE = 10
YOUR_DRAFT_POSITION = 1  # 1-indexed, set before draft

# Scoring: 1pt per point, 1pt per rebound, 1pt per assist
# Fantasy pts = PTS + REB + AST

# API keys
ODDS_API_KEY = ""  # The Odds API key - get free at https://the-odds-api.com

# NBA season
SEASON = "2025-26"
SEASON_ID = "2025"  # nba_api uses start year
SEASON_TYPE = "Regular Season"

# Cache TTL in seconds
CACHE_TTL_STATS = 86400       # 24 hours for season stats
CACHE_TTL_PLAYOFF = 86400     # 24 hours for career playoff stats
CACHE_TTL_ODDS = 1800         # 30 min for odds
CACHE_TTL_INJURIES = 3600     # 1 hour for injuries

# Rate limiting (seconds between calls)
NBA_API_DELAY = 3.0
ODDS_API_DELAY = 1.0

# Playoff adjustment
STAR_THRESHOLD_MINUTES = 30.0
STAR_PLAYOFF_BUMP = 1.05
ROLE_PLAYER_PLAYOFF_DIP = 0.95
MIN_PLAYOFF_GAMES_FOR_ADJUSTMENT = 10
ADJUSTMENT_CLAMP_LOW = 0.80
ADJUSTMENT_CLAMP_HIGH = 1.25

# Cache directory
import pathlib
CACHE_DIR = pathlib.Path(__file__).parent / "data" / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
