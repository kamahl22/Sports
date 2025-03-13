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

def fetch_and_save_utah_jazz_ou_stats():
    """Fetch and print the Utah Jazz Over/Under trends from TeamRankings."""
    url = "https://www.teamrankings.com/nba/team/utah-jazz/over-under-trends"
    
    # Set up headless Chrome
    options = Options()
    options.headless = True  # Run in headless mode (no browser popup)
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    print(f"Fetching Over/Under trends for Utah Jazz")
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
    
    tables = driver.find_elements(By.TAG_NAME, "table")
    print(f"Number of tables found: {len(tables)}")
    
    if not tables:
        print("No tables found.")
        driver.quit()
        return None
    
    data = []
    for table in tables:
        if "tr-table" in table.get_attribute("class"):
            rows = table.find_elements(By.TAG_NAME, "tr")
            print(f"Number of rows in table: {len(rows)}")
            
            for row in rows[1:]:  # Skip header row
                cols = row.find_elements(By.TAG_NAME, "td")
                if len(cols) >= 5:
                    row_data = [col.text.strip() for col in cols[:5]]
                    print(f"Row data: {row_data}")
                    data.append(row_data)
    
    driver.quit()
    
    if not data:
        print("No data extracted from tables.")
        return None
    
    # Create DataFrame
    df = pd.DataFrame(data, columns=["Trend", "Over/Under Record", "Over/Under %", "MOV", "Over/Under +/-"])
    
    # Save to CSV
    csv_filename = os.path.join(BASE_DIR, "utah-jazz", "utah-jazz_over_under_trends.csv")
    os.makedirs(os.path.dirname(csv_filename), exist_ok=True)
    df.to_csv(csv_filename, index=False)
    print(f"CSV file saved: {csv_filename}")
    
    # Print formatted table
    print(f"\nOver/Under Trends for Utah Jazz")
    col_widths = [max(len(str(row[i])) for row in data + [df.columns]) for i in range(5)]
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
    print(bottom_border)
    
    return df

if __name__ == "__main__":
    fetch_and_save_utah_jazz_ou_stats()
