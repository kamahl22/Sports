import os
import pandas as pd
import subprocess
import re
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
from nba_api.stats.static import players
from nba_api.stats.endpoints import commonallplayers

# Directory containing team roster CSVs
ROSTER_DIR = "/Users/kamahl/Sports/scripts/nba/teamrankings/players/roster/nba_teams"
ROSTER_GENERATOR_SCRIPT = "/Users/kamahl/Sports/scripts/nba/teamrankings/players/roster/team_rosters.py"

# Base directory for player stats output, organized by team
BASE_DIR = "/Users/kamahl/Sports/scripts/nba/teamrankings/players/player_stats/nba_teams"
os.makedirs(BASE_DIR, exist_ok=True)

# Cache files for trade and player ID data
TRADE_CACHE_FILE = os.path.join(BASE_DIR, "trade_cache.json")
PLAYER_ID_CACHE_FILE = os.path.join(BASE_DIR, "player_id_cache.json")

nba_teams = [
    "atlanta-hawks", "boston-celtics", "brooklyn-nets", "charlotte-hornets",
    "chicago-bulls", "cleveland-cavaliers", "dallas-mavericks", "denver-nuggets",
    "detroit-pistons", "golden-state-warriors", "houston-rockets", "indiana-pacers",
    "los-angeles-clippers", "los-angeles-lakers", "memphis-grizzlies", "miami-heat",
    "milwaukee-bucks", "minnesota-timberwolves", "new-orleans-pelicans", "new-york-knicks",
    "oklahoma-city-thunder", "orlando-magic", "philadelphia-76ers", "phoenix-suns",
    "portland-trail-blazers", "sacramento-kings", "san-antonio-spurs", "toronto-raptors",
    "utah-jazz", "washington-wizards"
]

def format_player_name(player_name):
    """Convert player name to URL-friendly format."""
    formatted_name = player_name.lower().replace(" ", "-").replace(".", "").replace("'", "")
    formatted_name = re.sub(r"[^a-zA-Z0-9-]", "", formatted_name)
    return formatted_name

def normalize_player_name(player_name):
    """Normalize player name by removing special characters and converting to lowercase."""
    normalized = player_name.lower().replace(".", "").replace("'", "")
    normalized = re.sub(r"[^a-zA-Z0-9\s-]", "", normalized)
    return normalized.strip()

def team_name_to_slug(team_name):
    """Convert team name to slug format (e.g., 'Los Angeles Lakers' -> 'los-angeles-lakers')."""
    return team_name.lower().replace(" ", "-")

def fetch_traded_players():
    """
    Scrape the NBA.com Trade Tracker to get a list of players traded in the 2024-2025 season.
    Returns a dictionary mapping player_folder to their most recent team.
    """
    url = "https://www.nba.com/news/2024-25-nba-trade-tracker"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }

    # Check if cache exists and is recent
    if os.path.exists(TRADE_CACHE_FILE):
        with open(TRADE_CACHE_FILE, "r") as f:
            cache_data = json.load(f)
        cache_time = datetime.fromisoformat(cache_data["timestamp"])
        current_time = datetime.now()
        # Use cache if it's less than 24 hours old
        if (current_time - cache_time).total_seconds() < 24 * 60 * 60:
            print("Using cached trade data.")
            return cache_data["traded_players"]

    print(f"Fetching trade data from {url}...")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to fetch trade data: {e}")
        return {}

    soup = BeautifulSoup(response.content, "html.parser")
    traded_players = {}

    trade_sections = soup.find_all("div", class_=re.compile("Article_content|TradeTracker"))

    for section in trade_sections:
        trade_items = section.find_all(["p", "li"])
        for item in trade_items:
            text = item.get_text(strip=True)
            if "receives:" in text.lower() or "to the" in text.lower():
                if "receives:" in text.lower():
                    parts = text.split("receives:")
                    if len(parts) < 2:
                        continue
                    team_part = parts[0].strip()
                    players_part = parts[1].strip()
                    team_match = re.search(r"(\w+\s*\w*)\s*receives", team_part, re.IGNORECASE)
                    if not team_match:
                        continue
                    team_name = team_match.group(1)
                    team_slug = team_name_to_slug(team_name)
                    if team_slug not in nba_teams:
                        continue
                    players = re.findall(r"([A-Z][a-z]+ [A-Z][a-z]+)", players_part)
                    for player in players:
                        player_folder = format_player_name(player)
                        traded_players[player_folder] = team_slug
                elif "to the" in text.lower():
                    match = re.search(r"([A-Z][a-z]+ [A-Z][a-z]+)\s*to the\s*(\w+\s*\w*)", text, re.IGNORECASE)
                    if match:
                        player_name = match.group(1)
                        team_name = match.group(2)
                        player_folder = format_player_name(player_name)
                        team_slug = team_name_to_slug(team_name)
                        if team_slug not in nba_teams:
                            continue
                        traded_players[player_folder] = team_slug

    # Cache the trade data
    cache_data = {
        "timestamp": datetime.now().isoformat(),
        "traded_players": traded_players
    }
    with open(TRADE_CACHE_FILE, "w") as f:
        json.dump(cache_data, f)
    print(f"Trade data cached to {TRADE_CACHE_FILE}")

    return traded_players

def fetch_player_ids():
    """
    Fetch all NBA player IDs using nba_api and create a mapping of player_folder to player_id and team.
    Returns a dictionary mapping player_folder to {'id': player_id, 'team': team_slug}.
    """
    # Check if cache exists and is recent
    if os.path.exists(PLAYER_ID_CACHE_FILE):
        with open(PLAYER_ID_CACHE_FILE, "r") as f:
            cache_data = json.load(f)
        cache_time = datetime.fromisoformat(cache_data["timestamp"])
        current_time = datetime.now()
        # Use cache if it's less than 24 hours old
        if (current_time - cache_time).total_seconds() < 24 * 60 * 60:
            print("Using cached player ID data.")
            return cache_data["player_ids"]

    print("Fetching player IDs from nba_api...")
    try:
        # Fetch all players for the 2024-2025 season
        all_players = commonallplayers.CommonAllPlayers(season="2024-25", is_only_current_season=1)
        players_df = all_players.get_data_frames()[0]
    except Exception as e:
        print(f"Failed to fetch player IDs: {e}")
        return {}

    player_id_mapping = {}
    for _, row in players_df.iterrows():
        player_name = row["DISPLAY_FIRST_LAST"]
        player_id = str(row["PERSON_ID"])
        team_name = row["TEAM_NAME"]
        # Only include players with a team (active players)
        if team_name and team_name.strip():
            player_folder = format_player_name(player_name)
            team_slug = team_name_to_slug(team_name)
            if team_slug in nba_teams:
                player_id_mapping[player_folder] = {
                    "id": player_id,
                    "team": team_slug
                }

    # Cache the player ID data
    cache_data = {
        "timestamp": datetime.now().isoformat(),
        "player_ids": player_id_mapping
    }
    with open(PLAYER_ID_CACHE_FILE, "w") as f:
        json.dump(cache_data, f)
    print(f"Player ID data cached to {PLAYER_ID_CACHE_FILE}")

    return player_id_mapping

# Updated template to handle three columns: Stat Category, Value, Qualified Rank
PLAYER_STATS_TEMPLATE = '''import pandas as pd
import re
import os
from playwright.sync_api import sync_playwright

# Base directory for saving files
BASE_DIR = "{base_dir}/{team}/{player_folder}"
os.makedirs(BASE_DIR, exist_ok=True)

def format_player_name(player_name):
    """Convert player name to URL-friendly format."""
    formatted_name = player_name.lower().replace(" ", "-")
    formatted_name = re.sub(r"[^a-zA-Z0-9-]", "", formatted_name)
    return formatted_name

def split_value_and_rank(cell_text):
    """Split a cell's text into value and qualified rank (e.g., '1710 (#5)' -> ('1710', '#5'))."""
    # Clean the cell text by removing newlines and extra spaces
    cell_text = " ".join(cell_text.split())
    print(f"Raw cell text: {{cell_text}}")
    
    # Match value and rank with a more robust regex
    # This regex matches a value (which can include numbers, decimals, or percentages) followed by an optional rank in parentheses
    match = re.match(r"^(.*?)\s*(?:\\((#[0-9]+)\\))?$", cell_text)
    if match:
        value = match.group(1).strip() if match.group(1) else "N/A"
        rank = match.group(2) if match.group(2) else "N/A"
        print(f"Split result: Value={{value}}, Rank={{rank}}")
        return value, rank
    print(f"No match for cell text, returning as-is: {{cell_text}}")
    return cell_text, "N/A"

def print_table(title, data, columns):
    """Print a formatted table to the terminal."""
    if not data:
        print(f"\\n{{title}}: No data available.")
        return
    
    print(f"\\n{{title}}")
    col_widths = [max(len(str(row[i])) for row in data + [columns]) for i in range(len(columns))]
    top_border = "┌" + "─".join("─" * (w + 2) for w in col_widths) + "┐"
    bottom_border = "└" + "─".join("─" * (w + 2) for w in col_widths) + "┘"
    separator = "├" + "─".join("─" * (w + 2) for w in col_widths) + "┤"
    
    header_row = "│ " + " │ ".join(str(h).center(w) for h, w in zip(columns, col_widths)) + " │"
    print(top_border)
    print(header_row)
    print(separator)
    
    for row in data:
        row_str = "│ " + " │ ".join(str(item).ljust(w) if item != "N/A" else "N/A".ljust(w) for item, w in zip(row, col_widths)) + " │"
        print(row_str)
    print(bottom_border)

def fetch_and_save_{player_function}_stats():
    """Fetch and save stats for {player_name} from TeamRankings."""
    player_name = "{player_name}"
    formatted_name = "{player_id}"
    url = f"https://www.teamrankings.com/nba/player/{{formatted_name}}/stats"
    
    print(f"Fetching stats for {{player_name}} from {{url}}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_extra_http_headers({{
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        }})
        page.goto(url)
        
        try:
            page.wait_for_selector('table', timeout=30000)
            page.wait_for_timeout(2000)
            tables = page.query_selector_all('table')
        except Exception as e:
            print(f"Failed to find any tables: {{e}}. Page may not exist.")
            tables = []
        
        print(f"Number of tables found: {{len(tables)}}")
        
        basic_data = []
        ranking_data = []
        
        if not tables:
            print("No tables found on page.")
            basic_data = [["No Tables Found", "N/A", "N/A"]]
            ranking_data = [["No Tables Found", "N/A", "N/A"]]
        else:
            # Process "Basic Stat Highlights" table (first table, 9 columns)
            if len(tables) >= 1:
                basic_table = tables[0]
                rows = basic_table.query_selector_all('tr')
                print(f"Number of rows in Basic Stat Highlights table: {{len(rows)}}")
                
                if len(rows) >= 4:  # Expect header + 3 rows (Season Totals, Per Minute, Per Game)
                    headers = [col.inner_text().strip() for col in rows[0].query_selector_all('th')]
                    print(f"Basic Stat Headers: {{headers}}")
                    
                    # Skip the first header if it's empty
                    if headers[0] == '':
                        headers = headers[1:]
                        start_col = 1
                    else:
                        start_col = 0
                    
                    for i, row in enumerate(rows[1:4], 1):  # Process rows 1-3
                        cols = row.query_selector_all('td')
                        if len(cols) == len(headers) + start_col:
                            row_name = cols[0].inner_text().strip()  # e.g., "Season Totals"
                            for j in range(1, len(cols)):
                                stat_name = f"{{row_name}} {{headers[j - start_col]}}"
                                cell_text = cols[j].inner_text().strip()
                                value, rank = split_value_and_rank(cell_text)
                                basic_data.append([stat_name, value, rank])
                        else:
                            print(f"Row {{i}} in Basic Stat Highlights has {{len(cols)}} columns, expected {{len(headers) + start_col}}")
                            basic_data.append(["Parse Error", "Column mismatch", "N/A"])
                else:
                    basic_data.append(["No Data Available", "N/A", "N/A"])
            
            # Process "Player Ranking Summary" table
            ranking_table_found = False
            for table_idx, table in enumerate(tables[1:], 1):
                rows = table.query_selector_all('tr')
                print(f"Number of rows in table {{table_idx + 1}}: {{len(rows)}}")
                
                if len(rows) < 2:
                    continue
                
                headers = [col.inner_text().strip() for col in rows[0].query_selector_all('th')]
                print(f"Table {{table_idx + 1}} Headers: {{headers}}")
                
                # Check if this is the "Player Ranking Summary" table
                if "Season Totals" in headers and "Per Minute" in headers and "Per Game" in headers:
                    ranking_table_found = True
                    for i, row in enumerate(rows[1:], 1):  # Skip header
                        cols = row.query_selector_all('td')
                        raw_cols = [col.inner_text().strip() for col in cols]
                        print(f"Row {{i}} in table {{table_idx + 1}} has {{len(cols)}} columns: {{raw_cols}}")
                        if len(cols) >= 7:  # Expect 7 columns: Stat, Season Totals value, Season Totals rank, Per Minute value, Per Minute rank, Per Game value, Per Game rank
                            stat_name = raw_cols[0]  # e.g., "Points"
                            # Process each pair of columns (value and rank) for Season Totals, Per Minute, Per Game
                            for j in range(1, 6, 2):  # Step by 2 to process pairs: (1,2) for Season Totals, (3,4) for Per Minute, (5,6) for Per Game
                                if j + 1 < len(raw_cols):  # Ensure both value and rank columns exist
                                    # Map the column index to the header
                                    header_idx = (j - 1) // 2 + 1  # Maps j=1 to "Season Totals", j=3 to "Per Minute", j=5 to "Per Game"
                                    category = f"{{stat_name}} {{headers[header_idx]}}"
                                    # Combine the value and rank into a single string
                                    value_text = raw_cols[j]
                                    rank_text = raw_cols[j + 1] if raw_cols[j + 1] else ""
                                    combined_text = f"{{value_text}} {{rank_text}}".strip()
                                    value, rank = split_value_and_rank(combined_text)
                                    print(f"Appending for {{category}}: Value={{value}}, Rank={{rank}}")
                                    ranking_data.append([category, value, rank])
                                else:
                                    print(f"Missing data for {{stat_name}} {{headers[(j-1)//2 + 1]}} in row {{i}}")
                                    ranking_data.append([f"{{stat_name}} {{headers[(j-1)//2 + 1]}}", "N/A", "N/A"])
                        else:
                            print(f"Row {{i}} in table {{table_idx + 1}} has {{len(cols)}} columns, expected at least 7")
                            ranking_data.append(["Parse Error", "Column mismatch", "N/A"])
                    break
            
            if not ranking_table_found:
                print("Player Ranking Summary table not found.")
                ranking_data.append(["Table Not Found", "N/A", "N/A"])
        
        browser.close()
    
    # Create DataFrames
    basic_df = pd.DataFrame(basic_data, columns=["Stat Category", "Value", "Qualified Rank"])
    ranking_df = pd.DataFrame(ranking_data, columns=["Stat Category", "Value", "Qualified Rank"])
    
    # Save Basic Stat Highlights to CSV and Excel
    basic_csv_filename = os.path.join(BASE_DIR, "{player_folder}_basic_stats.csv")
    basic_df.to_csv(basic_csv_filename, index=False)
    print(f"Basic Stats CSV file saved: {{basic_csv_filename}}")
    
    basic_excel_filename = os.path.join(BASE_DIR, "{player_folder}_basic_stats.xlsx")
    basic_df.to_excel(basic_excel_filename, index=False)
    print(f"Basic Stats Excel file saved: {{basic_excel_filename}}")
    
    # Save Player Ranking Summary to CSV and Excel
    ranking_csv_filename = os.path.join(BASE_DIR, "{player_folder}_ranking_stats.csv")
    ranking_df.to_csv(ranking_csv_filename, index=False)
    print(f"Ranking Stats CSV file saved: {{ranking_csv_filename}}")
    
    ranking_excel_filename = os.path.join(BASE_DIR, "{player_folder}_ranking_stats.xlsx")
    ranking_df.to_excel(ranking_excel_filename, index=False)
    print(f"Ranking Stats Excel file saved: {{ranking_excel_filename}}")
    
    # Print both tables to terminal
    print_table(f"Basic Stat Highlights for {{player_name}}", basic_data, ["Stat Category", "Value", "Qualified Rank"])
    print_table(f"Player Ranking Summary for {{player_name}}", ranking_data, ["Stat Category", "Value", "Qualified Rank"])
    
    return basic_df, ranking_df

if __name__ == "__main__":
    fetch_and_save_{player_function}_stats()
'''

# Fetch the list of traded players dynamically
traded_players = fetch_traded_players()

# Fetch the player ID mapping
player_id_mapping = fetch_player_ids()

# Check for existing roster CSVs
roster_files_exist = False
for team in nba_teams:
    roster_csv = os.path.join(ROSTER_DIR, team, f"{team}_roster.csv")
    if os.path.exists(roster_csv):
        roster_files_exist = True
        break

# If no roster files exist, run the roster generator script
if not roster_files_exist:
    print(f"No roster CSVs found in {ROSTER_DIR}. Running {ROSTER_GENERATOR_SCRIPT} to generate them...")
    try:
        result = subprocess.run(["python", ROSTER_GENERATOR_SCRIPT], check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(f"Errors from roster generator: {result.stderr}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to run {ROSTER_GENERATOR_SCRIPT}: {e}")
        print(f"Error output: {e.stderr}")
        exit(1)
else:
    print(f"Roster CSVs found in {ROSTER_DIR}. Proceeding with player stats generation...")

# Collect all players from roster CSVs
player_team_mapping = {}
for team in nba_teams:
    roster_csv = os.path.join(ROSTER_DIR, team, f"{team}_roster.csv")
    if os.path.exists(roster_csv):
        try:
            df = pd.read_csv(roster_csv)
            if "Player Name" in df.columns:
                for player_name in df["Player Name"].dropna():
                    player_folder = format_player_name(player_name)
                    player_team_mapping[player_folder] = {
                        "name": player_name,
                        "team": team
                    }
            else:
                print(f"Warning: 'Player Name' column not found in {roster_csv}")
        except Exception as e:
            print(f"Error reading {roster_csv}: {e}")
    else:
        print(f"Warning: Roster CSV not found for {team} at {roster_csv}")

if not player_team_mapping:
    print("No players found in roster CSVs. Exiting.")
    exit(1)

# Override team assignments for all traded players
for player_folder, current_team in traded_players.items():
    if player_folder in player_team_mapping:
        old_team = player_team_mapping[player_folder]["team"]
        print(f"Found {player_team_mapping[player_folder]['name']} in roster for {old_team}")
        if old_team != current_team:
            print(f"Updating team for {player_team_mapping[player_folder]['name']} from {old_team} to {current_team}")
            player_team_mapping[player_folder]["team"] = current_team
        else:
            print(f"No update needed for {player_team_mapping[player_folder]['name']}: already on {current_team}")
    else:
        player_name = " ".join(word.capitalize() for word in player_folder.split("-"))
        print(f"Adding traded player {player_name} to {current_team} (not found in any roster)")
        player_team_mapping[player_folder] = {"name": player_name, "team": current_team}

# Update player_id_mapping with current teams after trades
for player_folder in player_team_mapping:
    if player_folder in player_id_mapping:
        current_team = player_team_mapping[player_folder]["team"]
        player_id_mapping[player_folder]["team"] = current_team
    else:
        # If player not found in API data, use the formatted name as the ID
        player_name = player_team_mapping[player_folder]["name"]
        current_team = player_team_mapping[player_folder]["team"]
        print(f"Warning: {player_name} not found in NBA API data. Using formatted name as ID.")
        player_id_mapping[player_folder] = {
            "id": player_folder,
            "team": current_team
        }

# Generate a script and folder for each player under their current team folder
for player_folder, info in player_team_mapping.items():
    player_name = info["name"]
    team = info["team"]
    player_function = player_folder.replace("-", "_")
    
    # Get the player ID from the mapping
    player_info = player_id_mapping.get(player_folder, {"id": player_folder})
    player_id = player_info["id"]
    
    # Create team-specific folder and player subfolder
    player_dir = os.path.join(BASE_DIR, team, player_folder)
    os.makedirs(player_dir, exist_ok=True)
    
    # Generate script content
    script_content = PLAYER_STATS_TEMPLATE.format(
        base_dir=BASE_DIR,
        team=team,
        player_folder=player_folder,
        player_name=player_name,
        player_function=player_function,
        player_id=player_id
    )
    
    # Write script to file with "teamrankings" suffix
    script_filename = os.path.join(player_dir, f"{player_folder}_stats_teamrankings.py")
    with open(script_filename, "w", encoding="utf-8") as f:
        f.write(script_content.strip())
    
    print(f"Script generated for {player_name} ({team}): {script_filename}")

print("All player stats scripts have been generated successfully!")