import pandas as pd
import re
import os
from playwright.sync_api import sync_playwright

# Base directory for saving files
BASE_DIR = "/Users/kamahl/Sports/scripts/nba/teamrankings/players/player_stats/nba_teams/houston-rockets/jaesean-tate"
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
    print(f"Raw cell text: {cell_text}")
    
    # Match value and rank with a more robust regex
    # This regex matches a value (which can include numbers, decimals, or percentages) followed by an optional rank in parentheses
    match = re.match(r"^(.*?)\s*(?:\((#[0-9]+)\))?$", cell_text)
    if match:
        value = match.group(1).strip() if match.group(1) else "N/A"
        rank = match.group(2) if match.group(2) else "N/A"
        print(f"Split result: Value={value}, Rank={rank}")
        return value, rank
    print(f"No match for cell text, returning as-is: {cell_text}")
    return cell_text, "N/A"

def print_table(title, data, columns):
    """Print a formatted table to the terminal."""
    if not data:
        print(f"\n{title}: No data available.")
        return
    
    print(f"\n{title}")
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

def fetch_and_save_jaesean_tate_stats():
    """Fetch and save stats for Jae'Sean Tate from TeamRankings."""
    player_name = "Jae'Sean Tate"
    formatted_name = "jaesean-tate"
    url = f"https://www.teamrankings.com/nba/player/{formatted_name}/stats"
    
    print(f"Fetching stats for {player_name} from {url}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        })
        page.goto(url)
        
        try:
            page.wait_for_selector('table', timeout=30000)
            page.wait_for_timeout(2000)
            tables = page.query_selector_all('table')
        except Exception as e:
            print(f"Failed to find any tables: {e}. Page may not exist.")
            tables = []
        
        print(f"Number of tables found: {len(tables)}")
        
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
                print(f"Number of rows in Basic Stat Highlights table: {len(rows)}")
                
                if len(rows) >= 4:  # Expect header + 3 rows (Season Totals, Per Minute, Per Game)
                    headers = [col.inner_text().strip() for col in rows[0].query_selector_all('th')]
                    print(f"Basic Stat Headers: {headers}")
                    
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
                                stat_name = f"{row_name} {headers[j - start_col]}"
                                cell_text = cols[j].inner_text().strip()
                                value, rank = split_value_and_rank(cell_text)
                                basic_data.append([stat_name, value, rank])
                        else:
                            print(f"Row {i} in Basic Stat Highlights has {len(cols)} columns, expected {len(headers) + start_col}")
                            basic_data.append(["Parse Error", "Column mismatch", "N/A"])
                else:
                    basic_data.append(["No Data Available", "N/A", "N/A"])
            
            # Process "Player Ranking Summary" table
            ranking_table_found = False
            for table_idx, table in enumerate(tables[1:], 1):
                rows = table.query_selector_all('tr')
                print(f"Number of rows in table {table_idx + 1}: {len(rows)}")
                
                if len(rows) < 2:
                    continue
                
                headers = [col.inner_text().strip() for col in rows[0].query_selector_all('th')]
                print(f"Table {table_idx + 1} Headers: {headers}")
                
                # Check if this is the "Player Ranking Summary" table
                if "Season Totals" in headers and "Per Minute" in headers and "Per Game" in headers:
                    ranking_table_found = True
                    for i, row in enumerate(rows[1:], 1):  # Skip header
                        cols = row.query_selector_all('td')
                        raw_cols = [col.inner_text().strip() for col in cols]
                        print(f"Row {i} in table {table_idx + 1} has {len(cols)} columns: {raw_cols}")
                        if len(cols) >= 7:  # Expect 7 columns: Stat, Season Totals value, Season Totals rank, Per Minute value, Per Minute rank, Per Game value, Per Game rank
                            stat_name = raw_cols[0]  # e.g., "Points"
                            # Process each pair of columns (value and rank) for Season Totals, Per Minute, Per Game
                            for j in range(1, 6, 2):  # Step by 2 to process pairs: (1,2) for Season Totals, (3,4) for Per Minute, (5,6) for Per Game
                                if j + 1 < len(raw_cols):  # Ensure both value and rank columns exist
                                    # Map the column index to the header
                                    header_idx = (j - 1) // 2 + 1  # Maps j=1 to "Season Totals", j=3 to "Per Minute", j=5 to "Per Game"
                                    category = f"{stat_name} {headers[header_idx]}"
                                    # Combine the value and rank into a single string
                                    value_text = raw_cols[j]
                                    rank_text = raw_cols[j + 1] if raw_cols[j + 1] else ""
                                    combined_text = f"{value_text} {rank_text}".strip()
                                    value, rank = split_value_and_rank(combined_text)
                                    print(f"Appending for {category}: Value={value}, Rank={rank}")
                                    ranking_data.append([category, value, rank])
                                else:
                                    print(f"Missing data for {stat_name} {headers[(j-1)//2 + 1]} in row {i}")
                                    ranking_data.append([f"{stat_name} {headers[(j-1)//2 + 1]}", "N/A", "N/A"])
                        else:
                            print(f"Row {i} in table {table_idx + 1} has {len(cols)} columns, expected at least 7")
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
    basic_csv_filename = os.path.join(BASE_DIR, "jaesean-tate_basic_stats.csv")
    basic_df.to_csv(basic_csv_filename, index=False)
    print(f"Basic Stats CSV file saved: {basic_csv_filename}")
    
    basic_excel_filename = os.path.join(BASE_DIR, "jaesean-tate_basic_stats.xlsx")
    basic_df.to_excel(basic_excel_filename, index=False)
    print(f"Basic Stats Excel file saved: {basic_excel_filename}")
    
    # Save Player Ranking Summary to CSV and Excel
    ranking_csv_filename = os.path.join(BASE_DIR, "jaesean-tate_ranking_stats.csv")
    ranking_df.to_csv(ranking_csv_filename, index=False)
    print(f"Ranking Stats CSV file saved: {ranking_csv_filename}")
    
    ranking_excel_filename = os.path.join(BASE_DIR, "jaesean-tate_ranking_stats.xlsx")
    ranking_df.to_excel(ranking_excel_filename, index=False)
    print(f"Ranking Stats Excel file saved: {ranking_excel_filename}")
    
    # Print both tables to terminal
    print_table(f"Basic Stat Highlights for {player_name}", basic_data, ["Stat Category", "Value", "Qualified Rank"])
    print_table(f"Player Ranking Summary for {player_name}", ranking_data, ["Stat Category", "Value", "Qualified Rank"])
    
    return basic_df, ranking_df

if __name__ == "__main__":
    fetch_and_save_jaesean_tate_stats()