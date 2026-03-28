"""Main Textual application for the NBA Playoff Fantasy Draft Tool."""

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Footer, Input, Static
from textual.binding import Binding

from model.players import Player
from model.projections import rerank, get_value_tiers
from ui.draft_board import DraftBoard
from ui.draft_tracker import DraftTracker
from ui.player_detail import PlayerDetail
from config import NUM_TEAMS, ROSTER_SIZE, YOUR_DRAFT_POSITION


class StatusBar(Static):
    """Bottom status bar showing current state."""
    pass


class DraftApp(App):
    """NBA Playoff Fantasy Draft Tool."""

    CSS_PATH = "styles.tcss"
    TITLE = "NBA Playoff Fantasy Draft"

    BINDINGS = [
        Binding("d", "draft_player", "Draft Player", show=True),
        Binding("u", "undo_pick", "Undo Pick", show=True),
        Binding("r", "refresh_odds", "Refresh Odds", show=True),
        Binding("slash", "focus_search", "Search", show=True),
        Binding("escape", "clear_search", "Clear Search", show=False),
        Binding("i", "set_injury", "Set Injury", show=True),
        Binding("p", "set_position", "Set Draft Pos", show=True),
        Binding("q", "quit", "Quit", show=True),
    ]

    def __init__(self, players: list[Player], **kwargs):
        super().__init__(**kwargs)
        self.all_players = players
        self.draft_position = YOUR_DRAFT_POSITION

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            with Vertical(id="left-panel"):
                yield DraftBoard(id="player-table", cursor_type="row")
                yield Input(placeholder="Search players... (/ to focus, Esc to clear)", id="search-box")
                yield StatusBar(id="status-bar")
            with Vertical(id="right-panel"):
                yield DraftTracker(
                    num_teams=NUM_TEAMS,
                    roster_size=ROSTER_SIZE,
                    your_position=self.draft_position,
                    id="draft-tracker",
                )
                yield PlayerDetail(id="player-detail")
        yield Footer()

    def on_mount(self):
        board = self.query_one("#player-table", DraftBoard)
        board.setup_columns()
        board.populate(self.all_players)
        self._update_status()

    def on_data_table_row_highlighted(self, event):
        """Update detail panel when cursor moves."""
        board = self.query_one("#player-table", DraftBoard)
        player = board.get_selected_player()
        detail = self.query_one("#player-detail", PlayerDetail)
        detail.show_player(player)

    def on_input_changed(self, event: Input.Changed):
        """Filter board as user types in search."""
        if event.input.id == "search-box":
            board = self.query_one("#player-table", DraftBoard)
            board.filter_by_name(event.value)

    def action_focus_search(self):
        self.query_one("#search-box", Input).focus()

    def action_clear_search(self):
        search = self.query_one("#search-box", Input)
        search.value = ""
        board = self.query_one("#player-table", DraftBoard)
        board.filter_by_name("")
        board.focus()

    def action_draft_player(self):
        """Draft the currently selected player."""
        board = self.query_one("#player-table", DraftBoard)
        tracker = self.query_one("#draft-tracker", DraftTracker)

        if tracker.current_pick > tracker.total_picks:
            self.notify("Draft is complete!", severity="warning")
            return

        player = board.get_selected_player()
        if player is None:
            self.notify("No player selected", severity="warning")
            return

        if player.is_drafted:
            self.notify(f"{player.name} is already drafted", severity="warning")
            return

        # Mark drafted
        team_num = tracker.get_team_for_pick(tracker.current_pick)
        player.is_drafted = True
        player.drafted_by = team_num
        player.draft_pick = tracker.current_pick

        # Record pick
        pick_info = tracker.make_pick(player.name, player.team)

        # Re-rank and refresh board
        rerank(self.all_players)
        get_value_tiers(self.all_players)
        board.populate(self.all_players)

        is_yours = " (YOUR PICK)" if team_num == self.draft_position else ""
        self.notify(f"Pick #{pick_info['pick']}: {player.name} to Team {team_num}{is_yours}")
        self._update_status()

    def action_undo_pick(self):
        """Undo the last pick."""
        tracker = self.query_one("#draft-tracker", DraftTracker)
        board = self.query_one("#player-table", DraftBoard)

        pick_info = tracker.undo_pick()
        if pick_info is None:
            self.notify("No picks to undo", severity="warning")
            return

        # Find and un-draft the player
        for p in self.all_players:
            if p.name == pick_info["player"] and p.is_drafted:
                p.is_drafted = False
                p.drafted_by = None
                p.draft_pick = None
                break

        rerank(self.all_players)
        get_value_tiers(self.all_players)
        board.populate(self.all_players)

        self.notify(f"Undid pick #{pick_info['pick']}: {pick_info['player']}")
        self._update_status()

    def action_refresh_odds(self):
        """Re-fetch odds and recalculate projections."""
        self.notify("Refreshing odds...", severity="information")
        self.run_worker(self._refresh_odds_worker, thread=True)

    async def _refresh_odds_worker(self):
        """Background worker to refresh odds."""
        try:
            from data.odds import refresh_odds
            from model.games import calc_expected_total_games
            from model.projections import project_all, get_value_tiers

            futures, series = refresh_odds()

            # Recalculate expected games for each team
            team_games = {}
            for p in self.all_players:
                if p.team not in team_games:
                    champ_prob = futures.get(p.team, 0.01)
                    total, breakdown = calc_expected_total_games(
                        p.team, p.seed, p.conference, champ_prob, series
                    )
                    team_games[p.team] = (total, breakdown)

                total, breakdown = team_games[p.team]
                p.expected_games = total
                p.games_breakdown = breakdown

            project_all(self.all_players)
            get_value_tiers(self.all_players)

            # Refresh UI on main thread
            self.call_from_thread(self._refresh_board)
            self.call_from_thread(self.notify, "Odds refreshed!", severity="information")

        except Exception as e:
            self.call_from_thread(self.notify, f"Error: {e}", severity="error")

    def _refresh_board(self):
        board = self.query_one("#player-table", DraftBoard)
        rerank(self.all_players)
        board.populate(self.all_players)
        self._update_status()

    def action_set_injury(self):
        """Prompt to set a player's injury status."""
        board = self.query_one("#player-table", DraftBoard)
        player = board.get_selected_player()
        if not player:
            self.notify("Select a player first", severity="warning")
            return

        # Cycle through statuses
        statuses = ["Healthy", "Questionable", "Doubtful", "Out"]
        current_idx = statuses.index(player.injury_status) if player.injury_status in statuses else 0
        next_status = statuses[(current_idx + 1) % len(statuses)]
        player.injury_status = next_status

        board.populate(self.all_players)
        detail = self.query_one("#player-detail", PlayerDetail)
        detail.show_player(player)
        self.notify(f"{player.name}: {next_status}")

    def action_set_position(self):
        """Change your draft position."""
        self.draft_position = (self.draft_position % NUM_TEAMS) + 1
        tracker = self.query_one("#draft-tracker", DraftTracker)
        tracker.your_position = self.draft_position
        tracker.refresh_display()
        self._update_status()
        self.notify(f"Draft position set to {self.draft_position}")

    def _update_status(self):
        tracker = self.query_one("#draft-tracker", DraftTracker)
        status = self.query_one("#status-bar", StatusBar)

        if tracker.current_pick <= tracker.total_picks:
            team = tracker.get_team_for_pick(tracker.current_pick)
            rnd = tracker.get_round_for_pick(tracker.current_pick)
            yours = " ** YOUR PICK **" if tracker.is_your_pick() else ""
            available = len([p for p in self.all_players if not p.is_drafted])
            status.update(
                f"Pick #{tracker.current_pick} | Round {rnd} | Team {team} | "
                f"You: Team {self.draft_position} | "
                f"{available} available{yours}"
            )
        else:
            status.update("DRAFT COMPLETE")
