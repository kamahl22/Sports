import requests
import csv
import os
from bs4 import BeautifulSoup

player_id = "4397227"
player_name = "Vince Williams Jr."

def fetch_and_save_data():
    url = f"https://www.espn.com/nba/player/splits/_/id/{player_id}/{player_name.lower().replace(' ', '-')}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    if response.status_code != 200:
        print(f"Error: Unable to fetch data for {player_name} (ID: {player_id}) - Status Code {response.status_code}")
        return None, None
    
    soup = BeautifulSoup(response.text, "html.parser")
    tables = soup.find_all("table")
    print(f"Number of tables found: {len(tables)}")
    
    if not tables:
        print(f"No stats tables found for {player_name}. The page structure may have changed.")
        return None, None
    
    expected_headers = ["SPLIT", "GP", "MIN", "FG", "FG%", "3PT", "3P%", "FT", "FT%", "OR", "DR", "REB", "AST", "BLK", "STL", "PF", "TO", "PTS"]
    
    preset_splits = [
        "All Splits", "Home", "Road", "vs. Division", "vs. Conference", "3+ Days Rest",
        "October", "November", "December", "January", "February", "March",
        "Pre All-Star", "Post All-Star", "Wins", "Losses",
        "As Starter", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday",
        "vs ATL", "vs BOS", "vs CHA", "vs CHI", "vs CLE", "vs DAL", "vs DEN", "vs DET", "vs GS", "vs HOU",
        "vs LAC", "vs LAL", "vs MEM", "vs MIA", "vs MIL", "vs NO", "vs NY", "vs ORL", "vs PHI", "vs PHO",
        "vs POR", "vs SA", "vs SAC", "vs OKC", "vs TOR", "vs UTA", "vs WAS"
    ]
    
    default_stats = ["0", "0.0", "0.0-0.0", "0.0", "0.0-0.0", "0.0", "0.0-0.0", "0.0", "0.0", "0.0", "0.0", "0.0", "0.0", "0.0", "0.0", "0.0", "0.0"]
    player_data_dict = {split: default_stats.copy() for split in preset_splits}
    
    all_rows = []
    for table in tables:
        all_rows.extend(table.find_all("tr")[1:])
    
    splits = []
    stats_rows = []
    for i, row in enumerate(all_rows):
        columns = row.find_all("td")
        row_data = [col.text.strip() for col in columns if col.text.strip()]
        if not row_data:
            continue
        if len(row_data) == 1 and row_data[0] in preset_splits:
            splits.append(row_data[0])
            print(f"Split found ({len(splits)-1}): ['{row_data[0]}']")
        elif len(row_data) > 1 and row_data[0].isdigit():
            stats_rows.append(row_data)
            print(f"Stats found ({len(stats_rows)-1}): {row_data}")
        else:
            print(f"Subheader: {row_data}")
        print()
    
    for idx, split in enumerate(splits):
        if idx < len(stats_rows):
            stats = stats_rows[idx][:len(expected_headers)-1] + ["N/A" for _ in range(len(stats_rows[idx]), len(expected_headers)-1)] if len(stats_rows[idx]) < len(expected_headers)-1 else stats_rows[idx][:len(expected_headers)-1]
            player_data_dict[split] = stats
            print(f"Paired: ['{split}'] with {stats}")
            print()
    
    player_data = [[split] + player_data_dict[split] for split in preset_splits]
    
    if not player_data:
        print(f"No player splits data found for {player_name}.")
        return None, None
    
    base_directory = "/Users/kamahl/Sports/scripts/espn/nba/team_roster/test_roster"
    player_folder = os.path.join(base_directory, "memphis-grizzlies", "vince_williams_jr.")
    os.makedirs(player_folder, exist_ok=True)
    
    csv_filename = os.path.join(player_folder, f"{player_name.lower().replace(' ', '_')}_splits.csv")
    with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(expected_headers)
        writer.writerows(player_data)
    
    print(f"CSV file saved: {csv_filename}")
    return expected_headers, player_data

def print_excel_style():
    headers, data = fetch_and_save_data()
    if not headers or not data:
        print("No headers or data to display.")
        return
    
    max_cols = len(headers)
    col_widths = [len(str(h)) for h in headers]
    
    for row in data:
        padded_row = row + [""] * (max_cols - len(row)) if len(row) < max_cols else row[:max_cols]
        for i, cell in enumerate(padded_row):
            col_widths[i] = max(col_widths[i], len(str(cell)))
    
    top_border = "┌" + "─".join("─" * (w + 2) for w in col_widths) + "┐"
    bottom_border = "└" + "─".join("─" * (w + 2) for w in col_widths) + "┘"
    separator = "├" + "─".join("─" * (w + 2) for w in col_widths) + "┤"
    
    print(top_border)
    header_row = "│ " + " │ ".join(h.center(w) for h, w in zip(headers, col_widths)) + " │"
    print(header_row)
    print(separator)
    
    for row in data:
        padded_row = row + [""] * (max_cols - len(row)) if len(row) < max_cols else row[:max_cols]
        data_row = "│ " + " │ ".join(str(cell).ljust(w) for cell, w in zip(padded_row, col_widths)) + " │"
        print(data_row)
    
    print(bottom_border)

if __name__ == "__main__":
    print_excel_style()
