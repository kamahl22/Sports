# predict_player_points_with_team_stats.py
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import os
from datetime import datetime

# Base directories
GAME_LOG_DIR = "/Users/kamahl/Sports/scripts_espn/nba/team_roster/nba_team_rosters/nba_teams"
TEAM_STATS_DIR = "/Users/kamahl/Sports/scripts/nba/teamrankings/team_stats/team_overall_stats"

# Opponent abbreviation to team name mapping
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

def load_player_data(player_name, team):
    """Load a player's game log data."""
    player_folder = player_name.lower().replace(" ", "_")
    game_log_csv = os.path.join(GAME_LOG_DIR, team, player_folder, f"{player_folder}_gamelog.csv")
    if not os.path.exists(game_log_csv):
        print(f"Game log not found for {player_name}")
        return None
    
    df = pd.read_csv(game_log_csv)
    return df

def get_team_stat(team_name, category, stat_name):
    """Fetch a specific stat for a team (e.g., Opp Points/Game)."""
    stats_file = os.path.join(TEAM_STATS_DIR, team_name, f"{team_name}_stats.csv")
    if not os.path.exists(stats_file):
        return None
    
    df = pd.read_csv(stats_file)
    value = df[
        (df["Category"] == category) & (df["MIN Defense"] == stat_name)
    ]["Value (rank)"].values
    if len(value) == 0:
        return None
    
    # Extract numeric value (e.g., "109.2 (#6)" -> 109.2)
    try:
        return float(value[0].split()[0])
    except (ValueError, IndexError):
        return None

def get_day_of_week(date_str):
    """Convert a date string to the day of the week."""
    day_mapping = {
        "Mon": "Monday", "Tue": "Tuesday", "Wed": "Wednesday",
        "Thu": "Thursday", "Fri": "Friday", "Sat": "Saturday", "Sun": "Sunday"
    }
    parts = date_str.split()
    if len(parts) < 2:
        return None
    day_name = parts[0]
    return day_mapping.get(day_name)

def prepare_features(df):
    """Prepare features for prediction."""
    df['PTS'] = pd.to_numeric(df['PTS'], errors='coerce')
    df = df.dropna(subset=['PTS'])
    
    # Feature: Average points in last 5 games
    df['Avg_PTS_Last_5'] = df['PTS'].rolling(window=5, min_periods=1).mean().shift(1)
    
    # Feature: Day of week (encoded as numbers)
    df['Day_of_Week'] = df['DATE'].apply(lambda x: get_day_of_week(x))
    df['Day_of_Week'] = df['Day_of_Week'].map({
        "Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3,
        "Friday": 4, "Saturday": 5, "Sunday": 6
    })
    
    # Feature: Home/Away (1 for home, 0 for away)
    df['Home_Away'] = df['OPP'].apply(lambda x: 1 if 'vs' in x else 0)
    
    # Feature: Opponent defensive points allowed
    df['Opp_Def_Pts_Allowed'] = df['OPP'].apply(
        lambda x: get_team_stat(OPP_TO_TEAM.get(x.replace("@", "").replace("vs", "").strip(), ""), 
                               "Overall Statistics", "Opp Points/Game")
    )
    
    return df

def predict_points(player_name, team, next_opponent, next_day_of_week, is_home_game):
    """Predict points for a player's next game."""
    df = load_player_data(player_name, team)
    if df is None:
        return None, None
    
    df = prepare_features(df)
    
    # Drop rows with missing features
    df = df.dropna(subset=['Avg_PTS_Last_5', 'Day_of_Week', 'Home_Away', 'Opp_Def_Pts_Allowed'])
    if df.empty:
        print(f"Insufficient data for {player_name} after feature preparation.")
        return None, None
    
    # Features and target
    X = df[['Avg_PTS_Last_5', 'Day_of_Week', 'Home_Away', 'Opp_Def_Pts_Allowed']]
    y = df['PTS']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train model
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    
    # Prepare features for the next game
    last_game = X.iloc[-1:].copy()
    next_features = {
        'Avg_PTS_Last_5': df['Avg_PTS_Last_5'].iloc[-1],
        'Day_of_Week': next_day_of_week,
        'Home_Away': 1 if is_home_game else 0,
        'Opp_Def_Pts_Allowed': get_team_stat(OPP_TO_TEAM.get(next_opponent, ""), 
                                             "Overall Statistics", "Opp Points/Game")
    }
    if next_features['Opp_Def_Pts_Allowed'] is None:
        print(f"Opponent defensive stats not available for {next_opponent}.")
        return None, None
    
    next_game_df = pd.DataFrame([next_features])
    predicted_points = model.predict(next_game_df)[0]
    return predicted_points, mae

def predict_for_upcoming_games(upcoming_games):
    """Predict points for all players in upcoming games."""
    predictions = []
    
    for team_folder in os.listdir(GAME_LOG_DIR):
        team_path = os.path.join(GAME_LOG_DIR, team_folder)
        if not os.path.isdir(team_path):
            continue
        
        for player_folder in os.listdir(team_path):
            player_path = os.path.join(team_path, player_folder)
            if not os.path.isdir(player_path):
                continue
            
            player_name = player_folder.replace("_", " ").title()
            # Check if the player's team is in the upcoming games
            game = next((g for g in upcoming_games if g['team'] == team_folder), None)
            if not game:
                continue
            
            predicted_points, mae = predict_points(
                player_name=player_name,
                team=team_folder,
                next_opponent=game['opponent'],
                next_day_of_week=game['day_of_week'],
                is_home_game=game['is_home']
            )
            
            if predicted_points is not None:
                predictions.append({
                    'Player': player_name,
                    'Team': team_folder.replace("-", " ").title(),
                    'Predicted Points': predicted_points,
                    'MAE': mae,
                    'Opponent': game['opponent'],
                    'Day': game['day_of_week']
                })
    
    # Sort predictions by predicted points
    predictions.sort(key=lambda x: x['Predicted Points'], reverse=True)
    
    # Print results
    print("\nPredictions for Upcoming Games:")
    print("=================================")
    for pred in predictions:
        print(f"Player: {pred['Player']} ({pred['Team']})")
        print(f"Predicted Points: {pred['Predicted Points']:.1f} (MAE: {pred['MAE']:.2f})")
        print(f"Opponent: {pred['Opponent']}, Day: {pred['Day']}")
        print("---------------------------------")

if __name__ == "__main__":
    # Example upcoming games (replace with actual schedule)
    upcoming_games = [
        {'team': 'minnesota-timberwolves', 'opponent': 'DEN', 'day_of_week': 0, 'is_home': True},  # Monday
        {'team': 'boston-celtics', 'opponent': 'LAL', 'day_of_week': 0, 'is_home': False},
        {'team': 'los-angeles-lakers', 'opponent': 'BOS', 'day_of_week': 0, 'is_home': True},
    ]
    predict_for_upcoming_games(upcoming_games)