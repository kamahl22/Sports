# nba_roster_and_split_update.py
# This scripts updates each teams roster when it runs and a folder is created for each player
# Each player has a player script created for them as well

import requests
import csv
import os
from bs4 import BeautifulSoup

# Base directory with new nba_roster folder
BASE_DIR = "/Users/kamahl/Sports/scripts/espn/nba/team_roster/nba_team_rosters/nba_teams"
os.makedirs(BASE_DIR, exist_ok=True)

def fetch_team_rosters():
    """Fetch updated rosters for all NBA teams using team IDs."""
    team_rosters = {}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }
    
    for team_id in range(1, 31):  # NBA team IDs range from 1 to 30
        url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams/{team_id}/roster"
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to fetch roster for team ID {team_id}: {response.status_code}")
            continue
        
        data = response.json()
        team_info = data.get("team", {})
        # Combine city and name for full team name (e.g., "boston-celtics")
        team_city = team_info.get("location", "").lower().replace(" ", "-")
        team_name = team_info.get("name", "").lower().replace(" ", "-")
        full_team_name = f"{team_city}-{team_name}"
        
        team_folder = os.path.join(BASE_DIR, full_team_name)
        os.makedirs(team_folder, exist_ok=True)
        
        players = data.get("athletes", [])
        player_list = []
        for player in players:
            player_id = player.get("id", "N/A")
            player_name = player.get("fullName", "N/A")
            if player_id != "N/A" and player_name != "N/A":
                player_list.append({"name": player_name, "id": player_id})
        
        team_rosters[full_team_name] = player_list
        print(f"Fetched roster for {full_team_name}: {len(player_list)} players")
        
        # Save roster to CSV
        roster_csv = os.path.join(team_folder, f"{full_team_name}_roster.csv")
        with open(roster_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Player Name", "Player ID"])
            writer.writerows([[p["name"], p["id"]] for p in player_list])
    
    return team_rosters

def create_player_folders_and_scripts(team_rosters):
    """Create folders and scripts for each player."""
    script_template = '''import requests
import csv
import os
from bs4 import BeautifulSoup

player_id = "{player_id}"
player_name = "{player_name}"

def fetch_and_save_data():
    url = f"https://www.espn.com/nba/player/splits/_/id/{{player_id}}/{{player_name.lower().replace(' ', '-')}}"
    
    headers = {{
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }}
    response = requests.get(url, headers=headers)
    
    print(f"Status Code: {{response.status_code}}")
    if response.status_code != 200:
        print(f"Error: Unable to fetch data for {{player_name}} (ID: {{player_id}}) - Status Code {{response.status_code}}")
        return None, None
    
    soup = BeautifulSoup(response.text, "html.parser")
    tables = soup.find_all("table")
    print(f"Number of tables found: {{len(tables)}}")
    
    if not tables:
        print(f"No stats tables found for {{player_name}}. The page structure may have changed.")
        return None, None
    
    expected_headers = ["SPLIT", "GP", "MIN", "FG", "FG%", "3PT", "3P%", "FT", "FT%", "OR", "DR", "REB", "AST", "BLK", "STL", "PF", "TO", "PTS"]
    
    preset_splits = [
        "All Splits", "Home", "Road", "vs. Division", "vs. Conference", "3+ Days Rest",
        "October", "November", "December", "January", "February", "March",
        "Pre All-Star", "Post All-Star", "Wins", "Losses",
        "As Starter", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday",
        "vs ATL", "vs BOS", "vs CHA", "vs CHI", "vs CLE", "vs DAL", "vs DEN", "vs DET", "vs GS", "vs HOU",
        "vs LAC", "vs LAL", "vs MEM", "vs MIA", "vs MIL", "vs NO", "vs NY", "vs ORL", "vs PHI", "vs PHO",
        "vs POR", "vs SA", "vs SAC", "vs OKC", "vs TOR", "vs UTA", "vs WAS"
    ]
    
    default_stats = ["0", "0.0", "0.0-0.0", "0.0", "0.0-0.0", "0.0", "0.0-0.0", "0.0", "0.0", "0.0", "0.0", "0.0", "0.0", "0.0", "0.0", "0.0", "0.0"]
    player_data_dict = {{split: default_stats.copy() for split in preset_splits}}
    
    all_rows = []
    for table in tables:
        all_rows.extend(table.find_all("tr")[1:])
    
    splits = []
    stats_rows = []
    for i, row in enumerate(all_rows):
        columns = row.find_all("td")
        row_data = [col.text.strip() for col in columns if col.text.strip()]
        if not row_data:
            continue
        if len(row_data) == 1 and row_data[0] in preset_splits:
            splits.append(row_data[0])
            print(f"Split found ({{len(splits)-1}}): ['{{row_data[0]}}']")
        elif len(row_data) > 1 and row_data[0].isdigit():
            stats_rows.append(row_data)
            print(f"Stats found ({{len(stats_rows)-1}}): {{row_data}}")
        else:
            print(f"Subheader: {{row_data}}")
        print()
    
    for idx, split in enumerate(splits):
        if idx < len(stats_rows):
            stats = stats_rows[idx][:len(expected_headers)-1] + ["N/A" for _ in range(len(stats_rows[idx]), len(expected_headers)-1)] if len(stats_rows[idx]) < len(expected_headers)-1 else stats_rows[idx][:len(expected_headers)-1]
            player_data_dict[split] = stats
            print(f"Paired: ['{{split}}'] with {{stats}}")
            print()
    
    player_data = [[split] + player_data_dict[split] for split in preset_splits]
    
    if not player_data:
        print(f"No player splits data found for {{player_name}}.")
        return None, None
    
    base_directory = "{base_dir}"
    player_folder = os.path.join(base_directory, "{team}", "{player_name_dir}")
    os.makedirs(player_folder, exist_ok=True)
    
    csv_filename = os.path.join(player_folder, f"{{player_name.lower().replace(' ', '_')}}_splits.csv")
    with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(expected_headers)
        writer.writerows(player_data)
    
    print(f"CSV file saved: {{csv_filename}}")
    return expected_headers, player_data

def print_excel_style():
    headers, data = fetch_and_save_data()
    if not headers or not data:
        print("No headers or data to display.")
        return
    
    max_cols = len(headers)
    col_widths = [len(str(h)) for h in headers]
    
    for row in data:
        padded_row = row + [""] * (max_cols - len(row)) if len(row) < max_cols else row[:max_cols]
        for i, cell in enumerate(padded_row):
            col_widths[i] = max(col_widths[i], len(str(cell)))
    
    top_border = "┌" + "─".join("─" * (w + 2) for w in col_widths) + "┐"
    bottom_border = "└" + "─".join("─" * (w + 2) for w in col_widths) + "┘"
    separator = "├" + "─".join("─" * (w + 2) for w in col_widths) + "┤"
    
    print(top_border)
    header_row = "│ " + " │ ".join(h.center(w) for h, w in zip(headers, col_widths)) + " │"
    print(header_row)
    print(separator)
    
    for row in data:
        padded_row = row + [""] * (max_cols - len(row)) if len(row) < max_cols else row[:max_cols]
        data_row = "│ " + " │ ".join(str(cell).ljust(w) for cell, w in zip(padded_row, col_widths)) + " │"
        print(data_row)
    
    print(bottom_border)

if __name__ == "__main__":
    print_excel_style()
'''

    for team, players in team_rosters.items():
        team_folder = os.path.join(BASE_DIR, team)
        for player in players:
            player_name = player["name"]
            player_id = player["id"]
            player_name_dir = player_name.lower().replace(" ", "_")
            player_folder = os.path.join(team_folder, player_name_dir)
            os.makedirs(player_folder, exist_ok=True)
            
            # Generate script
            script_content = script_template.format(
                player_id=player_id,
                player_name=player_name,
                base_dir=BASE_DIR,
                team=team,
                player_name_dir=player_name_dir
            )
            script_path = os.path.join(player_folder, f"{player_name_dir}_splits.py")
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(script_content)
            print(f"Created script: {script_path}")

def main():
    print("Updating NBA team rosters...")
    team_rosters = fetch_team_rosters()
    if not team_rosters:
        print("No rosters found. Exiting.")
        return
    print("Creating player folders and scripts...")
    create_player_folders_and_scripts(team_rosters)
    print("Done!")

if __name__ == "__main__":
    main()