import os
import csv

# Base directory where team folders will be created
BASE_DIR = "/Users/kamahl/Sports/scripts/nba/teamrankings/team_stats/team_ats_stats/nba_teams"
os.makedirs(BASE_DIR, exist_ok=True)

# Template for the ATS trends script with Selenium
ATS_TEMPLATE = '''import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import os
import pandas as pd
from webdriver_manager.chrome import ChromeDriverManager

# Base directory for saving files
BASE_DIR = "{base_dir}"
os.makedirs(BASE_DIR, exist_ok=True)

def fetch_and_save_{team_name_underscore}_ats_trends():
    """Fetch, save, and print the {team_name_display} ATS trends from TeamRankings."""
    url = "https://www.teamrankings.com/nba/team/{team_name}/ats-trends"
    
    # Set up Selenium WebDriver
    options = Options()
    options.headless = False  # Set to True for headless mode if desired
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        driver.get(url)
        
        # Wait for the table to load (up to 20 seconds)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//table[contains(@class, "tr-table")]//tbody/tr[not(contains(., "Loading"))]'))
        )
        
        # Give extra time for stability
        time.sleep(2)
        
        # Find all tables
        tables = driver.find_elements(By.XPATH, '//table[contains(@class, "tr-table")]')
        print(f"Number of tables found: {{len(tables)}}")
        
        if not tables:
            print("No tables found. Dumping page snippet for debugging:")
            print(driver.page_source[:2000])
            return None
        
        all_trends = {{}}
        
        # Process tables
        for table in tables:
            # Determine category
            section_header = table.find_element(By.XPATH, './preceding-sibling::h2')
            category = section_header.text.strip() if section_header and "Trends" in section_header.text else "ATS Trends"
            print(f"Processing table category: {{category}}")
            
            trends = []
            rows = table.find_elements(By.TAG_NAME, "tr")
            for row in rows:
                cols = row.find_elements(By.TAG_NAME, "td")
                if len(cols) >= 5:  # Ensure at least 5 columns
                    trend = cols[0].text.strip()
                    ats_record = cols[1].text.strip()
                    cover_percent = cols[2].text.strip()
                    mov = cols[3].text.strip()
                    ats_plus_minus = cols[4].text.strip()
                    trends.append((trend, ats_record, cover_percent, mov, ats_plus_minus))
            if trends:
                all_trends[category] = trends
            else:
                print(f"No valid rows found in table for category: {{category}}. Dumping table HTML:")
                print(table.get_attribute('outerHTML')[:1000])
        
        if not all_trends:
            print("No ATS trends data extracted. Check table structure or page content.")
            return None
        
        # Save to CSV and Excel
        team_name_lower = "{team_name}"
        csv_filename = os.path.join(BASE_DIR, team_name_lower, "{team_name}_ats_trends.csv")
        excel_filename = os.path.join(BASE_DIR, team_name_lower, "{team_name}_ats_trends.xlsx")
        
        # Prepare data for saving
        headers = ["Category", "Trend", "ATS Record", "Cover %", "MOV", "ATS +/-"]
        all_rows = []
        for category, trends_list in all_trends.items():
            for trend in trends_list:
                all_rows.append([category] + list(trend))
        
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
        
        # Print trends in an Excel-like format
        for category, trends_list in all_trends.items():
            print(f"\\n{{category}}")
            if not trends_list:
                print("No trends found for this category.")
                continue
            
            col_widths = [max(len(str(item)) for item in [trend[0] for trend in trends_list] + ["Trend"]),
                          max(len(str(item)) for item in [trend[1] for trend in trends_list] + ["ATS Record"]),
                          max(len(str(item)) for item in [trend[2] for trend in trends_list] + ["Cover %"]),
                          max(len(str(item)) for item in [trend[3] for trend in trends_list] + ["MOV"]),
                          max(len(str(item)) for item in [trend[4] for trend in trends_list] + ["ATS +/-"])]
            
            top_border = "┌" + "─".join("─" * (w + 2) for w in col_widths) + "┐"
            bottom_border = "└" + "─".join("─" * (w + 2) for w in col_widths) + "┘"
            separator = "├" + "─".join("─" * (w + 2) for w in col_widths) + "┤"
            
            header_row = "│ " + " │ ".join(h.center(w) for h, w in zip(["Trend", "ATS Record", "Cover %", "MOV", "ATS +/-"], col_widths)) + " │"
            print(top_border)
            print(header_row)
            print(separator)
            
            for trend in trends_list:
                row = "│ " + " │ ".join(str(item).ljust(w) for item, w in zip(trend, col_widths)) + " │"
                print(row)
            
            print(bottom_border)  # Should be bottom_border
        
    finally:
        driver.quit()
    
    return all_trends

if __name__ == "__main__":
    trends = fetch_and_save_{team_name_underscore}_ats_trends()
'''

# List of NBA team names
TEAM_LIST = [
    "atlanta-hawks", "boston-celtics", "brooklyn-nets", "charlotte-hornets", "chicago-bulls",
    "cleveland-cavaliers", "dallas-mavericks", "denver-nuggets", "detroit-pistons", "golden-state-warriors",
    "houston-rockets", "indiana-pacers", "los-angeles-clippers", "los-angeles-lakers", "memphis-grizzlies",
    "miami-heat", "milwaukee-bucks", "minnesota-timberwolves", "new-orleans-pelicans", "new-york-knicks",
    "oklahoma-city-thunder", "orlando-magic", "philadelphia-76ers", "phoenix-suns", "portland-trail-blazers",
    "sacramento-kings", "san-antonio-spurs", "toronto-raptors", "utah-jazz", "washington-wizards"
]

def generate_ats_scripts():
    """Generate ATS trends scripts for each NBA team."""
    for team_name in TEAM_LIST:
        team_folder = os.path.join(BASE_DIR, team_name)
        os.makedirs(team_folder, exist_ok=True)
        
        team_name_display = team_name.replace("-", " ").title()
        team_name_underscore = team_name.replace("-", "_")
        
        script_content = ATS_TEMPLATE.format(
            base_dir=BASE_DIR,
            team_name=team_name,
            team_name_display=team_name_display,
            team_name_underscore=team_name_underscore
        )
        
        script_filename = f"{team_name}_ats_trends.py"
        script_path = os.path.join(team_folder, script_filename)
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(script_content)
        
        print(f"Created ATS trends script: {script_path}")

if __name__ == "__main__":
    print("Generating ATS trends scripts...")
    generate_ats_scripts()
    print("Done! All ATS trends scripts have been generated.")