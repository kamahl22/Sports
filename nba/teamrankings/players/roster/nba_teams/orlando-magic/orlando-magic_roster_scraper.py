import pandas as pd
import os
from playwright.sync_api import sync_playwright

# Base directory for saving files
BASE_DIR = "/Users/kamahl/Sports/scripts/nba/teamrankings/players/roster/nba_teams/orlando-magic"
os.makedirs(BASE_DIR, exist_ok=True)

def fetch_and_save_orlando_magic_roster():
    """Fetch and save the Orlando Magic roster from TeamRankings."""
    url = "https://www.teamrankings.com/nba/team/orlando-magic/roster"
    
    print(f"Fetching roster for Orlando Magic from {url}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        })
        page.goto(url)
        
        page.wait_for_selector('table.tr-table', timeout=10000)
        page.wait_for_timeout(2000)  # Ensure JS rendering
        
        tables = page.query_selector_all('table.tr-table')
        print(f"Number of tables found: {len(tables)}")
        
        if not tables:
            print("No tables found.")
            data = [["No Tables Found"] + ["N/A"] * 8]
        else:
            data = []
            for table in tables:
                rows = table.query_selector_all('tr')
                print(f"Number of rows in table: {len(rows)}")
                
                for i, row in enumerate(rows[1:]):  # Skip header
                    cols = row.query_selector_all('td')
                    print(f"Row {i} has {len(cols)} columns")
                    if len(cols) >= 9:
                        row_data = [col.inner_text().strip() for col in cols[:9]]
                        print(f"Row {i} data: {row_data}")
                        data.append(row_data)
                    else:
                        print(f"Row {i} skipped: insufficient columns ({len(cols)})")
            
            if not data:
                print("No data extracted from tables.")
                data = [["No Data Available"] + ["N/A"] * 8]
        
        browser.close()
    
    # Create DataFrame
    df = pd.DataFrame(data, columns=["Player Name", "Position", "Games Played", "Minutes Played", 
                                     "Points", "Rebounds", "Assists", "Steals", "Blocks"])
    
    # Save to CSV
    csv_filename = os.path.join(BASE_DIR, "orlando-magic_roster.csv")
    df.to_csv(csv_filename, index=False)
    print(f"CSV file saved: {csv_filename}")
    
    # Save to Excel
    excel_filename = os.path.join(BASE_DIR, "orlando-magic_roster.xlsx")
    df.to_excel(excel_filename, index=False)
    print(f"Excel file saved: {excel_filename}")
    
    # Print formatted table to terminal
    print(f"\nRoster for Orlando Magic")
    col_widths = [max(len(str(row[i])) for row in data + [df.columns]) for i in range(9)]
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
    fetch_and_save_orlando_magic_roster()