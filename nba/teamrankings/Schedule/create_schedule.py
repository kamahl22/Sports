import os

# Base directory for output
BASE_DIR = "/Users/kamahl/Sports/scripts/nba/teamrankings/Schedule/nba_teams"
os.makedirs(BASE_DIR, exist_ok=True)

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

# Template for team schedule script with terminal printing
SCHEDULE_TEMPLATE = '''import pandas as pd
import os
from playwright.sync_api import sync_playwright

# Base directory for saving files
BASE_DIR = "{base_dir}/{team_name}"
os.makedirs(BASE_DIR, exist_ok=True)

def fetch_and_save_{team_name_underscore}_schedule():
    """Fetch and save the {team_name_display} schedule from TeamRankings."""
    url = "https://www.teamrankings.com/nba/team/{team_name}"
    
    print(f"Fetching schedule for {team_name_display} from {{url}}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_extra_http_headers({{
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        }})
        page.goto(url)
        
        page.wait_for_selector('table.tr-table', timeout=10000)
        page.wait_for_timeout(2000)
        
        tables = page.query_selector_all('table.tr-table')
        print(f"Number of tables found: {{len(tables)}}")
        
        if not tables:
            print("No tables found.")
            data = [["No Tables Found"] + ["N/A"] * 5]
        else:
            data = []
            schedule_table = None
            for table in tables:
                if "Date" in table.inner_text():  # Identify schedule table
                    schedule_table = table
                    break
            
            if schedule_table:
                rows = schedule_table.query_selector_all('tr')
                print(f"Number of rows in table: {{len(rows)}}")
                
                for i, row in enumerate(rows[1:]):  # Skip header
                    cols = row.query_selector_all('td')
                    print(f"Row {{i}} has {{len(cols)}} columns")
                    if len(cols) >= 6:
                        row_data = [col.inner_text().strip() for col in cols[:6]]
                        print(f"Row {{i}} data: {{row_data}}")
                        data.append(row_data)
                    else:
                        print(f"Row {{i}} skipped: insufficient columns ({{len(cols)}})")
            else:
                print("No matching schedule table found.")
                data = [["No Schedule Found"] + ["N/A"] * 5]
            
            if not data:
                print("No data extracted from tables.")
                data = [["No Data Available"] + ["N/A"] * 5]
        
        browser.close()
    
    # Create DataFrame
    df = pd.DataFrame(data, columns=["Date", "Opponent", "Result", "Location", "W/L", "Division"])
    
    # Save to CSV
    csv_filename = os.path.join(BASE_DIR, "{team_name}_schedule_results.csv")
    df.to_csv(csv_filename, index=False)
    print(f"CSV file saved: {{csv_filename}}")
    
    # Save to Excel
    excel_filename = os.path.join(BASE_DIR, "{team_name}_schedule_results.xlsx")
    df.to_excel(excel_filename, index=False)
    print(f"Excel file saved: {{excel_filename}}")
    
    # Print formatted table to terminal
    print(f"\\nSchedule for {team_name_display}")
    col_widths = [max(len(str(row[i])) for row in data + [df.columns]) for i in range(6)]
    top_border = "┌" + "─".join("─" * (w + 2) for w in col_widths) + "┐"
    bottom_border = "└" + "─".join("─" * (w + 2) for w in col_widths) + "┘"
    separator = "├" + "─".join("─" * (w + 2) for w in col_widths) + "┤"
    
    header_row = "│ " + " │ ".join(h.center(w) for h, w in zip(df.columns, col_widths)) + " │"
    print(top_border)
    print(header_row)
    print(separator)
    
    for row in data:
        row_str = "│ " + " │ ".join(str(item).ljust(w) for item, w in zip(row, col_widths)) + " │"
        print(row_str)
    print(bottom_border)  # Should be bottom_border
    
    return df

if __name__ == "__main__":
    fetch_and_save_{team_name_underscore}_schedule()
'''

for team in nba_teams:
    team_folder = os.path.join(BASE_DIR, team)
    os.makedirs(team_folder, exist_ok=True)
    
    team_name_display = team.replace("-", " ").title()
    team_name_underscore = team.replace("-", "_")
    
    script_content = SCHEDULE_TEMPLATE.format(
        base_dir=BASE_DIR,
        team_name=team,
        team_name_display=team_name_display,
        team_name_underscore=team_name_underscore
    )
    
    script_filename = os.path.join(team_folder, f"{team}_schedule_scraper.py")
    with open(script_filename, "w", encoding="utf-8") as f:
        f.write(script_content.strip())
    
    print(f"Script generated: {script_filename}")

print("All team schedule scripts have been generated successfully!")