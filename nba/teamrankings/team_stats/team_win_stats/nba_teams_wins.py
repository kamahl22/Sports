import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd

# Base directory where team folders will be created
BASE_DIR = "/Users/kamahl/Sports/scripts/nba/teamrankings/team_stats/team_win_stats/nba_teams"
os.makedirs(BASE_DIR, exist_ok=True)

# List of NBA teams
nba_teams = [
    "cleveland-cavaliers", "los-angeles-lakers", "miami-heat", "chicago-bulls", 
    "new-york-knicks", "golden-state-warriors", "brooklyn-nets", "boston-celtics",
    "atlanta-hawks", "charlotte-hornets", "chicago-bulls", "dallas-mavericks", 
    "denver-nuggets", "detroit-pistons", "indiana-pacers", "los-angeles-clippers", 
    "memphis-grizzlies", "minnesota-timberwolves", "new-orleans-pelicans", "orlando-magic", 
    "philadelphia-76ers", "phoenix-suns", "portland-trail-blazers", "sacramento-kings", 
    "san-antonio-spurs", "toronto-raptors", "utah-jazz", "washington-wizards", 
    "houston-rockets", "oklahoma-city-thunder"
]

# Template for the team Wins script (raw table output, fixed By.TAG_NAME)
WINS_TEMPLATE = '''import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import os

# Base directory for saving files
BASE_DIR = "{base_dir}"
os.makedirs(BASE_DIR, exist_ok=True)

def fetch_and_save_{team_name_underscore}_win_trends():
    """Fetch, save, and print the {team_name_display} win trends from TeamRankings."""
    url = "https://www.teamrankings.com/nba/team/{team_name}/win-trends"
    
    # Set up headless Chrome with enhanced options
    options = Options()
    options.headless = True  # Primary headless setting (Selenium 4+)
    options.add_argument('--headless')  # Legacy headless argument for compatibility
    options.add_argument('--no-sandbox')  # Improve stability in some environments
    options.add_argument('--disable-dev-shm-usage')  # Reduce resource usage
    options.add_argument('--disable-gpu')  # Disable GPU (not needed in headless)
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    print(f"Fetching win trends for {team_name_display}")
    driver.get(url)
    
    # Wait for the table to load (up to 10 seconds)
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "tr-table"))
        )
        time.sleep(2)  # Additional wait for data
    except Exception as e:
        print(f"Error waiting for table: {{e}}")
        driver.quit()
        return None
    
    # Find all tables
    tables = driver.find_elements(By.TAG_NAME, "table")
    print(f"Number of tables found: {{len(tables)}}")
    
    if not tables:
        print("No tables found.")
        driver.quit()
        return None
    
    data = []
    for table in tables:
        if "tr-table" in table.get_attribute("class"):
            print(f"Processing win trends table")
            rows = table.find_elements(By.TAG_NAME, "tr")  # Fixed: By_TAG_NAME -> By.TAG_NAME
            for row in rows[1:]:  # Skip header row
                cols = row.find_elements(By.TAG_NAME, "td")  # Fixed: By_TAG_NAME -> By.TAG_NAME
                if len(cols) >= 5:
                    trend = cols[0].text.strip()
                    win_record = cols[1].text.strip()
                    win_pct = cols[2].text.strip()
                    mov = cols[3].text.strip()
                    ats_plus_minus = cols[4].text.strip()
                    data.append([trend, win_record, win_pct, mov, ats_plus_minus])
    
    driver.quit()
    
    if not data:
        print("No data extracted from tables.")
        return None
    
    # Create DataFrame with raw headers
    headers = ["Trend", "Win Record", "Win %", "MOV", "ATS +/-"]
    df = pd.DataFrame(data, columns=headers)
    
    # Save to CSV
    team_name_lower = "{team_name}"
    csv_filename = os.path.join(BASE_DIR, team_name_lower, "{team_name}_win_trends.csv")
    os.makedirs(os.path.dirname(csv_filename), exist_ok=True)
    df.to_csv(csv_filename, index=False)
    print(f"CSV file saved: {{csv_filename}}")
    
    # Save to Excel
    excel_filename = os.path.join(BASE_DIR, team_name_lower, "{team_name}_win_trends.xlsx")
    df.to_excel(excel_filename, index=False)
    print(f"Excel file saved: {{excel_filename}}")
    
    # Print formatted table
    print(f"\\nWin Trends for {team_name_display}")
    col_widths = [max(len(str(row[i])) for row in data + [headers]) for i in range(5)]
    top_border = "┌" + "─".join("─" * (w + 2) for w in col_widths) + "┐"
    bottom_border = "└" + "─".join("─" * (w + 2) for w in col_widths) + "┘"
    separator = "├" + "─".join("─" * (w + 2) for w in col_widths) + "┤"
    
    header_row = "│ " + " │ ".join(h.center(w) for h, w in zip(headers, col_widths)) + " │"
    print(top_border)
    print(header_row)
    print(separator)
    
    for row in data:
        row_str = "│ " + " │ ".join(str(item).ljust(w) for item, w in zip(row, col_widths)) + " │"
        print(row_str)
    print(bottom_border)  # Should be bottom_border
    
    return df

if __name__ == "__main__":
    fetch_and_save_{team_name_underscore}_win_trends()
'''

def generate_wins_scripts():
    for team_name in nba_teams:
        team_folder = os.path.join(BASE_DIR, team_name)
        os.makedirs(team_folder, exist_ok=True)
        
        team_name_display = team_name.replace("-", " ").title()
        team_name_underscore = team_name.replace("-", "_")
        
        script_content = WINS_TEMPLATE.format(
            base_dir=BASE_DIR,
            team_name=team_name,
            team_name_display=team_name_display,
            team_name_underscore=team_name_underscore
        )
        
        script_filename = f"{team_name}_win_trends.py"
        script_path = os.path.join(team_folder, script_filename)
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(script_content)
        
        print(f"Created win trends script: {script_path}")

if __name__ == "__main__":
    print("Generating win trends scripts...")
    generate_wins_scripts()
    print("Done! All win trends scripts have been generated.")