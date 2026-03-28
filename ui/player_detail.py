"""Player detail panel widget."""

from textual.widgets import Static
from model.players import Player


class PlayerDetail(Static):
    """Shows expanded stats for a selected player."""

    def show_player(self, player: Player | None):
        if player is None:
            self.update("[dim]Select a player to see details[/]")
            return

        lines = []
        lines.append(f"[bold]{player.name}[/] | {player.team} | {player.position}")
        lines.append(f"Seed: {player.seed} | Conference: {player.conference}")
        lines.append("")

        # Season averages
        lines.append("[bold]Season Averages:[/]")
        lines.append(f"  PTS: {player.pts:.1f}  REB: {player.reb:.1f}  AST: {player.ast:.1f}")
        lines.append(f"  MIN: {player.min:.1f}  GP: {player.games_played}  USG: {player.usg_pct:.1%}")
        lines.append(f"  Fantasy/G: [bold]{player.season_fantasy_avg:.1f}[/]")
        lines.append("")

        # Playoff adjustment
        method = player.adj_details.get("method", "archetype")
        lines.append("[bold]Playoff Adjustment:[/]")
        lines.append(f"  Factor: [bold]{player.playoff_adj_factor:.3f}x[/] ({method})")
        if method == "player_specific":
            lines.append(f"  Career Playoff Fantasy/G: {player.adj_details.get('playoff_fantasy', '?')}")
            lines.append(f"  Career Regular Fantasy/G: {player.adj_details.get('reg_fantasy', '?')}")
            lines.append(f"  Minutes Diff: {player.adj_details.get('min_diff', '?'):+.1f}")
            lines.append(f"  Playoff Games: {player.adj_details.get('playoff_games', 0)}")
        lines.append("")

        # Expected games
        lines.append("[bold]Expected Games:[/]")
        lines.append(f"  Total: [bold]{player.expected_games:.1f}[/]")
        for rnd, games in player.games_breakdown.items():
            if games > 0.01:
                lines.append(f"  {rnd.upper()}: {games:.1f}")
        lines.append("")

        # Projection
        lines.append("[bold]PROJECTION:[/]")
        lines.append(f"  [bold]{player.projected_fantasy_pts:.1f} total fantasy pts[/]")
        lines.append(f"  = {player.season_fantasy_avg:.1f}/g x {player.playoff_adj_factor:.2f} adj x {player.expected_games:.1f} games")
        lines.append("")

        # Injury
        status_color = {
            "Healthy": "green",
            "Questionable": "yellow",
            "Doubtful": "#ff6600",
            "Out": "red",
        }.get(player.injury_status, "white")
        lines.append(f"[bold]Injury:[/] [{status_color}]{player.injury_status}[/]")
        if player.injury_note:
            lines.append(f"  {player.injury_note}")

        self.update("\n".join(lines))

    def on_mount(self):
        self.update("[dim]Select a player to see details[/]")
