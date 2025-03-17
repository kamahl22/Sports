import time
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
BASE_DIR = "/Users/kamahl/Sports/scripts/nba/teamrankings/team_stats/team_ou_stats/nba_teams"
os.makedirs(BASE_DIR, exist_ok=True)

def fetch_and_save_golden_state_warriors_over_under_trends():
    """Fetch, save, and print the Golden State Warriors Over/Under trends from TeamRankings."""
    url = "https://www.teamrankings.com/nba/team/golden-state-warriors/over-under-trends"
    
    # Set up headless Chrome with enhanced options
    options = Options()
    options.headless = True  # Primary headless setting (Selenium 4+)
    options.add_argument('--headless')  # Legacy headless argument for compatibility
    options.add_argument('--no-sandbox')  # Improve stability in some environments
    options.add_argument('--disable-dev-shm-usage')  # Reduce resource usage
    options.add_argument('--disable-gpu')  # Disable GPU (not needed in headless)
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    print(f"Fetching Over/Under trends for Golden State Warriors")
    driver.get(url)
    
    # Wait for the table to load (up to 10 seconds)
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "tr-table"))
        )
        time.sleep(2)  # Additional wait for data
    except Exception as e:
        print(f"Error waiting for table: {e}")
        driver.quit()
        return None
    
    # Find all tables
    tables = driver.find_elements(By.TAG_NAME, "table")
    print(f"Number of tables found: {len(tables)}")
    
    if not tables:
        print("No tables found.")
        driver.quit()
        return None
    
    data = []
    for table in tables:
        if "tr-table" in table.get_attribute("class"):
            print(f"Processing Over/Under trends table")
            rows = table.find_elements(By.TAG_NAME, "tr")  # Fixed: By.TAG_NAME
            for row in rows[1:]:  # Skip header row
                cols = row.find_elements(By.TAG_NAME, "td")  # Fixed: By.TAG_NAME
                if len(cols) >= 5:
                    trend = cols[0].text.strip()
                    over_record = cols[1].text.strip()
                    over_pct = cols[2].text.strip()
                    under_pct = cols[3].text.strip()
                    total_plus_minus = cols[4].text.strip()
                    data.append([trend, over_record, over_pct, under_pct, total_plus_minus])
    
    driver.quit()
    
    if not data:
        print("No data extracted from tables.")
        return None
    
    # Create DataFrame with raw headers
    headers = ["Trend", "Over Record", "Over %", "Under %", "Total +/-"]
    df = pd.DataFrame(data, columns=headers)
    
    # Save to CSV
    team_name_lower = "golden-state-warriors"
    csv_filename = os.path.join(BASE_DIR, team_name_lower, "golden-state-warriors_over_under_trends.csv")
    os.makedirs(os.path.dirname(csv_filename), exist_ok=True)
    df.to_csv(csv_filename, index=False)
    print(f"CSV file saved: {csv_filename}")
    
    # Save to Excel
    excel_filename = os.path.join(BASE_DIR, team_name_lower, "golden-state-warriors_over_under_trends.xlsx")
    df.to_excel(excel_filename, index=False)
    print(f"Excel file saved: {excel_filename}")
    
    # Print formatted table
    print(f"\nOver/Under Trends for Golden State Warriors")
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
    fetch_and_save_golden_state_warriors_over_under_trends()
