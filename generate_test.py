"""Generate draft_board.html with ~150 realistic test players.
Updated for 2025-26 season rosters/trades as of March 2026.
Stats sourced from Basketball Monster rankings + Basketball Reference.
"""

import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pathlib import Path
from model.games import calc_expected_total_games

# === STANDINGS (as of late March 2026) ===
TEAMS = [
    # West
    ("OKC", "West", 1, 0.22),
    ("SAS", "West", 2, 0.12),
    ("LAL", "West", 3, 0.10),
    ("DEN", "West", 4, 0.08),
    ("MIN", "West", 5, 0.05),
    ("HOU", "West", 6, 0.06),
    ("PHX", "West", 7, 0.02),
    ("LAC", "West", 8, 0.03),
    ("POR", "West", 9, 0.01),
    ("GSW", "West", 10, 0.04),
    # East
    ("DET", "East", 1, 0.08),
    ("BOS", "East", 2, 0.12),
    ("NYK", "East", 3, 0.10),
    ("CLE", "East", 4, 0.08),
    ("ATL", "East", 5, 0.02),
    ("TOR", "East", 6, 0.02),
    ("PHI", "East", 7, 0.02),
    ("ORL", "East", 8, 0.02),
    ("CHA", "East", 9, 0.01),
    ("MIA", "East", 10, 0.01),
]

team_info = {}
for abbr, conf, seed, cp in TEAMS:
    total, breakdown = calc_expected_total_games(abbr, seed, conf, cp)
    team_info[abbr] = {"conf": conf, "seed": seed, "champ_prob": cp, "exp_games": total, "breakdown": breakdown}

def age_factor(age):
    if age < 23: return 0.98
    if age <= 27: return 1.02
    if age <= 31: return 1.00
    if age <= 34: return 0.97
    if age <= 37: return 0.93
    return 0.88

# (name, team, pos, pts, reb, ast, stl, blk, threes, min, gp, usg, has_playoff_hist, adj, age, injury_status, injury_note)
# Stats from Basketball Monster / Basketball Reference as of March 2026
PLAYERS = [
    # === OKC Thunder (1-seed West) ===
    ("Shai Gilgeous-Alexander", "OKC", "G", 31.5, 4.4, 6.6, 1.4, 0.8, 1.7, 33.5, 61, 0.341, True, 1.08, 27, "Healthy", ""),
    ("Jalen Williams", "OKC", "F", 21.5, 5.8, 5.1, 1.2, 0.7, 1.8, 33.0, 68, 0.245, True, 1.03, 23, "Healthy", ""),
    ("Chet Holmgren", "OKC", "C", 17.1, 8.9, 1.7, 0.5, 1.9, 1.2, 29.2, 63, 0.198, False, 1.05, 23, "Healthy", ""),
    ("Lu Dort", "OKC", "G", 11.2, 4.0, 1.8, 1.0, 0.3, 1.5, 28.5, 65, 0.155, True, 0.95, 26, "Healthy", ""),
    ("Isaiah Hartenstein", "OKC", "C", 10.5, 9.2, 2.8, 0.8, 0.7, 0.3, 26.0, 62, 0.145, True, 0.97, 27, "Healthy", ""),
    ("Alex Caruso", "OKC", "G", 9.5, 4.2, 3.5, 1.5, 0.5, 1.2, 27.0, 64, 0.135, True, 0.95, 32, "Healthy", ""),
    ("Isaiah Joe", "OKC", "G", 10.8, 2.5, 1.5, 0.6, 0.2, 2.5, 22.0, 66, 0.148, False, 0.95, 26, "Healthy", ""),
    ("Aaron Wiggins", "OKC", "G", 8.5, 3.0, 1.2, 0.5, 0.3, 1.0, 20.0, 60, 0.125, False, 0.95, 25, "Healthy", ""),
    ("Kenrich Williams", "OKC", "F", 7.0, 3.5, 2.0, 0.7, 0.3, 0.8, 18.0, 55, 0.105, True, 0.95, 31, "Healthy", ""),

    # === SAS Spurs (2-seed West, 55-18) ===
    ("Victor Wembanyama", "SAS", "C", 24.2, 11.2, 3.0, 1.1, 3.1, 1.9, 29.2, 58, 0.285, True, 1.05, 21, "Healthy", ""),
    ("Devin Vassell", "SAS", "G", 17.5, 3.8, 4.5, 1.0, 0.4, 2.5, 30.0, 55, 0.225, True, 0.98, 24, "Healthy", ""),
    ("Stephon Castle", "SAS", "G", 12.0, 3.5, 3.5, 1.1, 0.4, 0.8, 26.0, 62, 0.165, False, 0.95, 20, "Healthy", ""),
    ("Dylan Harper", "SAS", "G", 14.5, 3.2, 4.8, 0.8, 0.2, 1.5, 28.0, 60, 0.188, False, 0.95, 20, "Healthy", ""),
    ("Jeremy Sochan", "SAS", "F", 13.2, 6.5, 3.2, 0.9, 0.5, 1.0, 28.0, 64, 0.178, False, 0.95, 22, "Healthy", ""),
    ("Keldon Johnson", "SAS", "F", 12.5, 4.0, 2.0, 0.6, 0.3, 1.5, 25.0, 62, 0.168, False, 0.95, 26, "Healthy", ""),
    ("Tre Jones", "SAS", "G", 9.0, 2.5, 5.0, 0.8, 0.1, 0.3, 24.0, 60, 0.138, False, 0.95, 26, "Healthy", ""),
    ("Zach Collins", "SAS", "C", 8.5, 5.5, 2.0, 0.4, 0.5, 0.8, 20.0, 55, 0.128, True, 0.95, 28, "Healthy", ""),

    # === LAL Lakers (3-seed West, 47-26) ===
    ("Luka Doncic", "LAL", "G", 33.6, 7.8, 8.3, 1.6, 0.5, 4.0, 35.9, 61, 0.345, True, 1.10, 26, "Healthy", ""),
    ("LeBron James", "LAL", "F", 21.3, 5.8, 6.9, 0.9, 0.5, 1.5, 32.0, 49, 0.255, True, 1.12, 41, "Healthy", ""),
    ("Austin Reaves", "LAL", "G", 23.6, 4.7, 5.6, 1.1, 0.4, 2.3, 34.7, 47, 0.248, True, 1.02, 27, "Healthy", ""),
    ("Dalton Knecht", "LAL", "G", 13.5, 3.8, 2.1, 0.6, 0.3, 2.0, 25.0, 68, 0.185, False, 0.95, 24, "Healthy", ""),
    ("Rui Hachimura", "LAL", "F", 12.0, 5.0, 1.5, 0.5, 0.3, 1.0, 24.0, 60, 0.165, True, 0.95, 27, "Healthy", ""),
    ("D'Angelo Russell", "LAL", "G", 14.5, 2.5, 5.0, 0.8, 0.2, 2.5, 26.0, 55, 0.195, True, 0.98, 30, "Healthy", ""),
    ("DeAndre Ayton", "LAL", "C", 12.5, 8.5, 1.2, 0.5, 0.6, 0.2, 24.0, 58, 0.168, True, 0.95, 27, "Healthy", ""),
    ("Marcus Smart", "LAL", "G", 8.0, 3.0, 4.0, 1.0, 0.3, 1.2, 22.0, 55, 0.128, True, 0.98, 32, "Healthy", ""),
    ("Jaxson Hayes", "LAL", "C", 7.5, 4.5, 0.8, 0.3, 0.8, 0.1, 16.0, 52, 0.115, False, 0.95, 25, "Healthy", ""),

    # === DEN Nuggets (4-seed West) ===
    # MPJ traded to BKN for Cam Johnson (July 2025)
    ("Nikola Jokic", "DEN", "C", 27.8, 12.8, 10.8, 1.4, 0.8, 1.8, 34.8, 58, 0.312, True, 1.15, 31, "Healthy", ""),
    ("Jamal Murray", "DEN", "G", 25.4, 4.4, 7.1, 0.9, 0.3, 3.1, 35.1, 69, 0.265, True, 1.06, 29, "Healthy", ""),
    ("Cam Johnson", "DEN", "F", 14.5, 4.2, 2.0, 0.8, 0.4, 2.8, 29.0, 62, 0.185, True, 0.98, 29, "Healthy", ""),
    ("Aaron Gordon", "DEN", "F", 13.8, 6.2, 3.0, 0.7, 0.5, 1.0, 30.5, 65, 0.165, True, 1.00, 30, "Healthy", ""),
    ("Christian Braun", "DEN", "G", 11.0, 4.5, 2.8, 0.8, 0.3, 1.5, 26.0, 68, 0.155, True, 0.98, 24, "Healthy", ""),
    ("Russell Westbrook", "DEN", "G", 10.5, 4.0, 4.5, 0.8, 0.2, 0.5, 22.0, 52, 0.185, True, 0.95, 37, "Healthy", ""),
    ("Peyton Watson", "DEN", "F", 8.0, 3.5, 1.5, 0.6, 0.7, 0.8, 20.0, 55, 0.118, False, 0.95, 23, "Healthy", ""),
    ("Julian Strawther", "DEN", "G", 7.5, 2.5, 1.5, 0.4, 0.2, 1.5, 16.0, 50, 0.108, False, 0.95, 23, "Healthy", ""),

    # === MIN Timberwolves (5-seed West) ===
    ("Anthony Edwards", "MIN", "G", 29.5, 5.1, 3.7, 1.4, 0.8, 3.4, 35.5, 58, 0.298, True, 1.06, 24, "Healthy", ""),
    ("Julius Randle", "MIN", "F", 20.2, 8.5, 4.0, 0.7, 0.3, 1.5, 33.5, 60, 0.265, True, 1.00, 31, "Healthy", ""),
    ("Rudy Gobert", "MIN", "C", 10.5, 11.2, 1.5, 0.5, 1.5, 0.0, 30.0, 65, 0.128, True, 0.95, 33, "Healthy", ""),
    ("Jaden McDaniels", "MIN", "F", 12.8, 4.0, 1.5, 0.9, 0.5, 1.2, 32.0, 68, 0.155, True, 0.95, 25, "Healthy", ""),
    ("Mike Conley", "MIN", "G", 9.0, 2.8, 5.5, 0.8, 0.2, 1.5, 25.0, 55, 0.138, True, 0.95, 38, "Healthy", ""),
    ("Naz Reid", "MIN", "C", 12.5, 5.5, 1.5, 0.5, 0.8, 1.2, 22.0, 62, 0.175, True, 0.98, 26, "Healthy", ""),
    ("Rob Dillingham", "MIN", "G", 8.5, 2.0, 3.0, 0.5, 0.1, 1.0, 16.0, 48, 0.128, False, 0.95, 21, "Healthy", ""),

    # === HOU Rockets (6-seed West) ===
    ("Kevin Durant", "HOU", "F", 26.0, 5.4, 4.6, 0.9, 0.9, 2.4, 36.4, 70, 0.305, True, 1.10, 37, "Healthy", ""),
    ("Alperen Sengun", "HOU", "C", 18.2, 9.5, 4.5, 0.8, 0.7, 0.5, 31.0, 65, 0.245, False, 1.05, 23, "Healthy", ""),
    ("Amen Thompson", "HOU", "F", 17.9, 7.9, 5.2, 1.5, 0.6, 0.4, 37.3, 71, 0.198, False, 0.95, 22, "Healthy", ""),
    ("Jabari Smith Jr.", "HOU", "F", 14.5, 7.0, 1.5, 0.7, 0.6, 2.0, 30.0, 62, 0.178, False, 0.95, 22, "Healthy", ""),
    ("Fred VanVleet", "HOU", "G", 14.0, 3.5, 6.0, 1.2, 0.3, 2.2, 30.0, 60, 0.195, True, 0.98, 32, "Healthy", ""),
    ("Reed Sheppard", "HOU", "G", 11.5, 2.5, 3.8, 1.0, 0.3, 2.0, 24.0, 60, 0.158, False, 0.95, 21, "Healthy", ""),
    ("Cam Whitmore", "HOU", "F", 9.5, 3.5, 1.0, 0.5, 0.3, 1.2, 18.0, 50, 0.145, False, 0.95, 21, "Healthy", ""),
    ("Tari Eason", "HOU", "F", 8.0, 5.0, 1.0, 1.0, 0.5, 0.5, 18.0, 52, 0.125, False, 0.95, 23, "Healthy", ""),
    ("Steven Adams", "HOU", "C", 6.0, 7.5, 1.5, 0.5, 0.5, 0.0, 18.0, 50, 0.088, True, 0.95, 32, "Healthy", ""),

    # === PHX Suns (7-seed West, play-in) ===
    ("Devin Booker", "PHX", "G", 25.8, 4.2, 6.8, 0.8, 0.3, 2.8, 34.0, 63, 0.295, True, 1.05, 29, "Healthy", ""),
    ("Jalen Green", "PHX", "G", 22.5, 4.0, 3.8, 0.7, 0.3, 3.0, 33.5, 68, 0.275, False, 1.05, 23, "Healthy", ""),
    ("Dillon Brooks", "PHX", "F", 11.5, 3.0, 1.8, 0.8, 0.3, 1.5, 28.0, 65, 0.158, True, 0.95, 30, "Healthy", ""),
    ("Mark Williams", "PHX", "C", 10.5, 8.0, 1.5, 0.4, 1.0, 0.0, 24.0, 58, 0.148, False, 0.95, 23, "Healthy", ""),
    ("Jusuf Nurkic", "PHX", "C", 9.5, 8.5, 2.0, 0.6, 0.5, 0.3, 24.0, 58, 0.135, True, 0.95, 31, "Healthy", ""),
    ("Grayson Allen", "PHX", "G", 11.0, 3.0, 2.5, 0.7, 0.2, 2.2, 26.0, 60, 0.155, True, 0.95, 30, "Healthy", ""),
    ("Royce O'Neale", "PHX", "F", 7.5, 4.0, 2.5, 0.8, 0.3, 1.5, 22.0, 62, 0.108, True, 0.95, 33, "Healthy", ""),

    # === LAC Clippers (8-seed West, play-in) ===
    ("Kawhi Leonard", "LAC", "F", 28.3, 6.3, 3.6, 2.0, 0.4, 2.6, 32.2, 58, 0.298, True, 1.12, 34, "Healthy", ""),
    ("Darius Garland", "LAC", "G", 18.9, 2.4, 6.9, 1.0, 0.2, 2.2, 32.0, 58, 0.248, True, 1.00, 26, "Healthy", ""),
    ("Norman Powell", "LAC", "G", 19.8, 3.2, 2.5, 0.8, 0.3, 2.5, 30.0, 65, 0.248, True, 0.98, 32, "Healthy", ""),
    ("John Collins", "LAC", "F", 12.0, 6.5, 1.5, 0.5, 0.5, 1.0, 24.0, 60, 0.165, True, 0.95, 28, "Healthy", ""),
    ("Bennedict Mathurin", "LAC", "G", 14.0, 3.5, 2.0, 0.6, 0.2, 2.0, 26.0, 58, 0.188, False, 0.95, 23, "Healthy", ""),
    ("Derrick Jones Jr.", "LAC", "F", 8.0, 3.0, 1.0, 0.7, 0.5, 0.8, 20.0, 58, 0.118, True, 0.95, 28, "Healthy", ""),

    # === POR Trail Blazers (9-seed West, play-in) ===
    ("Anfernee Simons", "POR", "G", 22.0, 3.0, 5.5, 0.7, 0.3, 3.5, 33.5, 62, 0.268, False, 1.05, 26, "Healthy", ""),
    ("Donovan Clingan", "POR", "C", 12.4, 11.8, 2.2, 0.6, 1.7, 1.1, 27.2, 69, 0.158, False, 0.95, 21, "Healthy", ""),
    ("Jerami Grant", "POR", "F", 16.5, 4.2, 2.5, 0.8, 0.4, 1.8, 30.0, 58, 0.218, True, 0.95, 31, "Healthy", ""),
    ("Shaedon Sharpe", "POR", "G", 15.5, 3.5, 2.5, 0.6, 0.3, 2.0, 28.0, 55, 0.208, False, 0.95, 22, "Healthy", ""),
    ("Scoot Henderson", "POR", "G", 11.0, 3.0, 5.0, 0.8, 0.2, 1.0, 24.0, 58, 0.168, False, 0.95, 21, "Healthy", ""),
    ("Deni Avdija", "POR", "F", 13.0, 6.0, 3.5, 0.9, 0.4, 1.5, 30.0, 62, 0.178, False, 0.95, 25, "Healthy", ""),
    ("Robert Williams III", "POR", "C", 7.0, 6.5, 1.0, 0.5, 1.2, 0.0, 18.0, 45, 0.108, True, 0.95, 28, "Questionable", "Knee management"),
    ("Toumani Camara", "POR", "F", 9.0, 4.5, 1.5, 0.7, 0.4, 1.0, 22.0, 58, 0.128, False, 0.95, 24, "Healthy", ""),

    # === GSW Warriors (10-seed West, play-in) ===
    ("Stephen Curry", "GSW", "G", 27.2, 3.5, 4.8, 1.1, 0.4, 4.5, 31.3, 39, 0.305, True, 1.12, 37, "Healthy", ""),
    ("Jimmy Butler", "GSW", "F", 20.0, 5.6, 4.9, 1.4, 0.2, 0.8, 31.1, 38, 0.255, True, 1.15, 36, "Healthy", ""),
    ("Kristaps Porzingis", "GSW", "C", 15.9, 7.0, 2.0, 0.6, 1.5, 1.8, 26.0, 25, 0.215, True, 1.00, 30, "Questionable", "Injury management - limited to 25 games"),
    ("Draymond Green", "GSW", "F", 8.5, 6.5, 5.8, 1.0, 0.6, 0.5, 28.0, 58, 0.145, True, 1.05, 36, "Healthy", ""),
    ("Brandin Podziemski", "GSW", "G", 10.0, 5.0, 4.0, 0.8, 0.2, 1.2, 28.0, 64, 0.148, False, 0.95, 22, "Healthy", ""),
    ("Kevon Looney", "GSW", "C", 5.5, 7.0, 2.0, 0.5, 0.4, 0.0, 20.0, 60, 0.088, True, 0.95, 30, "Healthy", ""),
    ("Trayce Jackson-Davis", "GSW", "C", 6.5, 4.5, 1.0, 0.3, 0.7, 0.0, 14.0, 52, 0.098, False, 0.95, 25, "Healthy", ""),

    # === DET Pistons (1-seed East, 53-20) ===
    ("Cade Cunningham", "DET", "G", 24.5, 5.6, 9.9, 1.5, 0.9, 2.0, 34.4, 61, 0.305, False, 1.05, 24, "Questionable", "Collapsed lung - expected back for playoffs"),
    ("Jaden Ivey", "DET", "G", 17.5, 4.0, 4.8, 0.8, 0.3, 2.0, 31.0, 68, 0.225, False, 1.05, 23, "Healthy", ""),
    ("Jalen Duren", "DET", "C", 19.5, 10.6, 1.8, 0.9, 0.9, 0.0, 28.0, 63, 0.198, False, 0.95, 21, "Healthy", ""),
    ("Ausar Thompson", "DET", "F", 12.0, 6.5, 2.5, 1.5, 0.5, 0.5, 28.0, 55, 0.165, False, 0.95, 21, "Healthy", ""),
    ("Tobias Harris", "DET", "F", 11.5, 5.0, 2.5, 0.6, 0.3, 1.2, 26.0, 60, 0.155, True, 0.95, 33, "Healthy", ""),
    ("Tim Hardaway Jr.", "DET", "G", 11.0, 2.5, 2.0, 0.5, 0.2, 2.2, 24.0, 58, 0.158, True, 0.95, 34, "Healthy", ""),
    ("Malik Beasley", "DET", "G", 10.0, 2.0, 1.5, 0.5, 0.2, 2.5, 22.0, 62, 0.148, True, 0.95, 29, "Healthy", ""),
    ("Ron Holland", "DET", "F", 8.0, 3.5, 1.5, 0.6, 0.3, 0.5, 18.0, 50, 0.118, False, 0.95, 19, "Healthy", ""),

    # === BOS Celtics (2-seed East) ===
    ("Jayson Tatum", "BOS", "F", 27.4, 8.9, 5.2, 1.0, 0.6, 2.5, 36.1, 68, 0.298, True, 1.10, 28, "Healthy", ""),
    ("Jaylen Brown", "BOS", "G", 23.5, 5.5, 3.8, 1.0, 0.4, 2.0, 33.5, 65, 0.268, True, 1.05, 29, "Healthy", ""),
    ("Derrick White", "BOS", "G", 17.1, 4.5, 5.5, 1.2, 1.4, 2.8, 34.3, 70, 0.198, True, 1.02, 31, "Healthy", ""),
    ("Jrue Holiday", "BOS", "G", 13.5, 5.0, 4.5, 1.0, 0.5, 1.5, 30.0, 62, 0.175, True, 1.02, 35, "Healthy", ""),
    ("Al Horford", "BOS", "C", 7.5, 5.0, 2.5, 0.5, 0.8, 1.0, 22.0, 55, 0.108, True, 1.00, 39, "Healthy", ""),
    ("Payton Pritchard", "BOS", "G", 11.0, 2.5, 3.0, 0.6, 0.2, 2.8, 22.0, 68, 0.155, True, 0.98, 28, "Healthy", ""),
    ("Sam Hauser", "BOS", "F", 8.5, 2.5, 1.0, 0.4, 0.2, 2.2, 18.0, 58, 0.118, True, 0.95, 27, "Healthy", ""),

    # === NYK Knicks (3-seed East) ===
    ("Jalen Brunson", "NYK", "G", 26.2, 3.4, 6.7, 0.8, 0.1, 2.7, 35.0, 68, 0.318, True, 1.08, 29, "Healthy", ""),
    ("Karl-Anthony Towns", "NYK", "C", 20.1, 11.9, 2.8, 0.9, 0.6, 1.6, 30.9, 69, 0.265, True, 1.02, 30, "Healthy", ""),
    ("Mikal Bridges", "NYK", "F", 14.7, 4.0, 3.9, 1.3, 0.8, 2.0, 33.4, 74, 0.208, True, 0.98, 29, "Healthy", ""),
    ("OG Anunoby", "NYK", "F", 16.8, 5.2, 2.2, 1.6, 0.7, 2.3, 33.2, 60, 0.178, True, 0.98, 28, "Healthy", ""),
    ("Josh Hart", "NYK", "G", 10.0, 8.5, 4.0, 0.8, 0.3, 1.0, 30.0, 68, 0.138, True, 1.02, 30, "Healthy", ""),
    ("Donte DiVincenzo", "NYK", "G", 11.0, 3.0, 3.0, 0.8, 0.2, 2.5, 24.0, 60, 0.158, True, 0.98, 28, "Healthy", ""),
    ("Mitchell Robinson", "NYK", "C", 6.5, 8.5, 0.8, 0.4, 1.0, 0.0, 22.0, 42, 0.095, True, 0.95, 27, "Questionable", "Ankle"),
    ("Miles McBride", "NYK", "G", 8.0, 2.0, 2.5, 0.6, 0.2, 1.2, 18.0, 55, 0.118, False, 0.95, 25, "Healthy", ""),

    # === CLE Cavaliers (4-seed East) ===
    ("Donovan Mitchell", "CLE", "G", 27.9, 4.5, 5.8, 1.5, 0.3, 3.3, 33.5, 65, 0.278, True, 1.06, 29, "Healthy", ""),
    ("James Harden", "CLE", "G", 24.0, 5.0, 8.1, 1.1, 0.4, 3.1, 35.0, 64, 0.275, True, 1.02, 36, "Healthy", ""),
    ("Evan Mobley", "CLE", "F", 18.2, 8.9, 3.6, 0.8, 1.8, 1.0, 32.3, 59, 0.228, True, 1.05, 24, "Healthy", ""),
    ("Jarrett Allen", "CLE", "C", 13.8, 10.0, 1.5, 0.5, 1.0, 0.1, 30.0, 66, 0.158, True, 0.95, 28, "Healthy", ""),
    ("Max Strus", "CLE", "G", 11.0, 3.0, 2.5, 0.6, 0.3, 2.5, 26.0, 62, 0.155, True, 0.95, 28, "Healthy", ""),
    ("Dennis Schroder", "CLE", "G", 10.0, 2.5, 4.5, 0.8, 0.2, 1.0, 22.0, 58, 0.148, True, 0.95, 32, "Healthy", ""),
    ("Sam Merrill", "CLE", "G", 9.5, 2.0, 2.0, 0.5, 0.2, 2.5, 20.0, 55, 0.138, False, 0.95, 28, "Healthy", ""),
    ("Dean Wade", "CLE", "F", 7.0, 3.5, 1.5, 0.5, 0.3, 1.5, 18.0, 55, 0.105, True, 0.95, 28, "Healthy", ""),

    # === ATL Hawks (5-seed East) ===
    # Trae Young traded to WAS. Got Kuminga + Hield from GSW. Got NAW. Lost Porzingis to GSW.
    ("Jalen Johnson", "ATL", "F", 22.9, 10.3, 8.1, 1.3, 0.5, 1.7, 35.4, 65, 0.258, False, 1.05, 23, "Healthy", ""),
    ("Nickeil Alexander-Walker", "ATL", "G", 20.4, 3.4, 3.7, 1.3, 0.5, 3.1, 33.2, 71, 0.215, False, 0.95, 27, "Healthy", ""),
    ("Onyeka Okongwu", "ATL", "C", 15.3, 7.6, 3.2, 1.1, 1.1, 2.0, 31.0, 68, 0.178, False, 0.95, 24, "Healthy", ""),
    ("Jonathan Kuminga", "ATL", "F", 16.0, 5.5, 2.5, 0.7, 0.5, 1.0, 28.0, 60, 0.205, False, 0.95, 22, "Healthy", ""),
    ("De'Andre Hunter", "ATL", "F", 14.5, 4.0, 1.8, 0.7, 0.3, 1.5, 28.0, 55, 0.185, True, 0.95, 27, "Healthy", ""),
    ("Buddy Hield", "ATL", "G", 12.5, 2.5, 2.0, 0.5, 0.2, 3.0, 24.0, 62, 0.175, True, 0.95, 33, "Healthy", ""),
    ("Dyson Daniels", "ATL", "G", 10.5, 4.0, 3.5, 1.5, 0.3, 0.8, 28.0, 62, 0.148, False, 0.95, 22, "Healthy", ""),
    ("Clint Capela", "ATL", "C", 9.5, 9.0, 1.0, 0.5, 0.8, 0.0, 24.0, 60, 0.128, True, 0.95, 32, "Healthy", ""),
    ("Zaccharie Risacher", "ATL", "F", 10.0, 4.0, 1.5, 0.6, 0.4, 1.2, 24.0, 60, 0.148, False, 0.95, 20, "Healthy", ""),

    # === TOR Raptors (6-seed East) ===
    ("Scottie Barnes", "TOR", "F", 18.5, 7.8, 5.5, 1.4, 1.5, 0.9, 33.9, 70, 0.258, True, 1.03, 24, "Healthy", ""),
    ("RJ Barrett", "TOR", "F", 19.5, 5.5, 4.0, 0.7, 0.3, 1.5, 33.5, 64, 0.245, True, 0.98, 25, "Healthy", ""),
    ("Immanuel Quickley", "TOR", "G", 16.9, 4.1, 6.0, 1.3, 0.1, 2.6, 32.4, 67, 0.215, False, 0.95, 26, "Healthy", ""),
    ("Jakob Poeltl", "TOR", "C", 11.5, 8.5, 2.0, 0.5, 0.8, 0.0, 26.0, 65, 0.155, True, 0.95, 30, "Healthy", ""),
    ("Gradey Dick", "TOR", "G", 13.0, 3.0, 2.0, 0.5, 0.2, 2.5, 26.0, 64, 0.178, False, 0.95, 21, "Healthy", ""),
    ("Bruce Brown", "TOR", "G", 8.5, 4.0, 3.0, 0.7, 0.3, 0.8, 22.0, 55, 0.128, True, 0.98, 28, "Healthy", ""),

    # === PHI 76ers (7-seed East, play-in) ===
    ("Tyrese Maxey", "PHI", "G", 29.0, 4.1, 6.7, 2.0, 0.8, 3.3, 38.3, 61, 0.295, True, 1.03, 25, "Healthy", ""),
    ("Joel Embiid", "PHI", "C", 26.9, 7.5, 4.0, 0.6, 1.1, 1.3, 31.1, 34, 0.365, True, 1.08, 32, "Doubtful", "Knee management - limited availability"),
    ("Paul George", "PHI", "F", 16.4, 5.2, 3.7, 1.6, 0.5, 2.6, 30.4, 28, 0.235, True, 1.02, 35, "Healthy", ""),
    ("Caleb Martin", "PHI", "F", 10.0, 4.5, 2.0, 0.7, 0.3, 1.2, 26.0, 60, 0.148, True, 0.95, 30, "Healthy", ""),
    ("Kelly Oubre Jr.", "PHI", "G", 13.0, 4.0, 1.5, 0.8, 0.3, 1.5, 28.0, 58, 0.178, True, 0.95, 29, "Healthy", ""),
    ("Kyle Lowry", "PHI", "G", 7.5, 3.0, 4.5, 0.8, 0.2, 1.0, 22.0, 50, 0.115, True, 0.95, 40, "Healthy", ""),

    # === ORL Magic (8-seed East, play-in) ===
    # Got Desmond Bane from MEM for Cole Anthony + KCP + picks
    ("Paolo Banchero", "ORL", "F", 23.0, 7.0, 4.5, 0.8, 0.5, 1.2, 34.0, 55, 0.275, True, 1.03, 23, "Healthy", ""),
    ("Franz Wagner", "ORL", "F", 21.5, 5.5, 5.0, 1.0, 0.4, 1.8, 33.5, 60, 0.248, True, 1.02, 24, "Healthy", ""),
    ("Desmond Bane", "ORL", "G", 20.4, 4.2, 4.2, 1.0, 0.4, 2.0, 34.2, 73, 0.228, True, 0.98, 27, "Healthy", ""),
    ("Jalen Suggs", "ORL", "G", 14.0, 3.5, 4.5, 1.0, 0.3, 1.5, 30.0, 65, 0.188, True, 0.95, 24, "Healthy", ""),
    ("Wendell Carter Jr.", "ORL", "C", 10.5, 7.5, 2.5, 0.5, 0.5, 0.5, 26.0, 50, 0.148, True, 0.95, 26, "Questionable", "Plantar fascia"),
    ("Jonathan Isaac", "ORL", "F", 7.0, 4.5, 1.0, 0.7, 1.0, 0.5, 18.0, 42, 0.108, True, 0.95, 28, "Healthy", ""),

    # === CHA Hornets (9-seed East, play-in) ===
    ("LaMelo Ball", "CHA", "G", 19.7, 4.8, 7.1, 1.2, 0.2, 3.7, 27.6, 63, 0.285, False, 1.05, 24, "Healthy", ""),
    ("Brandon Miller", "CHA", "F", 18.5, 5.0, 2.8, 0.7, 0.4, 2.5, 32.0, 66, 0.228, False, 0.95, 22, "Healthy", ""),
    ("Miles Bridges", "CHA", "F", 17.0, 6.5, 3.0, 0.7, 0.4, 1.5, 32.0, 65, 0.218, False, 0.95, 28, "Healthy", ""),
    ("Kon Knueppel", "CHA", "F", 19.1, 5.3, 3.5, 0.7, 0.2, 3.5, 31.5, 72, 0.208, False, 0.95, 20, "Healthy", ""),
    ("Nick Richards", "CHA", "C", 8.5, 6.0, 0.8, 0.3, 0.8, 0.0, 18.0, 52, 0.128, False, 0.95, 27, "Healthy", ""),
    ("Tre Mann", "CHA", "G", 11.0, 2.5, 3.5, 0.6, 0.2, 1.8, 22.0, 60, 0.158, False, 0.95, 24, "Healthy", ""),

    # === MIA Heat (10-seed East, play-in) ===
    ("Bam Adebayo", "MIA", "C", 20.2, 9.9, 3.0, 1.2, 0.7, 1.7, 32.1, 65, 0.238, True, 1.05, 28, "Healthy", ""),
    ("Tyler Herro", "MIA", "G", 20.9, 4.8, 3.9, 0.8, 0.3, 2.5, 30.9, 27, 0.268, True, 0.98, 26, "Healthy", ""),
    ("Andrew Wiggins", "MIA", "F", 15.0, 4.8, 2.2, 0.7, 0.4, 1.5, 29.5, 60, 0.195, True, 0.98, 30, "Healthy", ""),
    ("Terry Rozier", "MIA", "G", 15.5, 3.5, 4.0, 0.8, 0.3, 2.0, 30.0, 58, 0.208, True, 0.98, 32, "Healthy", ""),
    ("Kyle Anderson", "MIA", "F", 8.0, 4.5, 3.5, 0.8, 0.4, 0.5, 22.0, 55, 0.128, True, 0.95, 32, "Healthy", ""),
    ("Jaime Jaquez Jr.", "MIA", "F", 12.5, 4.5, 2.5, 0.6, 0.3, 1.0, 28.0, 65, 0.175, False, 0.95, 24, "Healthy", ""),
    ("Nikola Jovic", "MIA", "F", 9.5, 4.0, 2.0, 0.4, 0.3, 1.2, 20.0, 55, 0.138, False, 0.95, 22, "Healthy", ""),
]

# Build player data
player_data = []
for i, (name, team, pos, pts, reb, ast, stl, blk, threes, mins, gp, usg, has_hist, adj, player_age, inj_status, inj_note) in enumerate(PLAYERS):
    ti = team_info[team]
    fantasy_avg = pts + reb + ast
    exp_games = ti["exp_games"]
    af = age_factor(player_age)
    projected = fantasy_avg * adj * af * exp_games

    player_data.append({
        "id": 200000 + i,
        "name": name,
        "team": team,
        "position": pos,
        "conference": ti["conf"],
        "seed": ti["seed"],
        "pts": pts, "reb": reb, "ast": ast,
        "stl": stl, "blk": blk, "threes": threes,
        "min": mins,
        "games_played": gp,
        "usg_pct": usg,
        "fantasy_avg": round(fantasy_avg, 1),
        "adj": round(adj * af, 3),
        "has_playoff_history": has_hist,
        "adj_details": {
            "method": "player_specific" if has_hist else "archetype",
            "playoff_games": 50 if has_hist else 0,
            "reg_fantasy": round(fantasy_avg * 0.95, 1) if has_hist else None,
            "playoff_fantasy": round(fantasy_avg * adj * 0.95, 1) if has_hist else None,
            "min_diff": round((adj - 1.0) * 10, 1) if has_hist else None,
            "age": player_age,
            "age_factor": af,
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

print(f"\nTop 25:")
for p in player_data[:25]:
    age = p["adj_details"]["age"]
    af = p["adj_details"]["age_factor"]
    print(f"  {p['rank']:3}. {p['name']:30s} {p['team']} | Proj: {p['projected']:6.0f} | "
          f"Avg: {p['fantasy_avg']:5.1f} | Games: {p['expected_games']:5.1f} | Adj: {p['adj']:.2f} | "
          f"Age: {age} ({af:.2f}x) | {p['tier']}")

print(f"\nInjured players:")
for p in player_data:
    if p["injury_status"] != "Healthy":
        print(f"  {p['name']:30s} {p['team']} | {p['injury_status']}: {p['injury_note']}")

print(f"\nAge adjustment examples:")
for name in ["Luka Doncic", "LeBron James", "Stephen Curry", "Victor Wembanyama", "Shai Gilgeous-Alexander", "Jalen Johnson", "Kevin Durant"]:
    p = next((x for x in player_data if x["name"] == name), None)
    if p:
        age = p["adj_details"]["age"]
        af = p["adj_details"]["age_factor"]
        print(f"  {name:30s} Age {age} -> {af:.2f}x | Proj: {p['projected']:.0f}")
