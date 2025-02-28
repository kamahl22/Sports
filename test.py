import requests

# ESPN NBA team roster API endpoint (example: Minnesota Timberwolves team ID = 16)
team_id = 16  # Change this ID for different teams
url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams/{team_id}/roster"

# Make the API request
response = requests.get(url)
data = response.json()

# Extract players from the roster
players = data.get("athletes", [])

# Print organized player information
print(f"NBA Team Roster (Team ID: {team_id})")
print("=" * 40)

for player in players:
    player_id = player.get("id", "N/A")
    full_name = player.get("fullName", "N/A")
    display_name = player.get("displayName", "N/A")
    
    print(f"ID: {player_id}")
    print(f"Full Name: {full_name}")
    print(f"Display Name: {display_name}")
    print("-" * 40)