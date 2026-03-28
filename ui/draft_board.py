"""Available players DataTable widget."""

from textual.widgets import DataTable
from model.players import Player


COLUMNS = [
    ("Rank", 5),
    ("ID", 5),
    ("Player", 22),
    ("Team", 5),
    ("Proj", 7),
    ("Avg/G", 6),
    ("Games", 6),
    ("Adj", 5),
    ("Tier", 7),
    ("Injury", 10),
]


class DraftBoard(DataTable):
    """DataTable showing available players ranked by projected fantasy points."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.players: list[Player] = []
        self._player_row_map: dict[int, any] = {}  # player_id -> row_key
        self._search_filter: str = ""

    def setup_columns(self):
        for name, width in COLUMNS:
            self.add_column(name, key=name.lower(), width=width)

    def populate(self, players: list[Player]):
        """Fill the table with player data."""
        self.players = players
        self.clear()
        self._player_row_map = {}

        for p in players:
            if p.is_drafted:
                continue
            if self._search_filter and self._search_filter.lower() not in p.name.lower():
                continue

            tier_style = _tier_color(p.tier)
            injury_display = _injury_display(p.injury_status, p.injury_note)

            row_key = self.add_row(
                str(p.rank),
                str(p.player_id),
                p.name,
                p.team,
                f"{p.projected_fantasy_pts:.0f}",
                f"{p.season_fantasy_avg:.1f}",
                f"{p.expected_games:.1f}",
                f"{p.playoff_adj_factor:.2f}",
                p.tier,
                injury_display,
                key=str(p.player_id),
            )
            self._player_row_map[p.player_id] = row_key

    def filter_by_name(self, query: str):
        """Filter visible rows by name substring."""
        self._search_filter = query
        self.populate(self.players)

    def get_selected_player(self) -> Player | None:
        """Get the currently highlighted player."""
        if self.cursor_row is None or self.cursor_row >= self.row_count:
            return None
        try:
            row_key = self.coordinate_to_cell_key((self.cursor_row, 0)).row_key
            pid = int(row_key.value)
            for p in self.players:
                if p.player_id == pid:
                    return p
        except (ValueError, IndexError, AttributeError):
            pass
        return None

    def get_player_by_id(self, player_id: int) -> Player | None:
        for p in self.players:
            if p.player_id == player_id:
                return p
        return None

    def get_player_by_name(self, name: str) -> Player | None:
        """Find a player by partial name match."""
        name_lower = name.lower().strip()
        # Exact match first
        for p in self.players:
            if not p.is_drafted and p.name.lower() == name_lower:
                return p
        # Partial match
        matches = [
            p for p in self.players
            if not p.is_drafted and name_lower in p.name.lower()
        ]
        if len(matches) == 1:
            return matches[0]
        return None


def _tier_color(tier: str) -> str:
    return {
        "Elite": "bold green",
        "Strong": "bold cyan",
        "Solid": "bold yellow",
        "Value": "bold #ff9900",
        "Depth": "dim",
    }.get(tier, "")


def _injury_display(status: str, note: str) -> str:
    if status == "Healthy":
        return "OK"
    short_note = note[:15] if note else ""
    return f"{status[:3]} {short_note}".strip()
