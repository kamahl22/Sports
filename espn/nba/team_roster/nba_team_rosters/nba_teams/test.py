import requests
import csv
import os
from bs4 import BeautifulSoup

# Define player_id and player_name at the start
player_id = 4594268
player_name = "Anthony Edwards"

# Rest of the script using these variables
url = f"https://www.espn.com/nba/player/splits/_/id/{player_id}/{player_name.lower().replace(' ', '-')}"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}
response = requests.get(url, headers=headers)

if response.status_code != 200:
    print(f"Error: Unable to fetch data for {player_name} (ID: {player_id}) - Status Code {response.status_code}")
    exit()

soup = BeautifulSoup(response.text, "html.parser")
tables = soup.find_all("table")

if not tables:
    print(f"No stats tables found for {player_name}. The page structure may have changed.")
    exit()

player_data = []
headers_list = []

for table in tables:
    headers = [header.text.strip() for header in table.find_all("th")]
    rows = table.find_all("tr")[1:]
    if headers:
        headers_list.append(headers)
    for row in rows:
        columns = row.find_all("td")
        row_data = [col.text.strip() for col in columns]
        if row_data:
            player_data.append(row_data)

# Updated base directory to match your desired path
base_directory = "/Users/kamahl/Sports/scripts/espn/nba/team_roster/nba_team_rosters/nba_teams"
player_folder = os.path.join(base_directory, "timberwolves", player_name.lower().replace(' ', '_'))
os.makedirs(player_folder, exist_ok=True)

csv_filename = os.path.join(player_folder, f"{player_name.lower().replace(' ', '_')}_splits.csv")

with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    if headers_list:
        writer.writerow(headers_list[0])
    writer.writerows(player_data)

print(f"CSV file saved: {csv_filename}")