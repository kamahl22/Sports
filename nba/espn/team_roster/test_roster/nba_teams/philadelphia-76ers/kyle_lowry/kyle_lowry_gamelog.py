import requests
import csv
import os
from bs4 import BeautifulSoup

# Player-specific variables
player_id = "3012"
player_name = "Kyle Lowry"
team = "philadelphia-76ers"

def fetch_and_save_gamelog():
    """Fetch and save the player's game log for the 2024-25 season."""
    url = f"https://www.espn.com/nba/player/gamelog/_/id/{player_id}/{player_name.lower().replace(' ', '-')}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    if response.status_code != 200:
        print(f"Error: Unable to fetch game log for {player_name} (ID: {player_id}) - Status Code {response.status_code}")
        return None, None
    
    soup = BeautifulSoup(response.text, "html.parser")
    tables = soup.find_all("table", class_="Table")
    
    print(f"Number of tables found: {len(tables)}")
    if not tables:
        print(f"No game log tables found for {player_name}. Dumping page snippet for debugging:")
        print(soup.prettify()[:1000])
        return None, None
    
    # Expected headers for the game log
    expected_headers = ["DATE", "OPP", "RESULT", "MIN", "FG", "FG%", "3PT", "3P%", "FT", "FT%", "REB", "AST", "BLK", "STL", "PF", "TO", "PTS"]
    
    game_data = []
    
    for table in tables:
        # Check for season title (for debugging)
        prev_sibling = table.find_previous_sibling("div", class_="Table__Title")
        season_label = prev_sibling.text.strip() if prev_sibling else "Unknown"
        print(f"Processing table with title: '{season_label}'")
        
        rows = table.find_all("tr")[1:]  # Skip header row
        print(f"Number of rows in table: {len(rows)}")
        
        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 2:
                print(f"Skipping row with insufficient columns: {[col.text.strip() for col in cols]}")
                continue
            
            # Extract game details
            date = cols[0].text.strip()
            # Skip if it's a month summary row (e.g., "march")
            if not any(day in date.lower() for day in ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]):
                print(f"Skipping summary row: {date}")
                continue
            
            opponent = cols[1].text.strip()
            result = cols[2].text.strip()
            stats = [col.text.strip() for col in cols[3:]]
            
            print(f"Raw row data: {[date, opponent, result] + stats}")
            
            # Ensure stats match expected length, padding with "N/A" if needed
            if len(stats) < len(expected_headers) - 3:  # Subtract DATE, OPP, RESULT
                stats.extend(["N/A"] * (len(expected_headers) - 3 - len(stats)))
            game_row = [date, opponent, result] + stats[:14]  # Cap at expected stats
            game_data.append(game_row)
    
    if not game_data:
        print(f"No game log data found for {player_name} in the 2024-25 season.")
        return None, None
    
    print(f"Collected {len(game_data)} games for {player_name}")
    
    # Save to CSV
    base_dir = "/Users/kamahl/Sports/scripts/espn/nba/team_roster/test_roster"
    player_folder = os.path.join(base_dir, "philadelphia-76ers", "kyle_lowry")
    os.makedirs(player_folder, exist_ok=True)
    csv_filename = os.path.join(player_folder, "kyle_lowry_gamelog.csv")
    
    with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(expected_headers)
        writer.writerows(game_data)
    
    print(f"CSV file saved: {csv_filename}")
    return expected_headers, game_data

def print_excel_style():
    """Print the game log in an Excel-like table format."""
    headers, data = fetch_and_save_gamelog()
    if not headers or not data:
        print("No headers or data to display.")
        return
    
    # Calculate column widths
    col_widths = [len(str(h)) for h in headers]
    for row in data:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))
    
    # Build table elements
    top_border = "┌" + "─".join("─" * (w + 2) for w in col_widths) + "┐"
    bottom_border = "└" + "─".join("─" * (w + 2) for w in col_widths) + "┘"
    separator = "├" + "─".join("─" * (w + 2) for w in col_widths) + "┤"
    
    # Print table
    print(top_border)
    header_row = "│ " + " │ ".join(h.center(w) for h, w in zip(headers, col_widths)) + " │"
    print(header_row)
    print(separator)
    
    for row in data:
        data_row = "│ " + " │ ".join(str(cell).ljust(w) for cell, w in zip(row, col_widths)) + " │"
        print(data_row)
    
    print(bottom_border)  # Should be bottom_border, kept for consistency

if __name__ == "__main__":
    print_excel_style()
