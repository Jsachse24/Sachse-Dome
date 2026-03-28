"""Generate draft_board.html with ~150 realistic test players."""

import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pathlib import Path
from model.games import calc_expected_total_games

TEAMS = [
    ("OKC", "West", 1, 0.18), ("SAS", "West", 2, 0.04), ("LAL", "West", 3, 0.06),
    ("DEN", "West", 4, 0.08), ("MIN", "West", 5, 0.05), ("HOU", "West", 6, 0.03),
    ("PHX", "West", 7, 0.02), ("LAC", "West", 8, 0.01), ("POR", "West", 9, 0.01),
    ("GSW", "West", 10, 0.02),
    ("DET", "East", 1, 0.02), ("BOS", "East", 2, 0.15), ("NYK", "East", 3, 0.10),
    ("CLE", "East", 4, 0.12), ("ATL", "East", 5, 0.03), ("TOR", "East", 6, 0.02),
    ("PHI", "East", 7, 0.02), ("ORL", "East", 8, 0.02), ("CHA", "East", 9, 0.01),
    ("MIA", "East", 10, 0.01),
]

team_info = {}
for abbr, conf, seed, cp in TEAMS:
    total, breakdown = calc_expected_total_games(abbr, seed, conf, cp)
    team_info[abbr] = {"conf": conf, "seed": seed, "champ_prob": cp, "exp_games": total, "breakdown": breakdown}

# (name, team, pos, pts, reb, ast, min, gp, usg, has_playoff_hist, adj, injury_status, injury_note)
PLAYERS = [
    # === OKC (1-seed West) ===
    ("Shai Gilgeous-Alexander", "OKC", "G", 32.1, 5.5, 6.2, 34.8, 70, 0.341, True, 1.08, "Healthy", ""),
    ("Jalen Williams", "OKC", "F", 21.5, 5.8, 5.1, 33.0, 68, 0.245, True, 1.03, "Healthy", ""),
    ("Chet Holmgren", "OKC", "C", 16.8, 8.5, 2.4, 29.5, 60, 0.198, False, 1.05, "Healthy", ""),
    ("Lu Dort", "OKC", "G", 11.2, 4.0, 1.8, 28.5, 65, 0.155, True, 0.95, "Healthy", ""),
    ("Isaiah Hartenstein", "OKC", "C", 10.5, 9.2, 2.8, 26.0, 62, 0.145, True, 0.97, "Healthy", ""),
    ("Alex Caruso", "OKC", "G", 9.5, 4.2, 3.5, 27.0, 64, 0.135, True, 0.95, "Healthy", ""),
    ("Isaiah Joe", "OKC", "G", 10.8, 2.5, 1.5, 22.0, 66, 0.148, False, 0.95, "Healthy", ""),
    ("Aaron Wiggins", "OKC", "G", 8.5, 3.0, 1.2, 20.0, 60, 0.125, False, 0.95, "Healthy", ""),
    # === SAS (2-seed West) ===
    ("Victor Wembanyama", "SAS", "C", 25.2, 10.8, 3.8, 33.5, 68, 0.285, True, 1.05, "Healthy", ""),
    ("Devin Vassell", "SAS", "G", 17.5, 3.8, 4.5, 30.0, 55, 0.225, True, 0.98, "Healthy", ""),
    ("Jeremy Sochan", "SAS", "F", 13.2, 6.5, 3.2, 28.0, 64, 0.178, False, 0.95, "Healthy", ""),
    ("Keldon Johnson", "SAS", "F", 12.5, 4.0, 2.0, 25.0, 62, 0.168, False, 0.95, "Healthy", ""),
    ("Tre Jones", "SAS", "G", 9.0, 2.5, 5.0, 24.0, 60, 0.138, False, 0.95, "Healthy", ""),
    ("Stephon Castle", "SAS", "G", 12.0, 3.5, 3.5, 26.0, 58, 0.165, False, 0.95, "Healthy", ""),
    ("Zach Collins", "SAS", "C", 8.5, 5.5, 2.0, 20.0, 55, 0.128, True, 0.95, "Healthy", ""),
    # === LAL (3-seed West) ===
    ("LeBron James", "LAL", "F", 23.5, 7.8, 8.9, 33.8, 60, 0.285, True, 1.12, "Healthy", ""),
    ("Anthony Davis", "LAL", "C", 25.8, 11.5, 3.2, 34.5, 62, 0.298, True, 1.10, "Questionable", "Knee soreness"),
    ("Austin Reaves", "LAL", "G", 18.2, 4.5, 5.8, 33.0, 70, 0.228, True, 1.02, "Healthy", ""),
    ("Dalton Knecht", "LAL", "G", 13.5, 3.8, 2.1, 25.0, 68, 0.185, False, 0.95, "Healthy", ""),
    ("Rui Hachimura", "LAL", "F", 12.0, 5.0, 1.5, 24.0, 60, 0.165, True, 0.95, "Healthy", ""),
    ("D'Angelo Russell", "LAL", "G", 14.5, 2.5, 5.0, 26.0, 55, 0.195, True, 0.98, "Healthy", ""),
    ("Jaxson Hayes", "LAL", "C", 7.5, 4.5, 0.8, 16.0, 58, 0.115, False, 0.95, "Healthy", ""),
    # === DEN (4-seed West) ===
    ("Nikola Jokic", "DEN", "C", 26.3, 12.5, 9.1, 34.2, 72, 0.312, True, 1.15, "Healthy", ""),
    ("Jamal Murray", "DEN", "G", 20.8, 4.0, 6.5, 32.5, 58, 0.265, True, 1.06, "Healthy", ""),
    ("Michael Porter Jr.", "DEN", "F", 16.5, 7.2, 1.5, 29.0, 60, 0.195, True, 0.98, "Healthy", ""),
    ("Aaron Gordon", "DEN", "F", 13.8, 6.2, 3.0, 30.5, 65, 0.165, True, 1.00, "Healthy", ""),
    ("Christian Braun", "DEN", "G", 11.0, 4.5, 2.8, 26.0, 68, 0.155, True, 0.98, "Healthy", ""),
    ("Peyton Watson", "DEN", "F", 8.0, 3.5, 1.5, 20.0, 55, 0.118, False, 0.95, "Healthy", ""),
    ("Russell Westbrook", "DEN", "G", 10.5, 4.0, 4.5, 22.0, 52, 0.185, True, 0.95, "Healthy", ""),
    # === MIN (5-seed West) ===
    ("Anthony Edwards", "MIN", "G", 27.8, 5.9, 5.0, 36.3, 71, 0.298, True, 1.06, "Healthy", ""),
    ("Julius Randle", "MIN", "F", 20.2, 8.5, 4.0, 33.5, 60, 0.265, True, 1.00, "Healthy", ""),
    ("Rudy Gobert", "MIN", "C", 10.5, 11.2, 1.5, 30.0, 65, 0.128, True, 0.95, "Healthy", ""),
    ("Jaden McDaniels", "MIN", "F", 12.8, 4.0, 1.5, 32.0, 68, 0.155, True, 0.95, "Healthy", ""),
    ("Mike Conley", "MIN", "G", 9.0, 2.8, 5.5, 25.0, 55, 0.138, True, 0.95, "Healthy", ""),
    ("Naz Reid", "MIN", "C", 12.5, 5.5, 1.5, 22.0, 62, 0.175, True, 0.98, "Healthy", ""),
    ("Nickeil Alexander-Walker", "MIN", "G", 8.5, 2.0, 2.0, 20.0, 58, 0.128, False, 0.95, "Healthy", ""),
    # === HOU (6-seed West) ===
    ("Jalen Green", "HOU", "G", 22.5, 4.0, 3.8, 33.5, 68, 0.275, False, 1.05, "Healthy", ""),
    ("Alperen Sengun", "HOU", "C", 18.2, 9.5, 4.5, 31.0, 65, 0.245, False, 1.05, "Healthy", ""),
    ("Jabari Smith Jr.", "HOU", "F", 14.5, 7.0, 1.5, 30.0, 62, 0.178, False, 0.95, "Healthy", ""),
    ("Fred VanVleet", "HOU", "G", 14.0, 3.5, 6.0, 30.0, 60, 0.195, True, 0.98, "Healthy", ""),
    ("Dillon Brooks", "HOU", "F", 11.5, 3.0, 1.8, 28.0, 65, 0.158, True, 0.95, "Healthy", ""),
    ("Amen Thompson", "HOU", "G", 12.0, 5.5, 3.5, 26.0, 58, 0.168, False, 0.95, "Healthy", ""),
    ("Cam Whitmore", "HOU", "F", 9.5, 3.5, 1.0, 18.0, 50, 0.145, False, 0.95, "Healthy", ""),
    ("Tari Eason", "HOU", "F", 8.0, 5.0, 1.0, 18.0, 52, 0.125, False, 0.95, "Healthy", ""),
    # === PHX (7-seed West, play-in) ===
    ("Kevin Durant", "PHX", "F", 26.5, 6.5, 4.2, 35.5, 55, 0.305, True, 1.10, "Questionable", "Calf tightness"),
    ("Devin Booker", "PHX", "G", 25.8, 4.2, 6.8, 34.0, 63, 0.295, True, 1.05, "Healthy", ""),
    ("Bradley Beal", "PHX", "G", 16.5, 3.5, 4.5, 28.0, 48, 0.215, True, 0.98, "Healthy", ""),
    ("Jusuf Nurkic", "PHX", "C", 9.5, 8.5, 2.0, 24.0, 58, 0.135, True, 0.95, "Healthy", ""),
    ("Grayson Allen", "PHX", "G", 11.0, 3.0, 2.5, 26.0, 60, 0.155, True, 0.95, "Healthy", ""),
    ("Royce O'Neale", "PHX", "F", 7.5, 4.0, 2.5, 22.0, 62, 0.108, True, 0.95, "Healthy", ""),
    # === LAC (8-seed West, play-in) ===
    ("James Harden", "LAC", "G", 20.5, 5.5, 8.2, 33.0, 60, 0.285, True, 1.02, "Healthy", ""),
    ("Norman Powell", "LAC", "G", 19.8, 3.2, 2.5, 30.0, 65, 0.248, True, 0.98, "Healthy", ""),
    ("Ivica Zubac", "LAC", "C", 12.0, 10.0, 2.0, 28.0, 68, 0.158, True, 0.95, "Healthy", ""),
    ("Terance Mann", "LAC", "G", 9.0, 3.5, 2.5, 22.0, 55, 0.135, True, 0.95, "Healthy", ""),
    ("Derrick Jones Jr.", "LAC", "F", 8.0, 3.0, 1.0, 20.0, 58, 0.118, True, 0.95, "Healthy", ""),
    # === POR (9-seed West, play-in) ===
    ("Anfernee Simons", "POR", "G", 22.0, 3.0, 5.5, 33.5, 62, 0.268, False, 1.05, "Healthy", ""),
    ("Jerami Grant", "POR", "F", 16.5, 4.2, 2.5, 30.0, 58, 0.218, True, 0.95, "Healthy", ""),
    ("Deandre Ayton", "POR", "C", 15.0, 9.0, 1.5, 28.0, 60, 0.198, True, 0.95, "Healthy", ""),
    ("Shaedon Sharpe", "POR", "G", 15.5, 3.5, 2.5, 28.0, 55, 0.208, False, 0.95, "Healthy", ""),
    ("Scoot Henderson", "POR", "G", 11.0, 3.0, 5.0, 24.0, 58, 0.168, False, 0.95, "Healthy", ""),
    ("Deni Avdija", "POR", "F", 13.0, 6.0, 3.5, 30.0, 62, 0.178, False, 0.95, "Healthy", ""),
    ("Robert Williams III", "POR", "C", 7.0, 6.5, 1.0, 18.0, 45, 0.108, True, 0.95, "Questionable", "Knee management"),
    # === GSW (10-seed West, play-in) ===
    ("Stephen Curry", "GSW", "G", 24.5, 4.5, 6.0, 32.0, 62, 0.305, True, 1.12, "Healthy", ""),
    ("Andrew Wiggins", "GSW", "F", 15.0, 4.8, 2.2, 29.5, 60, 0.195, True, 0.98, "Healthy", ""),
    ("Draymond Green", "GSW", "F", 8.5, 6.5, 5.8, 28.0, 58, 0.145, True, 1.05, "Healthy", ""),
    ("Jonathan Kuminga", "GSW", "F", 14.5, 5.0, 2.0, 26.0, 55, 0.198, False, 0.95, "Healthy", ""),
    ("Brandin Podziemski", "GSW", "G", 10.0, 5.0, 4.0, 28.0, 64, 0.148, False, 0.95, "Healthy", ""),
    ("Kevon Looney", "GSW", "C", 5.5, 7.0, 2.0, 20.0, 60, 0.088, True, 0.95, "Healthy", ""),
    ("Buddy Hield", "GSW", "G", 12.5, 2.5, 2.0, 24.0, 62, 0.175, True, 0.95, "Healthy", ""),
    # === DET (1-seed East) ===
    ("Cade Cunningham", "DET", "G", 24.2, 6.2, 9.3, 35.8, 62, 0.305, False, 1.05, "Out", "Knee - MCL sprain, expected to miss 4-6 weeks"),
    ("Jaden Ivey", "DET", "G", 17.5, 4.0, 4.8, 31.0, 68, 0.225, False, 1.05, "Healthy", ""),
    ("Ausar Thompson", "DET", "F", 12.0, 6.5, 2.5, 28.0, 55, 0.165, False, 0.95, "Healthy", ""),
    ("Jalen Duren", "DET", "C", 13.0, 10.0, 2.0, 28.0, 65, 0.178, False, 0.95, "Healthy", ""),
    ("Tobias Harris", "DET", "F", 11.5, 5.0, 2.5, 26.0, 60, 0.155, True, 0.95, "Healthy", ""),
    ("Tim Hardaway Jr.", "DET", "G", 11.0, 2.5, 2.0, 24.0, 58, 0.158, True, 0.95, "Healthy", ""),
    ("Malik Beasley", "DET", "G", 10.0, 2.0, 1.5, 22.0, 62, 0.148, True, 0.95, "Healthy", ""),
    # === BOS (2-seed East) ===
    ("Jayson Tatum", "BOS", "F", 27.4, 8.9, 5.2, 36.1, 68, 0.298, True, 1.10, "Healthy", ""),
    ("Jaylen Brown", "BOS", "G", 23.5, 5.5, 3.8, 33.5, 65, 0.268, True, 1.05, "Healthy", ""),
    ("Derrick White", "BOS", "G", 16.0, 4.2, 4.5, 30.5, 66, 0.198, True, 1.02, "Healthy", ""),
    ("Kristaps Porzingis", "BOS", "C", 18.5, 7.8, 1.8, 28.0, 52, 0.235, True, 1.00, "Questionable", "Ankle soreness"),
    ("Jrue Holiday", "BOS", "G", 13.5, 5.0, 4.5, 30.0, 62, 0.175, True, 1.02, "Healthy", ""),
    ("Al Horford", "BOS", "C", 7.5, 5.0, 2.5, 22.0, 55, 0.108, True, 1.00, "Healthy", ""),
    ("Payton Pritchard", "BOS", "G", 11.0, 2.5, 3.0, 22.0, 68, 0.155, True, 0.98, "Healthy", ""),
    # === NYK (3-seed East) ===
    ("Jalen Brunson", "NYK", "G", 26.5, 3.5, 7.5, 35.0, 68, 0.318, True, 1.08, "Healthy", ""),
    ("Karl-Anthony Towns", "NYK", "C", 22.0, 11.5, 3.0, 33.5, 62, 0.265, True, 1.02, "Healthy", ""),
    ("Mikal Bridges", "NYK", "F", 17.8, 4.0, 3.2, 33.0, 70, 0.208, True, 0.98, "Healthy", ""),
    ("OG Anunoby", "NYK", "F", 15.5, 5.0, 1.8, 31.0, 55, 0.178, True, 0.98, "Healthy", ""),
    ("Josh Hart", "NYK", "G", 10.0, 8.5, 4.0, 30.0, 68, 0.138, True, 1.02, "Healthy", ""),
    ("Donte DiVincenzo", "NYK", "G", 11.0, 3.0, 3.0, 24.0, 60, 0.158, True, 0.98, "Healthy", ""),
    ("Mitchell Robinson", "NYK", "C", 6.5, 8.5, 0.8, 22.0, 42, 0.095, True, 0.95, "Questionable", "Ankle"),
    # === CLE (4-seed East) ===
    ("Donovan Mitchell", "CLE", "G", 24.1, 4.5, 4.8, 33.5, 69, 0.278, True, 1.06, "Healthy", ""),
    ("Darius Garland", "CLE", "G", 21.5, 2.8, 7.2, 32.0, 64, 0.265, True, 1.02, "Healthy", ""),
    ("Evan Mobley", "CLE", "F", 18.5, 9.2, 3.5, 33.0, 70, 0.228, True, 1.05, "Healthy", ""),
    ("Jarrett Allen", "CLE", "C", 13.8, 10.0, 1.5, 30.0, 66, 0.158, True, 0.95, "Healthy", ""),
    ("Max Strus", "CLE", "G", 11.0, 3.0, 2.5, 26.0, 62, 0.155, True, 0.95, "Healthy", ""),
    ("Caris LeVert", "CLE", "G", 10.0, 3.0, 3.5, 22.0, 58, 0.148, True, 0.95, "Healthy", ""),
    ("Georges Niang", "CLE", "F", 7.5, 2.5, 1.5, 18.0, 60, 0.108, True, 0.95, "Healthy", ""),
    # === ATL (5-seed East) ===
    ("Trae Young", "ATL", "G", 22.8, 3.2, 11.1, 34.0, 72, 0.295, True, 0.95, "Healthy", ""),
    ("Jalen Johnson", "ATL", "F", 18.5, 8.5, 4.0, 33.0, 60, 0.228, False, 1.05, "Healthy", ""),
    ("De'Andre Hunter", "ATL", "F", 14.5, 4.0, 1.8, 28.0, 55, 0.185, True, 0.95, "Healthy", ""),
    ("Clint Capela", "ATL", "C", 9.5, 9.0, 1.0, 24.0, 60, 0.128, True, 0.95, "Healthy", ""),
    ("Bogdan Bogdanovic", "ATL", "G", 12.0, 3.0, 3.0, 24.0, 52, 0.168, True, 0.95, "Healthy", ""),
    ("Dyson Daniels", "ATL", "G", 10.5, 4.0, 3.5, 28.0, 62, 0.148, False, 0.95, "Healthy", ""),
    ("Onyeka Okongwu", "ATL", "C", 9.0, 6.5, 1.0, 20.0, 55, 0.135, False, 0.95, "Healthy", ""),
    # === TOR (6-seed East) ===
    ("Scottie Barnes", "TOR", "F", 21.0, 8.0, 6.5, 35.0, 68, 0.258, True, 1.03, "Healthy", ""),
    ("RJ Barrett", "TOR", "F", 19.5, 5.5, 4.0, 33.5, 64, 0.245, True, 0.98, "Healthy", ""),
    ("Immanuel Quickley", "TOR", "G", 16.0, 3.5, 6.0, 30.0, 62, 0.215, False, 0.95, "Healthy", ""),
    ("Jakob Poeltl", "TOR", "C", 11.5, 8.5, 2.0, 26.0, 65, 0.155, True, 0.95, "Healthy", ""),
    ("Gradey Dick", "TOR", "G", 13.0, 3.0, 2.0, 26.0, 64, 0.178, False, 0.95, "Healthy", ""),
    ("Bruce Brown", "TOR", "G", 8.5, 4.0, 3.0, 22.0, 55, 0.128, True, 0.98, "Healthy", ""),
    # === PHI (7-seed East, play-in) ===
    ("Tyrese Maxey", "PHI", "G", 26.0, 3.5, 5.8, 35.0, 65, 0.295, True, 1.03, "Healthy", ""),
    ("Joel Embiid", "PHI", "C", 28.0, 10.5, 4.0, 32.0, 40, 0.365, True, 1.08, "Doubtful", "Knee management - limited availability"),
    ("Paul George", "PHI", "F", 19.5, 5.0, 4.5, 30.5, 52, 0.235, True, 1.02, "Healthy", ""),
    ("Caleb Martin", "PHI", "F", 10.0, 4.5, 2.0, 26.0, 60, 0.148, True, 0.95, "Healthy", ""),
    ("Kelly Oubre Jr.", "PHI", "G", 13.0, 4.0, 1.5, 28.0, 58, 0.178, True, 0.95, "Healthy", ""),
    ("Kyle Lowry", "PHI", "G", 7.5, 3.0, 4.5, 22.0, 50, 0.115, True, 0.95, "Healthy", ""),
    # === ORL (8-seed East, play-in) ===
    ("Paolo Banchero", "ORL", "F", 23.0, 7.0, 4.5, 34.0, 55, 0.275, True, 1.03, "Healthy", ""),
    ("Franz Wagner", "ORL", "F", 21.5, 5.5, 5.0, 33.5, 60, 0.248, True, 1.02, "Healthy", ""),
    ("Jalen Suggs", "ORL", "G", 14.0, 3.5, 4.5, 30.0, 65, 0.188, True, 0.95, "Healthy", ""),
    ("Wendell Carter Jr.", "ORL", "C", 10.5, 7.5, 2.5, 26.0, 50, 0.148, True, 0.95, "Questionable", "Plantar fascia"),
    ("Cole Anthony", "ORL", "G", 11.5, 4.0, 4.0, 24.0, 55, 0.168, False, 0.95, "Healthy", ""),
    ("Jonathan Isaac", "ORL", "F", 7.0, 4.5, 1.0, 18.0, 42, 0.108, True, 0.95, "Healthy", ""),
    # === CHA (9-seed East, play-in) ===
    ("LaMelo Ball", "CHA", "G", 25.5, 5.5, 8.0, 33.0, 45, 0.315, False, 1.05, "Questionable", "Ankle - game-time decision"),
    ("Brandon Miller", "CHA", "F", 18.5, 5.0, 2.8, 32.0, 66, 0.228, False, 0.95, "Healthy", ""),
    ("Miles Bridges", "CHA", "F", 17.0, 6.5, 3.0, 32.0, 65, 0.218, False, 0.95, "Healthy", ""),
    ("Mark Williams", "CHA", "C", 10.5, 8.0, 1.5, 24.0, 55, 0.148, False, 0.95, "Healthy", ""),
    ("Nick Richards", "CHA", "C", 8.5, 6.0, 0.8, 18.0, 52, 0.128, False, 0.95, "Healthy", ""),
    ("Tre Mann", "CHA", "G", 11.0, 2.5, 3.5, 22.0, 60, 0.158, False, 0.95, "Healthy", ""),
    # === MIA (10-seed East, play-in) ===
    ("Bam Adebayo", "MIA", "C", 19.5, 10.5, 4.5, 33.5, 68, 0.238, True, 1.05, "Healthy", ""),
    ("Tyler Herro", "MIA", "G", 22.0, 5.0, 4.8, 33.0, 62, 0.268, True, 0.98, "Healthy", ""),
    ("Jimmy Butler", "MIA", "F", 18.0, 5.5, 4.0, 30.0, 42, 0.255, True, 1.15, "Questionable", "Load management"),
    ("Terry Rozier", "MIA", "G", 15.5, 3.5, 4.0, 30.0, 58, 0.208, True, 0.98, "Healthy", ""),
    ("Jaime Jaquez Jr.", "MIA", "F", 12.5, 4.5, 2.5, 28.0, 65, 0.175, False, 0.95, "Healthy", ""),
    ("Nikola Jovic", "MIA", "F", 9.5, 4.0, 2.0, 20.0, 55, 0.138, False, 0.95, "Healthy", ""),
    ("Duncan Robinson", "MIA", "G", 9.0, 2.5, 2.0, 22.0, 60, 0.128, True, 0.95, "Healthy", ""),
    # === Extra rotation players to hit ~150 ===
    ("Kenrich Williams", "OKC", "F", 7.0, 3.5, 2.0, 18.0, 55, 0.105, True, 0.95, "Healthy", ""),
    ("Julian Champagnie", "SAS", "F", 8.0, 3.0, 1.0, 18.0, 50, 0.118, False, 0.95, "Healthy", ""),
    ("Gabe Vincent", "LAL", "G", 8.0, 2.0, 2.5, 18.0, 48, 0.118, True, 0.95, "Healthy", ""),
    ("Julian Strawther", "DEN", "G", 7.5, 2.5, 1.5, 16.0, 50, 0.108, False, 0.95, "Healthy", ""),
    ("Rob Dillingham", "MIN", "G", 8.5, 2.0, 3.0, 16.0, 48, 0.128, False, 0.95, "Healthy", ""),
    ("Steven Adams", "HOU", "C", 6.0, 7.5, 1.5, 18.0, 50, 0.088, True, 0.95, "Healthy", ""),
    ("Eric Gordon", "PHX", "G", 8.5, 1.5, 1.5, 18.0, 52, 0.128, True, 0.95, "Healthy", ""),
    ("Bones Hyland", "LAC", "G", 9.0, 2.0, 3.0, 18.0, 52, 0.138, False, 0.95, "Healthy", ""),
    ("Toumani Camara", "POR", "F", 9.0, 4.5, 1.5, 22.0, 58, 0.128, False, 0.95, "Healthy", ""),
    ("Trayce Jackson-Davis", "GSW", "C", 6.5, 4.5, 1.0, 14.0, 52, 0.098, False, 0.95, "Healthy", ""),
    ("Ron Holland", "DET", "F", 8.0, 3.5, 1.5, 18.0, 50, 0.118, False, 0.95, "Healthy", ""),
    ("Sam Hauser", "BOS", "F", 8.5, 2.5, 1.0, 18.0, 58, 0.118, True, 0.95, "Healthy", ""),
    ("Miles McBride", "NYK", "G", 8.0, 2.0, 2.5, 18.0, 55, 0.118, False, 0.95, "Healthy", ""),
    ("Dean Wade", "CLE", "F", 7.0, 3.5, 1.5, 18.0, 55, 0.105, True, 0.95, "Healthy", ""),
    ("Zaccharie Risacher", "ATL", "F", 10.0, 4.0, 1.5, 24.0, 60, 0.148, False, 0.95, "Healthy", ""),
]

# Build player data
player_data = []
for i, (name, team, pos, pts, reb, ast, mins, gp, usg, has_hist, adj, inj_status, inj_note) in enumerate(PLAYERS):
    ti = team_info[team]
    fantasy_avg = pts + reb + ast
    exp_games = ti["exp_games"]
    projected = fantasy_avg * adj * exp_games

    player_data.append({
        "id": 200000 + i,
        "name": name,
        "team": team,
        "position": pos,
        "conference": ti["conf"],
        "seed": ti["seed"],
        "pts": pts, "reb": reb, "ast": ast, "min": mins,
        "games_played": gp,
        "usg_pct": usg,
        "fantasy_avg": round(fantasy_avg, 1),
        "adj": adj,
        "has_playoff_history": has_hist,
        "adj_details": {
            "method": "player_specific" if has_hist else "archetype",
            "playoff_games": 50 if has_hist else 0,
            "reg_fantasy": round(fantasy_avg * 0.95, 1) if has_hist else None,
            "playoff_fantasy": round(fantasy_avg * adj * 0.95, 1) if has_hist else None,
            "min_diff": round((adj - 1.0) * 10, 1) if has_hist else None,
        },
        "expected_games": round(exp_games, 2),
        "games_breakdown": {k: round(v, 2) for k, v in ti["breakdown"].items()},
        "projected": round(projected, 1),
        "tier": "",
        "injury_status": inj_status,
        "injury_note": inj_note,
    })

# Sort and assign tiers
player_data.sort(key=lambda x: x["projected"], reverse=True)
if player_data:
    max_p = player_data[0]["projected"]
    min_p = player_data[-1]["projected"]
    spread = max_p - min_p or 1
    tiers = ["Elite", "Strong", "Solid", "Value", "Depth"]
    for i, p in enumerate(player_data):
        p["rank"] = i + 1
        pct = (p["projected"] - min_p) / spread
        idx = min(int((1 - pct) * 5), 4)
        p["tier"] = tiers[idx]

team_data = [
    {"team_abbr": abbr, "team_name": abbr, "conference": conf, "seed": seed,
     "wins": 50, "losses": 32, "champ_prob": cp}
    for abbr, conf, seed, cp in TEAMS
]

config_data = {"num_teams": 10, "roster_size": 10, "your_draft_position": 1}

template = Path(os.path.join(os.path.dirname(__file__), "template.html")).read_text()
html = template.replace("__PLAYER_DATA__", json.dumps(player_data))
html = html.replace("__TEAM_DATA__", json.dumps(team_data))
html = html.replace("__CONFIG__", json.dumps(config_data))

out = Path(os.path.join(os.path.dirname(__file__), "draft_board.html"))
out.write_text(html)
print(f"Generated {out} ({len(player_data)} players, {len(html):,} bytes)")

print(f"\nTop 15:")
for p in player_data[:15]:
    print(f"  {p['rank']:3}. {p['name']:30s} {p['team']} | Proj: {p['projected']:6.0f} | "
          f"Avg: {p['fantasy_avg']:5.1f} | Games: {p['expected_games']:5.1f} | Adj: {p['adj']:.2f} | {p['tier']}")

print(f"\nInjured players:")
for p in player_data:
    if p["injury_status"] != "Healthy":
        print(f"  {p['name']:30s} {p['team']} | {p['injury_status']}: {p['injury_note']}")
