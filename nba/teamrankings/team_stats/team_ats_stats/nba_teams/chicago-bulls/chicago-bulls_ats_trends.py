import pandas as pd
import os
from playwright.sync_api import sync_playwright

# Base directory for saving files
BASE_DIR = "/Users/kamahl/Sports/scripts/nba/teamrankings/team_stats/team_ats_stats/nba_teams"
os.makedirs(BASE_DIR, exist_ok=True)

def fetch_and_save_chicago_bulls_ats_trends():
    """Fetch, save, and print the Chicago Bulls ATS trends from TeamRankings."""
    url = "https://www.teamrankings.com/nba/team/chicago-bulls/ats-trends"
    
    print(f"Fetching ATS trends for Chicago Bulls from {url}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        })
        page.goto(url)
        
        # Wait for table and ensure content is loaded
        page.wait_for_selector('table.tr-table', timeout=10000)
        page.wait_for_timeout(2000)  # Extra 2s to ensure JS renders fully
        
        # Debug: Print page content snippet
        content = page.content()
        print(f"Page content snippet: {content[:500]}...")
        
        tables = page.query_selector_all('table.tr-table')
        print(f"Number of tables found: {len(tables)}")
        
        if not tables:
            print("No tables found.")
            data = [["No Tables Found", "N/A", "N/A", "N/A", "N/A"]]
        else:
            data = []
            for table in tables:
                rows = table.query_selector_all('tr')
                print(f"Number of rows in table: {len(rows)}")
                
                for i, row in enumerate(rows):
                    cols = row.query_selector_all('td')
                    print(f"Row {i} has {len(cols)} columns")
                    if len(cols) >= 5:
                        row_data = [col.inner_text().strip() for col in cols[:5]]
                        print(f"Row {i} data: {row_data}")
                        data.append(row_data)
                    else:
                        print(f"Row {i} skipped: insufficient columns ({len(cols)})")
            
            if not data:
                print("No data extracted from tables.")
                data = [["No Data Available", "N/A", "N/A", "N/A", "N/A"]]
        
        browser.close()
    
    # Create DataFrame
    df = pd.DataFrame(data, columns=["Trend", "ATS Record", "Cover %", "MOV", "ATS +/-"])
    
    # Save to CSV
    team_name_lower = "chicago-bulls"
    csv_filename = os.path.join(BASE_DIR, team_name_lower, "chicago-bulls_ats_trends.csv")
    os.makedirs(os.path.dirname(csv_filename), exist_ok=True)
    df.to_csv(csv_filename, index=False)
    print(f"CSV file saved: {csv_filename}")
    
    # Save to Excel
    excel_filename = os.path.join(BASE_DIR, team_name_lower, "chicago-bulls_ats_trends.xlsx")
    df.to_excel(excel_filename, index=False)
    print(f"Excel file saved: {excel_filename}")
    
    # Print formatted table
    print(f"\nATS Trends for Chicago Bulls")
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
    print(bottom_border)  # Should be bottom_border
    
    return df

if __name__ == "__main__":
    fetch_and_save_chicago_bulls_ats_trends()
