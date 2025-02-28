import requests
import csv
import os

# ESPN NBA team roster API endpoint
team_id = 3
url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams/{team_id}/roster"

# Make the API request
response = requests.get(url)
data = response.json()

# Extract team information
team_info = data.get("team", {})
team_name = team_info.get("name", "N/A")
team_display_name = team_info.get("displayName", "N/A")
team_abbreviation = team_info.get("abbreviation", "N/A")

# Extract players from the roster
players = data.get("athletes", [])

# Print team details
print(f"NBA Team: {team_display_name} ({team_abbreviation})")
print("=" * 40)

# Create a list for CSV output
csv_data = [("ID", "Full Name", "Display Name")]

for player in players:
    player_id = player.get("id", "N/A")
    full_name = player.get("fullName", "N/A")
    display_name = player.get("displayName", "N/A")
    
    print(f"ID: {player_id}")
    print(f"Full Name: {full_name}")
    print(f"Display Name: {display_name}")
    print("-" * 40)
    
    csv_data.append((player_id, full_name, display_name))

# Create team folder if it doesn't exist
team_folder = os.path.join("nba_teams", "pelicans")
os.makedirs(team_folder, exist_ok=True)

# Save data to a CSV file inside the team folder
csv_filename = os.path.join(team_folder, f"{team_name.lower().replace(' ', '_')}_roster.csv")

with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerows(csv_data)

print(f"CSV file saved: {csv_filename}")