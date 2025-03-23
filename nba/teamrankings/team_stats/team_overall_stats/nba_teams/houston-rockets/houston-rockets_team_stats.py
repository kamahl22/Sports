import requests
from bs4 import BeautifulSoup
import csv
import os
import pandas as pd

# Base directory for saving files
BASE_DIR = "/Users/kamahl/Sports/scripts/nba/teamrankings/team_stats/team_overall_stats/nba_teams"
os.makedirs(BASE_DIR, exist_ok=True)

def fetch_and_save_houston_rockets_stats():
    """Fetch, save, and print the Houston Rockets team statistics from TeamRankings."""
    url = "https://www.teamrankings.com/nba/team/houston-rockets/stats"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    if response.status_code != 200:
        print(f"Error: Unable to fetch stats for Houston Rockets - Status Code {response.status_code}")
        return None
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Find all tables
    tables = soup.find_all("table")
    print(f"Number of tables found: {len(tables)}")
    
    if not tables:
        print("No tables found. Dumping page snippet for debugging:")
        print(soup.prettify()[:2000])
        return None
    
    # Expected categories
    categories = [
        "Overall Statistics",
        "Shooting Statistics",
        "Scoring Statistics",
        "Rebounding Statistics",
        "Blocks Statistics",
        "Steals Statistics",
        "Turnovers Statistics",
        "Fouls Statistics"
    ]
    
    all_stats = {}
    
    # Process tables
    for table in tables:
        section_header = table.find_previous("h2")
        category = section_header.text.strip() if section_header else "Unknown"
        print(f"Processing table category: {category}")
        
        if category in categories:
            stats = []
            rows = table.find_all("tr")
            for row in rows:
                cols = row.find_all("td")
                if len(cols) >= 4:
                    stat_name = cols[0].text.strip() if cols[0].text.strip() else "Unnamed Stat"
                    offense_value = cols[1].text.strip()
                    defense_stat_name = cols[2].text.strip() if len(cols) > 2 and cols[2].text.strip() else "Opp " + stat_name
                    defense_value = cols[3].text.strip()
                    stats.append((stat_name, offense_value, defense_stat_name, defense_value))
            all_stats[category] = stats
    
    # Save to CSV and Excel
    team_name_lower = "houston-rockets"
    csv_filename = os.path.join(BASE_DIR, team_name_lower, "houston-rockets_stats.csv")
    excel_filename = os.path.join(BASE_DIR, team_name_lower, "houston-rockets_stats.xlsx")
    
    # Prepare data for saving
    headers = ["Category", "MIN Offense", "Value (rank)", "MIN Defense", "Value (rank)"]
    all_rows = []
    for category, stats_list in all_stats.items():
        for stat in stats_list:
            all_rows.append([category, stat[0], stat[1], stat[2], stat[3]])
    
    # Save to CSV
    os.makedirs(os.path.dirname(csv_filename), exist_ok=True)
    with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(all_rows)
    print(f"CSV file saved: {csv_filename}")
    
    # Save to Excel
    os.makedirs(os.path.dirname(excel_filename), exist_ok=True)
    df = pd.DataFrame(all_rows, columns=headers)
    df.to_excel(excel_filename, index=False)
    print(f"Excel file saved: {excel_filename}")
    
    # Print stats in an Excel-like format
    for category, stats_list in all_stats.items():
        print(f"\n{category}")
        if not stats_list:
            print("No stats found for this category.")
            continue
        
        col_widths = [max(len(str(item)) for item in [stat[0] for stat in stats_list] + ["MIN Offense"]),
                      max(len(str(item)) for item in [stat[1] for stat in stats_list] + ["Value (rank)"]),
                      max(len(str(item)) for item in [stat[2] for stat in stats_list] + ["MIN Defense"]),
                      max(len(str(item)) for item in [stat[3] for stat in stats_list] + ["Value (rank)"])]
        
        top_border = "┌" + "─".join("─" * (w + 2) for w in col_widths) + "┐"
        bottom_border = "└" + "─".join("─" * (w + 2) for w in col_widths) + "┘"
        separator = "├" + "─".join("─" * (w + 2) for w in col_widths) + "┤"
        
        header_row = "│ " + " │ ".join(h.center(w) for h, w in zip(["MIN Offense", "Value (rank)", "MIN Defense", "Value (rank)"], col_widths)) + " │"
        print(top_border)
        print(header_row)
        print(separator)
        
        for stat_name, offense_value, defense_stat_name, defense_value in stats_list:
            row = "│ " + " │ ".join(str(item).ljust(w) for item, w in zip([stat_name, offense_value, defense_stat_name, defense_value], col_widths)) + " │"
            print(row)
        
        print(bottom_border)
    
    return all_stats

if __name__ == "__main__":
    stats = fetch_and_save_houston_rockets_stats()
