import os
import requests
import re

# Base directory for all team folders
BASE_OUTPUT_DIR = "/Users/kamahl/Sports/scripts/espn/nba/team_roster/nba_team_rosters/nba_teams"

# Ensure the base directory exists
os.makedirs(BASE_OUTPUT_DIR, exist_ok=True)

def generate_team_script(team_id):
    # Fetch team details to get the team name
    url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams/{team_id}/roster"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch team {team_id}: {response.status_code}")
        return
    
    data = response.json()
    
    # Extract team info
    team_info = data.get("team", {})
    team_name = team_info.get("name", f"Team_{team_id}")
    team_display_name = team_info.get("displayName", "N/A")
    team_abbreviation = team_info.get("abbreviation", "N/A")
    
    # Sanitize team name for folder and filenames
    safe_team_name = re.sub(r'[^a-zA-Z0-9_-]', '_', team_name).lower()

    # Create a team-specific folder inside the base directory
    team_folder = os.path.join(BASE_OUTPUT_DIR, safe_team_name)
    os.makedirs(team_folder, exist_ok=True)

    # Define the script content for the team roster and player splits generation
    script_content = f"""import requests
import csv
import os
from bs4 import BeautifulSoup

# ESPN NBA team roster API endpoint
team_id = {team_id}
url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams/{{team_id}}/roster"

# Make the API request
response = requests.get(url)
data = response.json()

# Extract team information
team_info = data.get("team", {{}})
team_name = team_info.get("name", "N/A")
team_display_name = team_info.get("displayName", "N/A")
team_abbreviation = team_info.get("abbreviation", "N/A")

# Extract players from the roster
players = data.get("athletes", [])

# Print team details
print(f"NBA Team: {{team_display_name}} ({{team_abbreviation}})")
print("=" * 40)

# Create a list for CSV output
csv_data = [("ID", "Full Name", "Display Name")]

# Base directory for player data
BASE_DIR = "{BASE_OUTPUT_DIR}"

# Player splits script template
PLAYER_SCRIPT_TEMPLATE = '''import requests
import csv
import os
from bs4 import BeautifulSoup

player_id = "{{player_id}}"
player_name = "{{player_name}}"

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
    
    base_directory = "{BASE_OUTPUT_DIR}"
    player_folder = os.path.join(base_directory, "{safe_team_name}", "{{player_name.lower().replace(' ', '_')}}")
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

for player in players:
    player_id = player.get("id", "N/A")
    full_name = player.get("fullName", "N/A")
    display_name = player.get("displayName", "N/A")
    
    print(f"ID: {{player_id}}")
    print(f"Full Name: {{full_name}}")
    print(f"Display Name: {{display_name}}")
    print("-" * 40)
    
    csv_data.append((player_id, full_name, display_name))
    
    # Create player folder
    player_folder = os.path.join(BASE_DIR, "{safe_team_name}", full_name.lower().replace(" ", "_"))
    os.makedirs(player_folder, exist_ok=True)
    
    # Generate player splits script
    player_script = PLAYER_SCRIPT_TEMPLATE.format(
        player_id=player_id,
        player_name=full_name,
        BASE_OUTPUT_DIR=BASE_DIR,
        safe_team_name="{safe_team_name}"
    )
    player_script_path = os.path.join(player_folder, f"fetch_{{full_name.lower().replace(' ', '_')}}_splits.py")
    with open(player_script_path, "w", encoding="utf-8") as f:
        f.write(player_script)
    print(f"Created splits script: {{player_script_path}}")

# Save roster data to a CSV file inside the team folder
csv_filename = os.path.join(BASE_DIR, "{safe_team_name}", f"{{team_name.lower().replace(' ', '_')}}_roster.csv")
with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerows(csv_data)

print(f"CSV file saved: {{csv_filename}}")
"""

    # Define the script path inside the team folder
    script_filename = os.path.join(team_folder, f"{safe_team_name}_roster.py")

    # Write or update the script inside the team folder
    with open(script_filename, "w") as f:
        f.write(script_content.format(
            BASE_OUTPUT_DIR=BASE_OUTPUT_DIR,
            safe_team_name=safe_team_name
        ).strip())

    print(f"Script updated: {script_filename}")

# Generate a script for each team (IDs 1-30)
for team_id in range(1, 31):
    generate_team_script(team_id)