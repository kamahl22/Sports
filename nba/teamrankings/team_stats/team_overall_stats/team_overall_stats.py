# What this script does
# This script fetches team stats fromm team rankings for each nba team
# creates a folder for each team with team name
# creates a script for each player to have their own playername_stats.py script

# generate_team_stats_scripts.py
import os
import csv

# Base directory where team folders will be created
BASE_DIR = "/Users/kamahl/Sports/scripts/nba/teamrankings/team_stats/team_overall_stats/nba_teams"
os.makedirs(BASE_DIR, exist_ok=True)

# Template for the team_stats.py script
TEAM_STATS_TEMPLATE = '''import requests
from bs4 import BeautifulSoup
import csv
import os
import pandas as pd

# Base directory for saving files
BASE_DIR = "{base_dir}"
os.makedirs(BASE_DIR, exist_ok=True)

def fetch_and_save_{team_name_underscore}_stats():
    """Fetch, save, and print the {team_name_display} team statistics from TeamRankings."""
    url = "https://www.teamrankings.com/nba/team/{team_name}/stats"
    
    headers = {{
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }}
    response = requests.get(url, headers=headers)
    
    print(f"Status Code: {{response.status_code}}")
    if response.status_code != 200:
        print(f"Error: Unable to fetch stats for {team_name_display} - Status Code {{response.status_code}}")
        return None
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Find all tables
    tables = soup.find_all("table")
    print(f"Number of tables found: {{len(tables)}}")
    
    if not tables:
        print("No tables found. Dumping page snippet for debugging:")
        print(soup.prettify()[:2000])
        return None
    
    # Expected categories
    categories = [
        "Overall Statistics",
        "Shooting Statistics",
        "Scoring Statistics",
        "Rebounding Statistics",
        "Blocks Statistics",
        "Steals Statistics",
        "Turnovers Statistics",
        "Fouls Statistics"
    ]
    
    all_stats = {{}}
    
    # Process tables
    for table in tables:
        section_header = table.find_previous("h2")
        category = section_header.text.strip() if section_header else "Unknown"
        print(f"Processing table category: {{category}}")
        
        if category in categories:
            stats = []
            rows = table.find_all("tr")
            for row in rows:
                cols = row.find_all("td")
                if len(cols) >= 4:
                    stat_name = cols[0].text.strip() if cols[0].text.strip() else "Unnamed Stat"
                    offense_value = cols[1].text.strip()
                    defense_stat_name = cols[2].text.strip() if len(cols) > 2 and cols[2].text.strip() else "Opp " + stat_name
                    defense_value = cols[3].text.strip()
                    stats.append((stat_name, offense_value, defense_stat_name, defense_value))
            all_stats[category] = stats
    
    # Save to CSV and Excel
    team_name_lower = "{team_name}"
    csv_filename = os.path.join(BASE_DIR, team_name_lower, "{team_name}_stats.csv")
    excel_filename = os.path.join(BASE_DIR, team_name_lower, "{team_name}_stats.xlsx")
    
    # Prepare data for saving
    headers = ["Category", "MIN Offense", "Value (rank)", "MIN Defense", "Value (rank)"]
    all_rows = []
    for category, stats_list in all_stats.items():
        for stat in stats_list:
            all_rows.append([category, stat[0], stat[1], stat[2], stat[3]])
    
    # Save to CSV
    os.makedirs(os.path.dirname(csv_filename), exist_ok=True)
    with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(all_rows)
    print(f"CSV file saved: {{csv_filename}}")
    
    # Save to Excel
    os.makedirs(os.path.dirname(excel_filename), exist_ok=True)
    df = pd.DataFrame(all_rows, columns=headers)
    df.to_excel(excel_filename, index=False)
    print(f"Excel file saved: {{excel_filename}}")
    
    # Print stats in an Excel-like format
    for category, stats_list in all_stats.items():
        print(f"\\n{{category}}")
        if not stats_list:
            print("No stats found for this category.")
            continue
        
        col_widths = [max(len(str(item)) for item in [stat[0] for stat in stats_list] + ["MIN Offense"]),
                      max(len(str(item)) for item in [stat[1] for stat in stats_list] + ["Value (rank)"]),
                      max(len(str(item)) for item in [stat[2] for stat in stats_list] + ["MIN Defense"]),
                      max(len(str(item)) for item in [stat[3] for stat in stats_list] + ["Value (rank)"])]
        
        top_border = "┌" + "─".join("─" * (w + 2) for w in col_widths) + "┐"
        bottom_border = "└" + "─".join("─" * (w + 2) for w in col_widths) + "┘"
        separator = "├" + "─".join("─" * (w + 2) for w in col_widths) + "┤"
        
        header_row = "│ " + " │ ".join(h.center(w) for h, w in zip(["MIN Offense", "Value (rank)", "MIN Defense", "Value (rank)"], col_widths)) + " │"
        print(top_border)
        print(header_row)
        print(separator)
        
        for stat_name, offense_value, defense_stat_name, defense_value in stats_list:
            row = "│ " + " │ ".join(str(item).ljust(w) for item, w in zip([stat_name, offense_value, defense_stat_name, defense_value], col_widths)) + " │"
            print(row)
        
        print(bottom_border)
    
    return all_stats

if __name__ == "__main__":
    stats = fetch_and_save_{team_name_underscore}_stats()
'''

# List of NBA team names (slug format used by TeamRankings)
TEAM_LIST = [
    "cleveland-cavaliers", "los-angeles-lakers", "miami-heat", "chicago-bulls",
    "new-york-knicks", "golden-state-warriors", "brooklyn-nets", "boston-celtics",
    "atlanta-hawks", "charlotte-hornets", "dallas-mavericks",
    "denver-nuggets", "detroit-pistons", "indiana-pacers", "los-angeles-clippers", "milwaukee-bucks",
    "memphis-grizzlies", "minnesota-timberwolves", "new-orleans-pelicans", "orlando-magic",
    "philadelphia-76ers", "phoenix-suns", "portland-trail-blazers", "sacramento-kings",
    "san-antonio-spurs", "toronto-raptors", "utah-jazz", "washington-wizards",
    "houston-rockets", "oklahoma-city-thunder"
]

def generate_team_stats_scripts():
    """Generate team stats scripts for each NBA team."""
    for team_name in TEAM_LIST:
        # Create team folder
        team_folder = os.path.join(BASE_DIR, team_name)
        os.makedirs(team_folder, exist_ok=True)
        
        # Display name for printing (capitalize and replace hyphens with spaces)
        team_name_display = team_name.replace("-", " ").title()
        
        # Replace hyphens with underscores for the function name
        team_name_underscore = team_name.replace("-", "_")
        
        # Customize the template
        script_content = TEAM_STATS_TEMPLATE.format(
            base_dir=BASE_DIR,
            team_name=team_name,
            team_name_display=team_name_display,
            team_name_underscore=team_name_underscore
        )
        
        # Write the script
        script_filename = f"{team_name}_team_stats.py"
        script_path = os.path.join(team_folder, script_filename)
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(script_content)
        
        print(f"Created team stats script: {script_path}")

if __name__ == "__main__":
    print("Generating team stats scripts...")
    generate_team_stats_scripts()
    print("Done! All team stats scripts have been generated.")