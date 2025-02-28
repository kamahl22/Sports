import requests
import csv
import os

# Player information
player_id = 5044385
player_name = "Leonard Miller"
url = "https://www.espn.com/nba/player/splits/_/id/{player_id}/{player_name.lower().replace(' ', '-')}"

# Make API request
response = requests.get(url)
if response.status_code != 200:
    print(f"Error: Unable to fetch data for {player_name} (ID: {player_id})")
    exit()

# Placeholder for parsing logic - You'll need BeautifulSoup for full scraping
data = response.text  # This will be replaced with actual parsed data

# Create CSV file inside player folder
player_folder = os.path.join("nba_teams", "timberwolves", "leonard_miller")
csv_filename = os.path.join(player_folder, f"{safe_player_name}_splits.csv")

# Save raw data (Modify this to properly parse and extract stats)
with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Raw HTML Data"])  # Replace with actual headers
    writer.writerow([data])  # Replace with parsed data rows

print(f"CSV file saved: {csv_filename}")