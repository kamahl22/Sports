# find_monday_top_scorer.py
import os
import csv
from datetime import datetime
import pandas as pd

# Base directories
GAME_LOG_DIR = "/Users/kamahl/Sports/scripts_espn/nba/team_roster/nba_team_rosters/nba_teams"
TEAM_STATS_DIR = "/Users/kamahl/Sports/scripts/nba/teamrankings/team_stats/team_overall_stats"

# Mapping of opponent abbreviations to team names (for TeamRankings URLs)
OPP_TO_TEAM = {
    "ATL": "atlanta-hawks", "BOS": "boston-celtics", "BKN": "brooklyn-nets", "CHA": "charlotte-hornets",
    "CHI": "chicago-bulls", "CLE": "cleveland-cavaliers", "DAL": "dallas-mavericks", "DEN": "denver-nuggets",
    "DET": "detroit-pistons", "GSW": "golden-state-warriors", "HOU": "houston-rockets", "IND": "indiana-pacers",
    "LAC": "los-angeles-clippers", "LAL": "los-angeles-lakers", "MEM": "memphis-grizzlies", "MIA": "miami-heat",
    "MIL": "milwaukee-bucks", "MIN": "minnesota-timberwolves", "NOP": "new-orleans-pelicans", "NYK": "new-york-knicks",
    "OKC": "oklahoma-city-thunder", "ORL": "orlando-magic", "PHI": "philadelphia-76ers", "PHX": "phoenix-suns",
    "POR": "portland-trail-blazers", "SAC": "sacramento-kings", "SAS": "san-antonio-spurs", "TOR": "toronto-raptors",
    "UTA": "utah-jazz", "WAS": "washington-wizards"
}

def get_day_of_week(date_str):
    """Convert a date string (e.g., 'Mon 3/9') to the day of the week."""
    day_mapping = {
        "Mon": "Monday", "Tue": "Tuesday", "Wed": "Wednesday",
        "Thu": "Thursday", "Fri": "Friday", "Sat": "Saturday", "Sun": "Sunday"
    }
    
    parts = date_str.split()
    if len(parts) < 2:
        return None
    
    day_name = parts[0]
    date_part = parts[1]
    
    month, day = map(int, date_part.split("/"))
    year = 2024 if month >= 10 else 2025
    try:
        date_obj = datetime(year, month, day)
        return date_obj.strftime("%A")
    except ValueError:
        return None

def get_opponent_defensive_stats(opponent_abbr):
    """Fetch the opponent's defensive stats (e.g., Opp Points/Game)."""
    opponent = opponent_abbr.replace("@", "").replace("vs", "").strip()
    if opponent not in OPP_TO_TEAM:
        print(f"Opponent abbreviation {opponent} not found in mapping.")
        return None
    
    team_name = OPP_TO_TEAM[opponent]
    stats_file = os.path.join(TEAM_STATS_DIR, team_name, f"{team_name}_stats.csv")
    if not os.path.exists(stats_file):
        print(f"Stats file not found for {team_name} at {stats_file}")
        return None
    
    df = pd.read_csv(stats_file)
    opp_points_game = df[
        (df["Category"] == "Overall Statistics") & (df["MIN Defense"] == "Opp Points/Game")
    ]["Value (rank)"].values
    return opp_points_game[0] if len(opp_points_game) > 0 else None

def format_game_details(headers, row):
    """Format game details with labels."""
    details = {}
    for header, value in zip(headers, row):
        if value.strip():  # Only include non-empty values
            if header == "DATE":
                details[header] = f"{value}"
            elif header == "OPP":
                details[header] = f"{value}"
            elif header == "RESULT":
                details[header] = f"{value}"
            elif header == "MIN":
                details[header] = f"MIN: {value}"
            elif header == "FGM-FGA":
                details[header] = f"FGM-FGA: {value}"
            elif header == "FG%":
                details[header] = f"FG%: {value}"
            elif header == "3PM-3PA":
                details[header] = f"3PM-3PA: {value}"
            elif header == "3P%":
                details[header] = f"3P%: {value}"
            elif header == "FTM-FTA":
                details[header] = f"FTM-FTA: {value}"
            elif header == "FT%":
                details[header] = f"FT%: {value}"
            elif header == "REB":
                details[header] = f"REB: {value}"
            elif header == "AST":
                details[header] = f"AST: {value}"
            elif header == "STL":
                details[header] = f"STL: {value}"
            elif header == "BLK":
                details[header] = f"BLK: {value}"
            elif header == "TO":
                details[header] = f"TO: {value}"
            elif header == "PF":
                details[header] = f"PF: {value}"
            elif header == "PTS":
                details[header] = f"PTS: {value}"
    
    return "\n".join(details.values())

def find_monday_top_scorer():
    """Find the player who scored the most points on a Monday and include opponent defensive stats."""
    top_scorer = None
    max_points = -1
    top_game = None
    opponent_defense = None
    
    for team_folder in os.listdir(GAME_LOG_DIR):
        team_path = os.path.join(GAME_LOG_DIR, team_folder)
        if not os.path.isdir(team_path):
            continue
        
        for player_folder in os.listdir(team_path):
            player_path = os.path.join(team_path, player_folder)
            if not os.path.isdir(player_path):
                continue
            
            game_log_csv = os.path.join(player_path, f"{player_folder}_gamelog.csv")
            if not os.path.exists(game_log_csv):
                continue
            
            player_name = player_folder.replace("_", " ").title()
            print(f"Checking game log for {player_name}...")
            
            with open(game_log_csv, mode="r", encoding="utf-8") as f:
                reader = csv.reader(f)
                headers = next(reader)  # Skip header
                date_idx = headers.index("DATE")
                opp_idx = headers.index("OPP")
                pts_idx = headers.index("PTS")
                
                for row in reader:
                    if len(row) <= max(date_idx, opp_idx, pts_idx):
                        continue
                    
                    date_str = row[date_idx]
                    day_of_week = get_day_of_week(date_str)
                    if day_of_week != "Monday":
                        continue
                    
                    try:
                        points = int(row[pts_idx])
                        if points > max_points:
                            max_points = points
                            top_scorer = player_name
                            top_game = row
                            # Get opponent defensive stats
                            opponent_abbr = row[opp_idx]
                            opponent_defense = get_opponent_defensive_stats(opponent_abbr)
                    except (ValueError, IndexError):
                        continue
    
    if top_scorer:
        print(f"\nTop Monday Scorer: {top_scorer}")
        print(f"Points: {max_points}")
        print(f"Game Details:\n{format_game_details(headers, top_game)}")
        if opponent_defense:
            print(f"Opponent Defensive Points Allowed: {opponent_defense}")
        else:
            print("Opponent defensive stats not available.")
    else:
        print("No Monday games found with valid points data.")

if __name__ == "__main__":
    find_monday_top_scorer()