"""Snake draft state machine and display widget."""

from textual.widgets import Static
from textual.reactive import reactive
from config import NUM_TEAMS, ROSTER_SIZE


class DraftTracker(Static):
    """Tracks snake draft state and displays pick history."""

    current_pick = reactive(1)

    def __init__(
        self,
        num_teams: int = NUM_TEAMS,
        roster_size: int = ROSTER_SIZE,
        your_position: int = 1,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.num_teams = num_teams
        self.roster_size = roster_size
        self.your_position = your_position
        self.total_picks = num_teams * roster_size
        self.picks: list[dict | None] = [None] * self.total_picks
        self.current_pick = 1

    def get_team_for_pick(self, pick: int) -> int:
        """Get which team (1-indexed) picks at a given pick number (1-indexed)."""
        pick_0 = pick - 1
        round_num = pick_0 // self.num_teams
        pos_in_round = pick_0 % self.num_teams

        if round_num % 2 == 0:
            # Odd rounds (1, 3, 5...): forward order
            return pos_in_round + 1
        else:
            # Even rounds (2, 4, 6...): reverse order
            return self.num_teams - pos_in_round

    def get_round_for_pick(self, pick: int) -> int:
        return ((pick - 1) // self.num_teams) + 1

    def get_next_your_pick(self) -> int | None:
        """Find the next pick belonging to your team."""
        for p in range(self.current_pick, self.total_picks + 1):
            if self.get_team_for_pick(p) == self.your_position:
                return p
        return None

    def get_your_picks_remaining(self) -> list[int]:
        """Get all remaining pick numbers for your team."""
        remaining = []
        for p in range(self.current_pick, self.total_picks + 1):
            if self.get_team_for_pick(p) == self.your_position:
                remaining.append(p)
        return remaining

    def is_your_pick(self) -> bool:
        return self.get_team_for_pick(self.current_pick) == self.your_position

    def make_pick(self, player_name: str, player_team: str) -> dict:
        """Record a pick and advance."""
        pick_info = {
            "pick": self.current_pick,
            "round": self.get_round_for_pick(self.current_pick),
            "team": self.get_team_for_pick(self.current_pick),
            "player": player_name,
            "player_team": player_team,
        }
        self.picks[self.current_pick - 1] = pick_info
        self.current_pick += 1
        self.refresh_display()
        return pick_info

    def undo_pick(self) -> dict | None:
        """Undo the last pick."""
        if self.current_pick <= 1:
            return None
        self.current_pick -= 1
        pick_info = self.picks[self.current_pick - 1]
        self.picks[self.current_pick - 1] = None
        self.refresh_display()
        return pick_info

    def get_your_roster(self) -> list[dict]:
        """Get all players drafted by your team."""
        roster = []
        for pick in self.picks:
            if pick and pick["team"] == self.your_position:
                roster.append(pick)
        return roster

    def refresh_display(self):
        """Update the display."""
        self.update(self._render_display())

    def _render_display(self) -> str:
        lines = []
        current_team = self.get_team_for_pick(self.current_pick) if self.current_pick <= self.total_picks else 0
        current_round = self.get_round_for_pick(self.current_pick) if self.current_pick <= self.total_picks else 0

        # Header
        if self.current_pick <= self.total_picks:
            is_yours = " << YOUR PICK!" if self.is_your_pick() else ""
            lines.append(f"[bold]Pick #{self.current_pick}[/] | Round {current_round} | Team {current_team}{is_yours}")

            next_yours = self.get_next_your_pick()
            if next_yours and not self.is_your_pick():
                picks_until = next_yours - self.current_pick
                lines.append(f"Your next pick: #{next_yours} ({picks_until} picks away)")
        else:
            lines.append("[bold green]DRAFT COMPLETE![/]")

        lines.append("")

        # Your roster
        roster = self.get_your_roster()
        lines.append(f"[bold]Your Roster (Team {self.your_position}):[/]")
        if roster:
            total_proj = 0
            for r in roster:
                lines.append(f"  R{r['round']} #{r['pick']}: {r['player']} ({r['player_team']})")
            lines.append(f"  [{len(roster)}/{self.roster_size} spots filled]")
        else:
            lines.append("  (empty)")

        lines.append("")

        # Recent picks
        lines.append("[bold]Recent Picks:[/]")
        made_picks = [p for p in self.picks if p is not None]
        for pick in reversed(made_picks[-8:]):
            marker = ">> " if pick["team"] == self.your_position else "   "
            lines.append(f"{marker}#{pick['pick']} T{pick['team']}: {pick['player']} ({pick['player_team']})")

        return "\n".join(lines)

    def on_mount(self):
        self.refresh_display()
